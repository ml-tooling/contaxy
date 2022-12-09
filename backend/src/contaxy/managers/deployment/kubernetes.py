import os
import time
from datetime import datetime, timezone
from typing import Any, List, Literal, Optional

from kubernetes import client as kube_client
from kubernetes import config as kube_config
from kubernetes.client.models import (
    V1Deployment,
    V1DeploymentList,
    V1Job,
    V1JobList,
    V1JobSpec,
    V1ServiceList,
)
from kubernetes.client.rest import ApiException
from loguru import logger

from contaxy.config import settings
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
from contaxy.managers.deployment.utils import (
    DEFAULT_DEPLOYMENT_ACTION_ID,
    NO_LOGS_MESSAGE,
    Labels,
)
from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentType, ServiceUpdate
from contaxy.schema.exceptions import ResourceNotFoundError, ServerBaseError


class KubernetesDeploymentPlatform:
    def __init__(
        self,
        kube_namespace: Optional[str] = None,
    ):
        """Initializes the Kubernetes Deployment Manager.

        Args:
            kube_namespace (str): Set the Kubernetes namespace to use. If it is not given, the manager will try to detect the namespace automatically.
        """

        try:
            # incluster config is the config given by a service account and it's role permissions
            kube_config.load_incluster_config()
        except kube_config.ConfigException:
            kube_config.load_kube_config(context=os.getenv("CTXY_K8S_CONTEXT", None))

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
            except FileNotFoundError as e:
                # TODO: fix arguments
                raise ServerBaseError(
                    "Could not detect the Kubernetes Namespace"
                ) from e
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
        service: Service,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Service:

        kube_service_config = build_kube_service_config(
            service=service,
            project_id=project_id,
            kube_namespace=self.kube_namespace,
        )
        kube_deployment_config, kube_deployment_pvc = build_kube_deployment_config(
            service=service,
            project_id=project_id,
            kube_namespace=self.kube_namespace,
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
                    self.apps_api.delete_namespaced_deployment(
                        namespace=self.kube_namespace, name=service.id
                    )
                except ApiException:
                    pass
                try:
                    self.core_api.delete_namespaced_service(
                        namespace=self.kube_namespace, name=service.id
                    )
                except ApiException:
                    pass

                # TODO: delete pvc here

            raise ServerBaseError(
                f"Could not create namespaced deployment '{service.display_name}'"
            ) from e

        try:
            transformed_service = map_kube_service(deployment)
        except Exception as e:
            # Delete already created resources upon an error
            try:
                self.core_api.delete_namespaced_service(
                    namespace=self.kube_namespace, name=service.id
                )
            except ApiException:
                pass

            try:
                self.apps_api.delete_namespaced_deployment(
                    namespace=self.kube_namespace, name=service.id
                )
            except ApiException:
                pass

            # TODO: delete pvc here

            raise ServerBaseError(
                f"Could not transform deployment '{service.display_name}' with reason: {e}"
            ) from e

        return transformed_service

    def update_service(
        self, project_id: str, service_id: str, service: ServiceUpdate
    ) -> Service:
        # Service update is only implemented on DeploymentManagerWithDB wrapper
        raise NotImplementedError()

    def update_service_access(self, project_id: str, service_id: str) -> None:
        # Service update is only implemented on DeploymentManagerWithDB wrapper
        raise NotImplementedError()

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
        except ApiException as e:
            raise ResourceNotFoundError(
                f"Could not get metadata of service '{service_id}' for project {project_id}."
            ) from e

    def delete_service(
        self,
        project_id: str,
        service_id: str,
        delete_volumes: bool = False,
        retries: int = 0,
    ) -> None:

        try:
            self.core_api.delete_namespaced_service(
                name=service_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
        except ApiException as e:
            if e.reason != "NotFound":
                raise ServerBaseError(
                    f"Could not delete Kubernetes service for service-id {service_id}."
                ) from e

        try:
            self.apps_api.delete_namespaced_deployment(
                name=service_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
        except ApiException as e:
            if e.reason != "NotFound":
                raise ServerBaseError(
                    f"Could not delete Kubernetes deployment for service-id {service_id}."
                )
        if delete_volumes:
            try:
                # TODO: if we work with a queue system, then add it to a deletion queue
                self.core_api.delete_namespaced_persistent_volume_claim(
                    namespace=self.kube_namespace, name=service_id
                )
            except ApiException as e:
                if e.reason != "NotFound":
                    raise ServerBaseError(
                        f"Could not delete Kubernetes Persistent Volume Claim for service-id {service_id}."
                    )
        try:
            # wait some time for the deployment to be deleted
            wait_for_deletion(
                self.apps_api, self.kube_namespace, deployment_id=service_id
            )
        except ApiException as e:
            # TODO: add resources to delete to a queue instead of deleting directly? This would have the advantage that even if an operation failes, it is repeated. Also, if the delete endpoint is called multiple times, it is only added once to the queue
            raise ServerBaseError(
                f"Error while waiting for deletion of service '{service_id}'.",
            ) from e

    def delete_services(
        self,
        project_id: str,
    ) -> None:
        label_selector = get_deployment_selection_labels(
            project_id=project_id, deployment_type=DeploymentType.SERVICE
        )

        # TODO: Replace with self.core_api.delete_collection_namespaced_service once added to the kubernetes python client
        try:
            services: V1ServiceList = self.core_api.list_namespaced_service(
                namespace=self.kube_namespace, label_selector=label_selector
            )
            for service in services.items:
                try:
                    self.core_api.delete_namespaced_service(
                        name=service.metadata.name, namespace=self.kube_namespace
                    )
                except ApiException as e:
                    logger.error(
                        f"Could not delete Kubernetes service {service.metadata.name}: {e}"
                    )
        except ApiException as e:
            logger.error(
                f"Could not list Kubernetes services for deletion in project {project_id}: {e}"
            )

        try:
            self.apps_api.delete_collection_namespaced_deployment(
                namespace=self.kube_namespace,
                label_selector=label_selector,
                propagation_policy="Foreground",
            )
        except ApiException as e:
            logger.error(
                f"Could not delete Kubernetes deployments for project '{project_id}':\n{e}"
            )

        try:
            self.core_api.delete_collection_namespaced_persistent_volume_claim(
                namespace=self.kube_namespace,
                label_selector=label_selector,
                propagation_policy="Foreground",
            )
        except ApiException as e:
            logger.error(
                f"Could not delete Kubernetes deployments for project '{project_id}':\n{e}"
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
            except ApiException as e:
                raise ServerBaseError(
                    f"Could not read logs of service {service_id}."
                ) from e
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
        job: Job,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Job:
        metadata = build_deployment_metadata(
            kube_namespace=self.kube_namespace,
            project_id=project_id,
            deployment=job,
        )

        # For debugging purposes, set restart_policy=Never to have access to job logs (see https://kubernetes.io/docs/concepts/workloads/controllers/job/#pod-backoff-failure-policy)
        pod_spec = build_pod_template_spec(
            deployment=job,
            metadata=metadata,
        )
        pod_spec.spec.restart_policy = "OnFailure"

        _job = V1Job(metadata=metadata, spec=V1JobSpec(template=pod_spec))
        try:
            deployed_job = self.batch_api.create_namespaced_job(
                namespace=self.kube_namespace, body=_job
            )
        except ApiException as e:
            raise ServerBaseError(f"Could not deploy job '{job.display_name}'.") from e

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
        except ApiException as e:
            raise ResourceNotFoundError(
                f"Could not get metadata of job '{job_id}'."
            ) from e

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
            raise ServerBaseError(
                f"Could not delete job '{job_id}'.",
            ) from e

    def delete_jobs(
        self,
        project_id: str,
    ) -> None:
        label_selector = get_deployment_selection_labels(
            project_id=project_id, deployment_type=DeploymentType.JOB
        )

        try:
            self.batch_api.delete_collection_namespaced_job(
                namespace=self.kube_namespace,
                label_selector=label_selector,
                propagation_policy="Foreground",
            )
        except ApiException as e:
            raise ServerBaseError(
                f"Could not delete Kubernetes jobs for project '{project_id}'"
            ) from e

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

    def suggest_service_config(
        self, project_id: str, container_image: str
    ) -> ServiceInput:
        raise NotImplementedError()

    def list_service_actions(
        self, project_id: str, service_id: str
    ) -> List[ResourceAction]:
        raise NotImplementedError()

    def execute_service_action(
        self, project_id: str, service_id: str, action_id: str
    ) -> Any:
        raise NotImplementedError()

    def suggest_job_config(self, project_id: str, container_image: str) -> JobInput:
        raise NotImplementedError()

    def list_job_actions(self, project_id: str, job_id: str) -> List[ResourceAction]:
        raise NotImplementedError()

    def execute_job_action(self, project_id: str, job_id: str, action_id: str) -> Any:
        raise NotImplementedError()
