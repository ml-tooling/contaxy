import shlex
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Union

from kubernetes import client as kube_client
from kubernetes import config as kube_config
from kubernetes.client.models import (
    V1Container,
    V1Deployment,
    V1DeploymentList,
    V1DeploymentSpec,
    V1EnvVar,
    V1Job,
    V1JobList,
    V1JobSpec,
    V1LabelSelector,
    V1ObjectMeta,
    V1PersistentVolumeClaim,
    V1PersistentVolumeClaimSpec,
    V1PersistentVolumeClaimVolumeSource,
    V1Pod,
    V1PodList,
    V1PodSpec,
    V1PodTemplateSpec,
    V1ResourceRequirements,
    V1Service,
    V1ServicePort,
    V1ServiceSpec,
    V1Status,
    V1Volume,
    V1VolumeMount,
)
from kubernetes.client.rest import ApiException

from ... import data_model
from .deployment_manager import JobDeploymentManager, ServiceDeploymentManager
from .kube_utils import get_label_selector, transform_kube_job, transform_kube_service
from .utils import (
    NAMESPACE,
    DeploymentError,
    EntityNotFoundError,
    Labels,
    log,
    normalize_service_name,
)

max_retries = 3


class KubernetesDeploymentManager(ServiceDeploymentManager, JobDeploymentManager):
    def __init__(self, kube_namespace: str = None):
        try:
            # incluster config is the config given by a service account and it's role permissions
            kube_config.load_incluster_config()
        except kube_config.ConfigException:
            kube_config.load_kube_config()

        self.core_api = kube_client.CoreV1Api()
        self.apps_api = kube_client.AppsV1Api()
        self.batch_api = kube_client.BatchV1Api()

        if kube_namespace is None:
            try:
                # at this path the namespace the container is in is stored in Kubernetes deployment (see https://stackoverflow.com/questions/31557932/how-to-get-the-namespace-from-inside-a-pod-in-openshift)
                with open(
                    "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
                ) as namespace_file:
                    self.kube_namespace = namespace_file.read()
            except FileNotFoundError:
                raise Exception("Could not detect the Kubernetes Namespace")
        else:
            self.kube_namespace = kube_namespace
        # TODO: when we have performance problems in the future, replicate the watch logic from JupyterHub KubeSpawner to keep Pod & other resource information in memory? (see https://github.com/jupyterhub/kubespawner/blob/941585f0f7acb0f366c9979b6274b7f47356a630/kubespawner/reflector.py#L238)

    # Return list of pods? As there can be multiple pods belonging to the same job / deployment (e.g. which were created / failed but do not run anymore)
    def get_pod(self, service_id: str) -> Optional[V1Pod]:
        label_selector = get_label_selector(
            [
                (Labels.NAMESPACE.value, NAMESPACE),
                (Labels.DEPLOYMENT_NAME.value, service_id),
            ]
        )

        pods: V1PodList = self.core_api.list_namespaced_pod(
            namespace=self.kube_namespace, label_selector=label_selector
        )

        if len(pods.items) == 0:
            raise EntityNotFoundError(
                f"No pod with label-selector {label_selector} found"
            )
        # TODO: this error will make problems for replicas
        #         elif len(pods.items) > 1:
        #             # TODO: also check for status (if more than 1 that are running)
        #             raise TooManyEntitiesFoundError(f"Too many pods found with label-selector {label_selector} found")

        return pods.items[0]

    def list_services(self, project_id: str) -> Any:
        label_selector = get_label_selector(
            [
                (Labels.NAMESPACE.value, NAMESPACE),
                (Labels.PROJECT_NAME.value, project_id),
                (Labels.DEPLOYMENT_TYPE.value, data_model.DeploymentType.SERVICE.value),
            ]
        )

        #         services = self.client.list_namespaced_service(
        #             namespace=self.kube_namespace,
        #             label_selector=label_selector
        #         )

        deployments: V1DeploymentList = self.apps_api.list_namespaced_deployment(
            namespace=self.kube_namespace, label_selector=label_selector
        )

        #         deployments_by_name = {x.metadata.name:x for x in deployments}

        #         return [transform_kube_service(service, deployments_by_name[service.metadata.name]) for service in services]
        return [transform_kube_service(deployment) for deployment in deployments.items]

    def get_service_metadata(self, service_id: str) -> Any:
        try:
            deployment: V1Deployment = self.apps_api.read_namespaced_deployment(
                name=service_id, namespace=self.kube_namespace
            )
            return transform_kube_service(deployment)
        except ApiException:
            return None

    def build_kube_service_config(
        self, service_id: str, service: data_model.ServiceInput, project_id: str
    ) -> kube_client.models.V1Service:

        # TODO: set the endpoints as annotations
        service_ports: Dict[str, V1ServicePort] = {}
        if service.endpoints:
            for endpoint in service.endpoints:

                # TODO: put this logic into utils and share with the DockerDeploymentManager
                # An endpoint can be in the form of one of the examples ["8080", "9001/webapp/ui", "9002b"]. See the Contaxy endpoint docs <LINK> for more information.
                port_number = endpoint.split("/")[0].replace("b", "")

                # Kubernetes throws an error when the same port is defined for the same service
                if port_number in service_ports:
                    continue

                service_port = V1ServicePort(
                    name=port_number, protocol="TCP", port=int(port_number)
                )
                service_ports[port_number] = service_port

        return V1Service(
            metadata=V1ObjectMeta(
                namespace=self.kube_namespace,
                name=service_id,
                labels={
                    # Labels.DISPLAY_NAME.value: service.display_name,# display_name cannot be a label since whitespaces are not allowed in label values. Kubernetes validation regex: (([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?')
                    Labels.NAMESPACE.value: NAMESPACE,
                    Labels.PROJECT_NAME.value: project_id,
                    Labels.DEPLOYMENT_NAME.value: service_id,
                },  # service.labels
            ),
            spec=V1ServiceSpec(
                selector={
                    Labels.DEPLOYMENT_NAME.value: service_id,
                    Labels.PROJECT_NAME.value: project_id,
                    Labels.NAMESPACE.value: NAMESPACE,
                    Labels.DEPLOYMENT_TYPE.value: data_model.DeploymentType.SERVICE.value,
                },
                # ports must be set and it must contain at least one port
                ports=list(service_ports.values())
                if len(service_ports.values()) > 0
                else [V1ServicePort(name="default", protocol="TCP", port=80)],
                type="ClusterIP",
            ),
        )

    def build_pod_template_spec(
        self,
        service_id: str,
        service: Union[data_model.ServiceInput, data_model.JobInput],
        metadata: V1ObjectMeta,
    ) -> V1PodTemplateSpec:
        compute_resources = service.compute or data_model.DeploymentCompute()
        # TODO: check default values and store them globally probably!
        min_cpus = compute_resources.min_cpus or 0
        max_cpus = compute_resources.max_cpus or 1
        min_memory = compute_resources.min_memory or 5
        max_memory = compute_resources.max_memory or 100
        max_container_size = compute_resources.max_container_size or 100
        resource_requirements = V1ResourceRequirements(
            limits={
                # e.g. 8000m = 8000 micro-cores = 8 cores (https://cloud.google.com/blog/products/gcp/kubernetes-best-practices-resource-requests-and-limits)
                "cpu": f"{max_cpus * 1000}m",
                "memory": f"{max_memory}M",
                "ephemeral-storage": f"{max_container_size}M",
            },
            requests={
                "cpu": f"{min_cpus * 1000}m",
                "memory": f"{min_memory}M",
                "ephemeral-storage": "0M",
            },
        )

        environment = service.parameters or {}
        # The user MUST not be able to manually set (which) GPUs to use
        if "NVIDIA_VISIBLE_DEVICES" in environment:
            del environment["NVIDIA_VISIBLE_DEVICES"]
        if compute_resources.max_gpus is not None and compute_resources.max_gpus > 0:
            environment["NVIDIA_VISIBLE_DEVICES"] = str(compute_resources.max_gpus)

        # the name is used by Kubernetes to match the container-volume and the pod-volume section
        mount_name = f"mount-{service_id}"
        container = V1Container(
            name=service_id,
            image=service.container_image,
            image_pull_policy="IfNotPresent",
            resources=resource_requirements,
            # In Kubernetes, `command` must be an array and `shlex` helps to split the string like the shell would
            command=shlex.split(service.command) if service.command else None,
            env=[
                V1EnvVar(name=name, value=value) for name, value in environment.items()
            ],
            volume_mounts=[
                V1VolumeMount(
                    name=mount_name, mount_path=str(compute_resources.volume_path)
                )
            ]
            if compute_resources.volume_path
            else None,
        )

        pod_spec = V1PodSpec(
            volumes=[
                V1Volume(
                    name=mount_name,
                    persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
                        claim_name=service_id
                    ),
                )
            ]
            if compute_resources.volume_path
            else None,
            containers=[container],
        )

        return V1PodTemplateSpec(metadata=metadata, spec=pod_spec)

    def build_kube_deployment_config(
        self, service_id: str, service: data_model.ServiceInput, project_id: str
    ) -> Tuple[V1Deployment, Union[V1PersistentVolumeClaim, None]]:
        compute_resources = service.compute or data_model.DeploymentCompute()
        # ---
        min_lifetime = compute_resources.min_lifetime or 0
        additional_metadata = service.additional_metadata or {}
        metadata = V1ObjectMeta(
            namespace=self.kube_namespace,
            name=service_id,
            labels={
                # TODO: use Annotation for DISPLAY_NAME, MIN_LIFETIME, ...
                Labels.DISPLAY_NAME.value: service.display_name.replace(
                    " ", "__"
                ),  # Kubernetes validation regex for labels: (([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?')
                Labels.NAMESPACE.value: NAMESPACE,
                Labels.MIN_LIFETIME.value: str(min_lifetime),
                Labels.PROJECT_NAME.value: project_id,
                Labels.DEPLOYMENT_NAME.value: service_id,
                Labels.DEPLOYMENT_TYPE.value: data_model.DeploymentType.SERVICE.value,
                **additional_metadata,
            },
        )

        # ---

        pvc = None
        # add mount - handle PVC; ignore Secret, Bind and NFS for now
        if compute_resources.volume_path:
            # TODO: change the default storage size
            default_storage_size = "100M"
            storage_size = (
                f"{compute_resources.max_volume_size}M"
                if compute_resources.max_volume_size is not None
                and compute_resources.max_volume_size > 0
                else default_storage_size
            )
            pvc = V1PersistentVolumeClaim(
                metadata=metadata,
                spec=V1PersistentVolumeClaimSpec(
                    # TODO: make the storage class name configurable?
                    storage_class_name="standard",
                    resources=V1ResourceRequirements(
                        requests={"storage": storage_size}
                    ),
                    access_modes=["ReadWriteOnce"],
                ),
            )

        # TODO: adding of ServiceAccountName needed?

        # --

        # TODO: set `.spec.minReadySeconds` option (see https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#min-ready-seconds)
        deployment = V1Deployment(
            metadata=metadata,
            spec=V1DeploymentSpec(
                # TODO: the max_replicas name does not make so much sense. Probably just replicas?
                replicas=compute_resources.max_replicas
                if compute_resources.max_replicas
                else 1,
                selector=V1LabelSelector(
                    match_labels={
                        Labels.DEPLOYMENT_NAME.value: service_id,
                        Labels.PROJECT_NAME.value: project_id,
                        Labels.NAMESPACE.value: NAMESPACE,
                        Labels.DEPLOYMENT_TYPE.value: data_model.DeploymentType.SERVICE.value,
                    }
                ),
                template=self.build_pod_template_spec(
                    service_id=service_id, service=service, metadata=metadata
                ),
            ),
        )

        return deployment, pvc

    def create_pvc(self, pvc: Optional[V1PersistentVolumeClaim]):
        if pvc is None:
            return

        try:
            self.core_api.create_namespaced_persistent_volume_claim(
                namespace=self.kube_namespace, body=pvc
            )
        except ApiException as e:
            # 409 means that the pvc was not created but already exists and can be used
            if e.status != 409:
                raise DeploymentError(
                    f"Could not create persistent volume claim for service '{pvc.metadata.name}' with reason: {e}"
                )

    def create_service(self, service_config: Optional[kube_client.models.V1Service]):
        if service_config is None:
            return

        try:
            self.core_api.create_namespaced_service(
                namespace=self.kube_namespace, body=service_config
            )
        except ApiException as e:
            raise DeploymentError(
                f"Could not create namespaced service '{service_config.metadata.name}' with reason: {e}"
            )

    def create_deployment(self, deployment_config):
        if deployment_config is None:
            return

    def deploy_service(self, service: data_model.ServiceInput, project_id: str) -> Any:
        normalized_service_name = normalize_service_name(
            project_id=project_id, display_name=service.display_name
        )

        kube_service_config = self.build_kube_service_config(
            service_id=normalized_service_name, service=service, project_id=project_id
        )
        kube_deployment_config, kube_deployment_pvc = self.build_kube_deployment_config(
            service_id=normalized_service_name, service=service, project_id=project_id
        )

        self.create_pvc(pvc=kube_deployment_pvc)
        self.create_service(service_config=kube_service_config)

        try:
            deployment: V1Deployment = self.apps_api.create_namespaced_deployment(
                namespace=self.kube_namespace, body=kube_deployment_config
            )
        except (ApiException, Exception) as e:
            # Delete service again as the belonging deployment could not be created, but only when status code is not 409 as 409 indicates that the deployment already exists
            if hasattr(e, "status") and e.status != 409:  # type: ignore
                try:
                    self.core_api.delete_namespaced_service(
                        namespace=self.kube_namespace, name=normalized_service_name
                    )
                except ApiException:
                    pass

            raise DeploymentError(
                f"Could not create namespaced deployment '{service.display_name}' with reason: {e}"
            )

        try:
            transformed_service = transform_kube_service(deployment)
        except Exception as e:
            # Delete already created resources upon an error
            try:
                self.core_api.delete_namespaced_service(
                    namespace=self.kube_namespace, name=normalized_service_name
                )
            except ApiException:
                pass

            try:
                self.apps_api.delete_namespaced_deployment(
                    namespace=self.kube_namespace, name=normalized_service_name
                )
            except ApiException:
                pass

            raise DeploymentError(
                f"Could not transform deployment '{service.display_name}' with reason: {e}"
            )

        return transformed_service

    def delete_service(
        self, service_id: str, delete_volumes: Optional[bool] = False, retries: int = 0
    ) -> Any:

        try:
            status: V1Status = self.core_api.delete_namespaced_service(
                name=service_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
            if status.status == "Failure":
                raise DeploymentError(
                    f"Could not delete Kubernetes service for service-id {service_id}"
                )

            status = self.apps_api.delete_namespaced_deployment(
                name=service_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
            if status.status == "Failure":
                log(
                    f"Could not delete Kubernetes deployment for service-id {service_id}"
                )
                return False
                # raise Exception(f"Could not delete Kubernetes deployment for service-id {service_id}")

            if delete_volumes:
                status = self.core_api.delete_namespaced_persistent_volume_claim(
                    namespace=self.kube_namespace, name=service_id
                )
                if status.status == "Failure":
                    # TODO: if we work with a queue system, then add it to a deletion queue
                    log(
                        f"Could not delete Kubernetes Persistent Volume Claim for service-id {service_id}"
                    )
                    return False

            # TODO: raise exception instead of return?
            return True
        except Exception as e:
            log(e.__repr__())
            # TODO: add resources to delete to a queue instead of deleting directly? This would have the advantage that even if an operation failes, it is repeated. Also, if the delete endpoint is called multiple times, it is only added once to the queue
            if retries < max_retries:
                return self.delete_service(service_id=service_id, retries=retries + 1)
            return False

    def get_service_logs(
        self,
        service_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> Any:
        no_logs_message = "No logs available"
        try:
            pod = self.get_pod(service_id=service_id)
        except Exception as e:
            log(e.__repr__())
            return no_logs_message

        if pod is None:
            return no_logs_message

        return self.core_api.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=self.kube_namespace,
            pretty="true",
            tail_lines=lines if lines else None,
            since_seconds=(int((datetime.now() - since).total_seconds()) + 1)
            if since is not None
            else None,
        )

    def cleanup(self):
        raise NotImplementedError

    def list_jobs(self, project_id: str) -> Any:
        label_selector = get_label_selector(
            [
                (Labels.NAMESPACE.value, NAMESPACE),
                (Labels.PROJECT_NAME.value, project_id),
                (Labels.DEPLOYMENT_TYPE.value, data_model.DeploymentType.JOB.value),
            ]
        )

        jobs: V1JobList = self.batch_api.list_namespaced_job(
            namespace=self.kube_namespace, label_selector=label_selector
        )

        return [transform_kube_job(job) for job in jobs.items]

    def get_job_metadata(self, job_id: str):
        try:
            job: V1Job = self.batch_api.read_namespaced_job(
                name=job_id, namespace=self.kube_namespace
            )
            return transform_kube_service(job)
        except ApiException:
            return None

    def list_job_deploy_actions(self, job_input: data_model.JobInput) -> Any:
        raise NotImplementedError

    def deploy_job(self, job: data_model.JobInput, project_id: str) -> Any:
        normalized_service_name = normalize_service_name(
            project_id=project_id, display_name=job.display_name
        )
        metadata = V1ObjectMeta(
            namespace=self.kube_namespace,
            name=normalized_service_name,
            labels={
                Labels.DISPLAY_NAME.value: job.display_name.replace(
                    " ", "__"
                ),  # Kubernetes validation regex for labels: (([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?')
                Labels.NAMESPACE.value: NAMESPACE,
                Labels.PROJECT_NAME.value: project_id,
                Labels.DEPLOYMENT_NAME.value: normalized_service_name,
                Labels.DEPLOYMENT_TYPE.value: data_model.DeploymentType.JOB.value,
            },  # service.deployment_labels
        )

        # For debugging purposes, set restart_policy=Never to have access to job logs (see https://kubernetes.io/docs/concepts/workloads/controllers/job/#pod-backoff-failure-policy)
        pod_spec = self.build_pod_template_spec(
            service_id=normalized_service_name, service=job, metadata=metadata
        )
        pod_spec.spec.restart_policy = "OnFailure"

        _job = V1Job(metadata=metadata, spec=V1JobSpec(template=pod_spec))
        job = self.batch_api.create_namespaced_job(
            namespace=self.kube_namespace, body=_job
        )
        return transform_kube_job(job=job)

    def delete_job(self, job_id: str) -> Any:
        try:
            self.batch_api.delete_namespaced_job(
                name=job_id,
                namespace=self.kube_namespace,
                propagation_policy="Foreground",
            )
        except ApiException as e:
            log(f"Could not delete job '{job_id}' with reason: {e}")
            return False
        return True

    def get_job_logs(
        self, job_id: str, lines: Optional[int] = None, since: Optional[datetime] = None
    ) -> Any:
        return self.get_service_logs(service_id=job_id, lines=lines, since=since)
