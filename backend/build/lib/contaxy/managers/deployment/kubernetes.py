import time
from datetime import datetime, timezone
from typing import List, Literal, Optional

from kubernetes import client as kube_client
from kubernetes import config as kube_config
from kubernetes.client.models import (
    V1Deployment,
    V1DeploymentList,
    V1Job,
    V1JobList,
    V1JobSpec,
    V1ServiceList,
    V1Status,
)
from kubernetes.client.rest import ApiException
from loguru import logger

from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.managers.deployment.kube_utils import (
    build_deployment_metadata,
    build_kube_deployment_config,
    build_kube_service_config,
    build_pod_template_spec,
    build_project_network_policy_spec,
    check_or_create_project_network_policy,
    create_pvc,
    create_service,
    get_deployment_selection_labels,
    get_label_selector,
    get_pod,
    map_kube_job,
    map_kube_service,
    wait_for_deletion,
    wait_for_deployment,
    wait_for_job,
)
from contaxy.managers.deployment.manager import DeploymentManager
from contaxy.managers.deployment.utils import (
    DEFAULT_DEPLOYMENT_ACTION_ID,
    NO_LOGS_MESSAGE,
    Labels,
    get_deployment_id,
    split_image_name_and_tag,
)
from contaxy.managers.system import SystemManager
from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentType
from contaxy.schema.exceptions import (
    ClientBaseError,
    ClientValueError,
    ResourceNotFoundError,
    ServerBaseError,
)
from contaxy.utils.auth_utils import parse_userid_from_resource_name
from contaxy.utils.state_utils import GlobalState, RequestState


class KubernetesDeploymentManager(DeploymentManager):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        system_manager: SystemManager,
        auth_manager: AuthManager,
        kube_namespace: str = None,
    ):
        """Initializes the Kubernetes Deployment Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            system_manager: The system manager used for getting the list of allowed images.
            auth_manager: The auth manager is used to generate api tokens that a passed to services and jobs.
            kube_namespace (str): Set the Kubernetes namespace to use. If it is not given, the manager will try to detect the namespace automatically.
        """
        self.global_state = global_state
        self.request_state = request_state
        self._system_manager = system_manager
        self._auth_manager = auth_manager

        try:
            # incluster config is the config given by a service account and it's role permissions
            kube_config.load_incluster_config()
        except kube_config.ConfigException:
            kube_config.load_kube_config()

        self.core_api = kube_client.CoreV1Api()
        self.apps_api = kube_client.AppsV1Api()
        self.batch_api = kube_client.BatchV1Api()
        self.networking_api = kube_client.NetworkingV1Api()

        if kube_namespace is None:
            try:
                # at this path the namespace the container is in is stored in Kubernetes deployment (see https://stackoverflow.com/questions/31557932/how-to-get-the-namespace-from-inside-a-pod-in-openshift)
                with open(
                    "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
                ) as namespace_file:
                    self.kube_namespace = namespace_file.read()
            except FileNotFoundError:
                # TODO: fix arguments
                raise ServerBaseError("Could not detect the Kubernetes Namespace")
        else:
            self.kube_namespace = kube_namespace
        # TODO: when we have performance problems in the future, replicate the watch logic from JupyterHub KubeSpawner to keep Pod & other resource information in memory? (see https://github.com/jupyterhub/kubespawner/blob/941585f0f7acb0f366c9979b6274b7f47356a630/kubespawner/reflector.py#L238)

    def list_services(
        self,
        project_id: str,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> List[Service]:
        label_selector = get_deployment_selection_labels(
            project_id=project_id, deployment_type=deployment_type
        )

        try:
            deployments: V1DeploymentList = self.apps_api.list_namespaced_deployment(
                namespace=self.kube_namespace, label_selector=label_selector
            )
            return [map_kube_service(deployment) for deployment in deployments.items]
        except ApiException:
            return []

    def deploy_service(
        self,
        project_id: str,
        service: ServiceInput,
        action_id: Optional[str] = None,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
        wait: bool = False,
    ) -> Service:
        image_name, image_tag = split_image_name_and_tag(service.container_image)
        self._system_manager.check_image(image_name, image_tag)
        if service.display_name is None:
            raise ClientValueError(
                message=f"Could not create a service id for service with display name {service.display_name}",
                explanation="A display name for the service must be provided.",
            )

        service_id = get_deployment_id(
            project_id=project_id,
            deployment_name=service.display_name,
            deployment_type=deployment_type,
        )

        kube_service_config = build_kube_service_config(
            service_id=service_id,
            service=service,
            project_id=project_id,
            kube_namespace=self.kube_namespace,
        )
        kube_deployment_config, kube_deployment_pvc = build_kube_deployment_config(
            service_id=service_id,
            service=service,
            project_id=project_id,
            kube_namespace=self.kube_namespace,
            auth_manager=self._auth_manager,
            user_id=parse_userid_from_resource_name(
                self.request_state.authorized_subject
            ),
        )

        check_or_create_project_network_policy(
            network_policy=build_project_network_policy_spec(
                project_id=project_id, kube_namespace=self.kube_namespace
            ),
            networking_api=self.networking_api,
        )

        create_pvc(
            pvc=kube_deployment_pvc,
            kube_namespace=self.kube_namespace,
            core_api=self.core_api,
        )
        create_service(
            service_config=kube_service_config,
            kube_namespace=self.kube_namespace,
            core_api=self.core_api,
        )

        try:
            deployment: V1Deployment = self.apps_api.create_namespaced_deployment(
                namespace=self.kube_namespace, body=kube_deployment_config
            )

            if wait:
                wait_for_deployment(
                    deployment_name=deployment.metadata.name,
                    kube_namespace=self.kube_namespace,
                    apps_api=self.apps_api,
                )

        except (ApiException, Exception) as e:
            # Delete service again as the belonging deployment could not be created, but only when status code is not 409 as 409 indicates that the deployment already exists
            if not hasattr(e, "status") or e.status != 409:  # type: ignore
                try:
                    self.core_api.delete_namespaced_service(
                        namespace=self.kube_namespace, name=service_id
                    )
                except ApiException:
                    pass

                # TODO: delete pvc here

            raise ClientBaseError(
                status_code=500,
                message=f"Could not create namespaced deployment '{service.display_name}' with reason: {e}",
            )

        try:
            transformed_service = map_kube_service(deployment)
        except Exception as e:
            # Delete already created resources upon an error
            try:
                self.core_api.delete_namespaced_service(
                    namespace=self.kube_namespace, name=service_id
                )
            except ApiException:
                pass

            try:
                self.apps_api.delete_namespaced_deployment(
                    namespace=self.kube_namespace, name=service_id
                )
            except ApiException:
                pass

            # TODO: delete pvc here

            raise ServerBaseError(
                f"Could not transform deployment '{service.display_name}' with reason: {e}"
            )

        return transformed_service

    def list_deploy_service_actions(
        self, project_id: str, service: ServiceInput
    ) -> List[ResourceAction]:
        # TODO: make some cluster checks?
        return [
            ResourceAction(
                action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
                display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
            )
        ]

    def get_service_metadata(self, project_id: str, service_id: str) -> Service:
        try:
            deployment: V1Deployment = self.apps_api.read_namespaced_deployment(
                name=service_id, namespace=self.kube_namespace
            )

            # Make sure that the service belongs to the same contaxy namespace as the core-backend. Also, double check that this service really belongs to the project (even though the serviceId should be unique)
            if (
                deployment.metadata.labels[Labels.NAMESPACE.value]
                != settings.SYSTEM_NAMESPACE
                or deployment.metadata.labels[Labels.PROJECT_NAME.value] != project_id
            ):
                raise ResourceNotFoundError(
                    f"Could not get metadata of service '{service_id}' for project {project_id}."
                )

            return map_kube_service(deployment)
        except ApiException:
            raise ResourceNotFoundError(
                f"Could not get metadata of service '{service_id}' for project {project_id}."
            )

    def delete_service(
        self,
        project_id: str,
        service_id: str,
        delete_volumes: bool = False,
        retries: int = 0,
    ) -> None:

        try:
            status: V1Status = self.core_api.delete_namespaced_service(
                name=service_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
            if status.status == "Failure":
                raise ServerBaseError(
                    f"Could not delete Kubernetes service for service-id {service_id}"
                )

            status = self.apps_api.delete_namespaced_deployment(
                name=service_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
            if status.status == "Failure":
                raise ServerBaseError(
                    f"Could not delete Kubernetes deployment for service-id {service_id}"
                )

            if delete_volumes:
                status = self.core_api.delete_namespaced_persistent_volume_claim(
                    namespace=self.kube_namespace, name=service_id
                )
                if status.status == "Failure":
                    # TODO: if we work with a queue system, then add it to a deletion queue
                    # log(
                    #     f"Could not delete Kubernetes Persistent Volume Claim for service-id {service_id}"
                    # )
                    raise ServerBaseError(
                        f"Could not delete Kubernetes Persistent Volume Claim for service-id {service_id}"
                    )

            # wait some time for the deployment to be deleted
            wait_for_deletion(
                self.apps_api, self.kube_namespace, deployment_id=service_id
            )
        except Exception:
            # TODO: add resources to delete to a queue instead of deleting directly? This would have the advantage that even if an operation failes, it is repeated. Also, if the delete endpoint is called multiple times, it is only added once to the queue
            # if retries < max_retries:
            #     try:
            #         return self.delete_service(
            #             project_id=project_id,
            #             service_id=service_id,
            #             delete_volumes=delete_volumes,
            #             retries=retries + 1,
            #         )
            #     except Exception:
            #         pass
            raise ClientBaseError(
                status_code=500,
                message=f"Could not delete service '{service_id}'.",
            )

    def delete_services(
        self,
        project_id: str,
    ) -> None:
        label_selector = get_deployment_selection_labels(
            project_id=project_id, deployment_type=DeploymentType.SERVICE
        )

        try:
            services: V1ServiceList = self.core_api.list_namespaced_service(
                namespace=self.kube_namespace, label_selector=label_selector
            )

            for service in services.items:
                self.core_api.delete_namespaced_service(
                    name=service.metadata.name, namespace=self.kube_namespace
                )

            status = self.apps_api.delete_collection_namespaced_deployment(
                namespace=self.kube_namespace,
                label_selector=label_selector,
                propagation_policy="Foreground",
            )

            if status.status == "Failure":
                raise ServerBaseError(
                    f"Could not delete Kubernetes deployments for project '{project_id}'"
                )

            status = self.core_api.delete_collection_namespaced_persistent_volume_claim(
                namespace=self.kube_namespace,
                label_selector=label_selector,
                propagation_policy="Foreground",
            )

            if status.status == "Failure":
                raise ServerBaseError(
                    f"Could not delete Kubernetes volumes for project '{project_id}'"
                )

        except Exception as e:
            logger.error(f"Error in Kubernetes->delete_services. Reason: {e}")
            raise ClientBaseError(
                500, f"Could not delete services for project '{project_id}'"
            )

    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        try:
            pod = get_pod(
                project_id=project_id,
                service_id=service_id,
                kube_namespace=self.kube_namespace,
                core_api=self.core_api,
            )
        except Exception:
            pod = None

        if pod is None:
            raise ResourceNotFoundError(
                f"Could not find service {service_id} to read logs from."
            )

        # TODO: remove as this should not be a concern of the get_logs function
        try:
            # Give some time to let the container within the pod start
            start = time.time()
            timeout = 60
            while True:
                if pod.status.phase in ["Pending", "ContainerCreating"]:
                    try:
                        pod = get_pod(
                            project_id=project_id,
                            service_id=service_id,
                            kube_namespace=self.kube_namespace,
                            core_api=self.core_api,
                        )
                        time.sleep(1)
                    except Exception:
                        pass
                else:
                    break

                if time.time() - start > timeout:
                    raise ServerBaseError(
                        f"Could not read logs from service {service_id} due to status error."
                    )

            since_seconds = None
            if since:
                since_seconds = (
                    int((datetime.now(timezone.utc) - since).total_seconds()) + 1
                )

            try:
                return self.core_api.read_namespaced_pod_log(
                    name=pod.metadata.name,
                    namespace=self.kube_namespace,
                    pretty="true",
                    tail_lines=lines if lines else None,
                    since_seconds=since_seconds,
                )
            except ApiException:
                raise ServerBaseError(f"Could not read logs of service {service_id}.")
        except Exception:
            return NO_LOGS_MESSAGE

    def list_jobs(self, project_id: str) -> List[Job]:
        label_selector = get_label_selector(
            [
                (Labels.NAMESPACE.value, settings.SYSTEM_NAMESPACE),
                (Labels.PROJECT_NAME.value, project_id),
                (Labels.DEPLOYMENT_TYPE.value, DeploymentType.JOB.value),
            ]
        )

        try:
            jobs: V1JobList = self.batch_api.list_namespaced_job(
                namespace=self.kube_namespace, label_selector=label_selector
            )
        except ApiException:
            return []

        return [map_kube_job(job) for job in jobs.items]

    def deploy_job(
        self,
        project_id: str,
        job: JobInput,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Job:
        image_name, image_tag = split_image_name_and_tag(job.container_image)
        self._system_manager.check_image(image_name, image_tag)
        if job.display_name is None:
            raise ClientValueError(
                message=f"Could not create service id for job {job.display_name}",
                explanation="The display name for a service must be set.",
            )

        deployment_id = get_deployment_id(
            project_id=project_id,
            deployment_name=job.display_name,
            deployment_type=DeploymentType.JOB,
        )
        metadata = build_deployment_metadata(
            kube_namespace=self.kube_namespace,
            project_id=project_id,
            deployment_id=deployment_id,
            display_name=job.display_name.replace(" ", "__"),
            labels=job.metadata,
            compute_resources=job.compute,
            endpoints=job.endpoints,
            deployment_type=DeploymentType.JOB,
            user_id=parse_userid_from_resource_name(
                self.request_state.authorized_subject
            ),
        )

        # For debugging purposes, set restart_policy=Never to have access to job logs (see https://kubernetes.io/docs/concepts/workloads/controllers/job/#pod-backoff-failure-policy)
        pod_spec = build_pod_template_spec(
            project_id=project_id,
            service_id=deployment_id,
            service=job,
            metadata=metadata,
            auth_manager=self._auth_manager,
            user_id=parse_userid_from_resource_name(
                self.request_state.authorized_subject
            ),
        )
        pod_spec.spec.restart_policy = "OnFailure"

        _job = V1Job(metadata=metadata, spec=V1JobSpec(template=pod_spec))
        try:
            deployed_job = self.batch_api.create_namespaced_job(
                namespace=self.kube_namespace, body=_job
            )
        except ApiException:
            raise ClientBaseError(
                status_code=500, message=f"Could not deploy job '{job.display_name}'."
            )

        if wait:
            wait_for_job(
                job_name=deployed_job.metadata.name,
                kube_namespace=self.kube_namespace,
                batch_api=self.batch_api,
            )

        return map_kube_job(job=deployed_job)

    def list_deploy_job_actions(
        self,
        project_id: str,
        job: JobInput,
    ) -> List[ResourceAction]:
        # TODO: make some cluster checks?
        return [
            ResourceAction(
                action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
                display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
            )
        ]

    def get_job_metadata(self, project_id: str, job_id: str) -> Job:
        try:
            job: V1Job = self.batch_api.read_namespaced_job(
                name=job_id, namespace=self.kube_namespace
            )
            return map_kube_job(job)
        except ApiException:
            raise ResourceNotFoundError(f"Could not get metadata of job '{job_id}'.")

    def delete_job(self, project_id: str, job_id: str) -> None:
        try:
            self.batch_api.delete_namespaced_job(
                name=job_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )

            # wait some time for the job to be deleted
            wait_for_deletion(self.batch_api, self.kube_namespace, job_id)
        except ApiException as e:
            raise ClientBaseError(
                status_code=500,
                message=f"Could not delete job '{job_id}' with reason: {e}",
            )

    def delete_jobs(
        self,
        project_id: str,
    ) -> None:
        label_selector = get_deployment_selection_labels(
            project_id=project_id, deployment_type=DeploymentType.JOB
        )

        try:
            status: V1Status = self.batch_api.delete_collection_namespaced_job(
                namespace=self.kube_namespace,
                label_selector=label_selector,
                propagation_policy="Foreground",
            )

            if status.status == "Failure":
                raise ServerBaseError(
                    f"Could not delete Kubernetes jobs for project '{project_id}'"
                )
        except ApiException as e:
            log = f"Could not delete Kubernetes jobs for project '{project_id}'"
            logger.error(f"{log}. Reason: {e}")
            raise ServerBaseError(log)

    def get_job_logs(
        self,
        project_id: str,
        job_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        return self.get_service_logs(
            project_id=project_id, service_id=job_id, lines=lines, since=since
        )
