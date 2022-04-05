import string
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from kubernetes import client as kube_client
from kubernetes.client.models import (
    V1Container,
    V1Deployment,
    V1DeploymentSpec,
    V1EnvVar,
    V1Job,
    V1LabelSelector,
    V1NetworkPolicy,
    V1NetworkPolicyIngressRule,
    V1NetworkPolicyPeer,
    V1NetworkPolicySpec,
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
    V1Volume,
    V1VolumeMount,
)
from kubernetes.client.rest import ApiException

from contaxy.config import settings
from contaxy.managers.deployment.utils import (
    _MIN_MEMORY_DEFAULT_MB,
    Labels,
    get_label_string,
    get_project_selection_labels,
    map_labels,
    map_list_to_string,
)
from contaxy.schema import Job, Service
from contaxy.schema.deployment import (
    Deployment,
    DeploymentCompute,
    DeploymentStatus,
    DeploymentType,
)
from contaxy.schema.exceptions import ResourceNotFoundError, ServerBaseError
from contaxy.utils.utils import remove_none_values_from_dict


def get_label_selector(label_pairs: List[Tuple[str, str]]) -> str:
    """Bring label tuples into the form required by the Kubernetes client, e.g. 'key1=value1,key2=value2,key3=value3)'."""
    return ",".join([get_label_string(pair[0], pair[1]) for pair in label_pairs])


def get_deployment_selection_labels(
    project_id: str, deployment_type: DeploymentType = DeploymentType.SERVICE
) -> str:
    """Return selector identifying project services/jobs in the form Kubernetes expects a label selector.

    Args:
        project_id (str): The project id of the resources to select.
        deployment_type (DeploymentType, optional): The deployment type by which the selected resources are filtered. Defaults to DeploymentType.SERVICE.

    Returns:
        str: Kubernetes label string in the form of 'key1=value1,key2=value2,key3=value3,...'
    """
    return get_label_selector(
        get_project_selection_labels(
            project_id=project_id, deployment_type=deployment_type
        )
    )


# TODO: Return list of pods? As there can be multiple pods belonging to the same job / deployment (e.g. which were created / failed but do not run anymore)
def get_pod(
    project_id: str,
    service_id: str,
    kube_namespace: str,
    core_api: kube_client.CoreV1Api,
) -> Optional[V1Pod]:
    """Get the pod filtered by the project id and service id labels in the given Kubernetes namespace.

    Args:
        service_id (str): If deployed via Contaxy, corresponds to the deployment id of the pod.
        kube_namespace (str): The Kubernetes namespaces in which to look for the pod.
        core_api (kube_client.CoreV1Api): Initialized Kubernetes CoreV1Api object.

    Raises:
        ResourceNotFoundError: Raised when no pod matches the selection criteria.

    Returns:
        Optional[V1Pod]: Returns the pod matching the selection criteria. In case of replicas, multiple pods can match the criteria; in this case, the first pod is selected arbitrarily.
    """
    label_selector = get_label_selector(
        [
            (Labels.NAMESPACE.value, settings.SYSTEM_NAMESPACE),
            (Labels.PROJECT_NAME.value, project_id),
            (Labels.DEPLOYMENT_ID.value, service_id),
        ]
    )

    pods: V1PodList = core_api.list_namespaced_pod(
        namespace=kube_namespace, label_selector=label_selector
    )

    if len(pods.items) == 0:
        raise ResourceNotFoundError(
            f"No pod with label-selector {label_selector} found"
        )

    return pods.items[0]


def create_pvc(
    pvc: Optional[V1PersistentVolumeClaim],
    kube_namespace: str,
    core_api: kube_client.CoreV1Api,
) -> None:
    if pvc is None:
        return

    try:
        core_api.create_namespaced_persistent_volume_claim(
            namespace=kube_namespace, body=pvc
        )
    except ApiException as e:
        # 409 means that the pvc was not created but already exists and can be used
        if e.status != 409:
            raise ServerBaseError(
                f"Could not create persistent volume claim for service '{pvc.metadata.name}' with reason: {e}"
            ) from e


def create_service(
    service_config: Optional[V1Service],
    kube_namespace: str,
    core_api: kube_client.CoreV1Api,
) -> None:
    if service_config is None:
        return

    try:
        core_api.create_namespaced_service(
            namespace=kube_namespace, body=service_config
        )
    except ApiException as e:
        raise ServerBaseError(
            f"Could not create namespaced service '{service_config.metadata.name}' with reason: {e}"
        ) from e


def build_kube_service_config(
    service: Service, project_id: str, kube_namespace: str
) -> V1Service:
    # TODO: set the endpoints as annotations
    service_ports: Dict[str, V1ServicePort] = {}
    if service.endpoints:
        for endpoint in service.endpoints:

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
            namespace=kube_namespace,
            name=service.id,
            labels={
                # Labels.DISPLAY_NAME.value: service.display_name,# display_name cannot be a label since whitespaces are not allowed in label values. Kubernetes validation regex: (([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?')
                Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                Labels.PROJECT_NAME.value: project_id,
                Labels.DEPLOYMENT_ID.value: service.id,
                Labels.DEPLOYMENT_TYPE.value: service.deployment_type,
            },  # service.labels
        ),
        spec=V1ServiceSpec(
            selector={
                Labels.DEPLOYMENT_ID.value: service.id,
                Labels.PROJECT_NAME.value: project_id,
                Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                Labels.DEPLOYMENT_TYPE.value: service.deployment_type,
            },
            # ports must be set and it must contain at least one port
            ports=list(service_ports.values())
            if len(service_ports.values()) > 0
            else [V1ServicePort(name="default", protocol="TCP", port=80)],
            type="ClusterIP",
        ),
    )


def build_pod_template_spec(
    deployment: Deployment,
    metadata: V1ObjectMeta,
) -> V1PodTemplateSpec:
    compute_resources = deployment.compute
    # TODO: check default values and store them globally probably!
    min_cpus = compute_resources.min_cpus or 0
    max_cpus = compute_resources.max_cpus or 1
    min_memory = compute_resources.min_memory or _MIN_MEMORY_DEFAULT_MB
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

    # the name is used by Kubernetes to match the container-volume and the pod-volume section
    mount_name = f"mount-{deployment.id}"
    volume_mounts, volumes = None, None
    if compute_resources.volume_path:
        volume_mounts = [
            V1VolumeMount(
                name=mount_name, mount_path=str(compute_resources.volume_path)
            )
        ]
        volumes = [
            V1Volume(
                name=mount_name,
                persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
                    claim_name=deployment.id
                ),
            )
        ]
    container = V1Container(
        name=deployment.id,
        image=deployment.container_image,
        image_pull_policy="IfNotPresent",
        resources=resource_requirements,
        command=deployment.command,
        args=deployment.args,
        env=[
            V1EnvVar(name=name, value=value)
            for name, value in deployment.parameters.items()
        ],
        volume_mounts=volume_mounts,
    )
    pod_spec = V1PodSpec(
        volumes=volumes,
        containers=[container],
    )

    return V1PodTemplateSpec(metadata=metadata, spec=pod_spec)


def build_deployment_metadata(
    kube_namespace: str,
    project_id: str,
    deployment: Deployment,
) -> V1ObjectMeta:
    return V1ObjectMeta(
        namespace=kube_namespace,
        name=deployment.id,
        labels={
            Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
            Labels.PROJECT_NAME.value: project_id,
            Labels.DEPLOYMENT_ID.value: deployment.id,
            Labels.DEPLOYMENT_TYPE.value: deployment.deployment_type.value,
        },
        annotations={
            **deployment.metadata,
            Labels.DISPLAY_NAME.value: deployment.display_name,
            Labels.DEPLOYMENT_TYPE.value: deployment.deployment_type.value,
            Labels.DESCRIPTION.value: deployment.description,
            Labels.ENDPOINTS.value: map_list_to_string(deployment.endpoints),
            Labels.REQUIREMENTS.value: map_list_to_string(deployment.requirements),
            Labels.ICON.value: deployment.icon,
            Labels.MIN_LIFETIME.value: str(deployment.compute.min_lifetime),
            Labels.CREATED_BY.value: deployment.created_by,
            Labels.VOLUME_PATH.value: deployment.compute.volume_path,
        },
    )


def build_kube_deployment_config(
    service: Service,
    project_id: str,
    kube_namespace: str,
) -> Tuple[V1Deployment, Union[V1PersistentVolumeClaim, None]]:
    compute_resources = service.compute

    metadata = build_deployment_metadata(
        kube_namespace=kube_namespace,
        project_id=project_id,
        deployment=service,
    )

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
                storage_class_name="default",
                resources=V1ResourceRequirements(requests={"storage": storage_size}),
                access_modes=["ReadWriteOnce"],
            ),
        )

    # TODO: adding of ServiceAccountName needed?

    # --

    deployment = V1Deployment(
        metadata=metadata,
        spec=V1DeploymentSpec(
            # TODO: the max_replicas name does not make so much sense. Probably just replicas?
            replicas=compute_resources.max_replicas
            if compute_resources.max_replicas
            else 1,
            selector=V1LabelSelector(
                match_labels={
                    Labels.DEPLOYMENT_ID.value: service.id,
                    Labels.PROJECT_NAME.value: project_id,
                    Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                    Labels.DEPLOYMENT_TYPE.value: service.deployment_type.value,
                }
            ),
            template=build_pod_template_spec(
                deployment=service,
                metadata=metadata,
            ),
            # TODO: Make min ready seconds configurable? (see https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#min-ready-seconds)
            min_ready_seconds=5,
        ),
    )

    return deployment, pvc


def build_project_network_policy_spec(
    project_id: str, kube_namespace: str
) -> V1NetworkPolicy:
    project_pod_selector = V1LabelSelector(
        match_labels={
            Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
            Labels.PROJECT_NAME.value: project_id,
        }
    )

    network_policy = V1NetworkPolicy(
        metadata=V1ObjectMeta(
            namespace=kube_namespace,
            name=project_id,
            labels={
                Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                Labels.PROJECT_NAME.value: project_id,
            },
        ),
        spec=V1NetworkPolicySpec(
            ingress=[
                V1NetworkPolicyIngressRule(
                    # Allow traffic from other pods of the same project and the Contaxy backend container
                    _from=[
                        V1NetworkPolicyPeer(pod_selector=project_pod_selector),
                        # TODO: probably not needed as this rule is added via our core kube-network-policy
                        V1NetworkPolicyPeer(
                            pod_selector=V1LabelSelector(
                                match_labels={
                                    Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                                    Labels.DEPLOYMENT_TYPE.value: f"{DeploymentType.CORE_BACKEND.value}",
                                }
                            )
                        ),
                    ]
                )
            ],
            pod_selector=project_pod_selector,
        ),
    )

    return network_policy


def check_or_create_project_network_policy(
    network_policy: V1NetworkPolicy, networking_api: kube_client.NetworkingV1Api
) -> V1NetworkPolicy:
    try:
        return networking_api.read_namespaced_network_policy(
            namespace=network_policy.metadata.namespace,
            name=network_policy.metadata.name,
        )
    except ApiException:
        return networking_api.create_namespaced_network_policy(
            namespace=network_policy.metadata.namespace, body=network_policy
        )


def wait_for_deployment(
    deployment_name: str,
    kube_namespace: str,
    apps_api: kube_client.AppsV1Api,
    timeout: int = 180,
) -> None:
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(5)
        response = apps_api.read_namespaced_deployment_status(
            namespace=kube_namespace, name=deployment_name
        )
        s = response.status
        # TODO: Check status of pod created by deployment. Is it crashing? Or is it pulling an image?
        if (
            s.updated_replicas == response.spec.replicas
            and s.replicas == response.spec.replicas
            and s.available_replicas == response.spec.replicas
            and s.observed_generation >= response.metadata.generation
        ):
            return
        else:
            # print(
            #     f"[updated_replicas:{s.updated_replicas},replicas:{s.replicas}"
            #     ",available_replicas:{s.available_replicas},observed_generation:{s.observed_generation}] waiting..."
            # )
            pass

    raise ServerBaseError(f"Waiting timeout for deployment {deployment_name}")


def wait_for_job(
    job_name: str,
    kube_namespace: str,
    batch_api: kube_client.BatchV1Api,
    timeout: int = 60,
) -> None:
    start = time.time()
    while time.time() - start < timeout:
        response = batch_api.read_namespaced_job_status(
            namespace=kube_namespace, name=job_name
        )
        s = response.status
        if (s.active and s.active > 0) or (s.succeeded and s.succeeded > 0):
            return

    raise RuntimeError(f"Waiting timeout for job {job_name}")


def wait_for_deletion(
    api: Union[kube_client.AppsV1Api, kube_client.BatchV1Api],
    kube_namespace: str,
    deployment_id: str,
) -> None:
    start = time.time()
    timeout = 60
    while time.time() - start < timeout:
        try:
            if type(api) == kube_client.AppsV1Api:
                api.read_namespaced_deployment_status(
                    namespace=kube_namespace, name=deployment_id
                )
            elif type(api) == kube_client.BatchV1Api:
                api.read_namespaced_job(name=deployment_id, namespace=kube_namespace)
            time.sleep(2)
        except ApiException:
            # Deployment is deleted
            break


def map_deployment(deployment: Union[V1Deployment, V1Job]) -> Dict[str, Any]:
    # We assume a 1:1 mapping between deployment/pod & containers
    container = deployment.spec.template.spec.containers[0]
    mapped_labels = map_labels(
        {**deployment.metadata.labels, **deployment.metadata.annotations}
    )

    resources = container.resources
    compute_resources = DeploymentCompute(
        min_cpus=int(resources.requests["cpu"].strip(string.ascii_letters)),  # / 1e9,
        max_cpus=int(resources.limits["cpu"].strip(string.ascii_letters)),  # / 1e9,
        min_memory=int(
            resources.requests["memory"].strip(string.ascii_letters)
        ),  # / 1000 / 1000,
        max_memory=int(
            resources.limits["memory"].strip(string.ascii_letters)
        ),  # / 1000 / 1000,
        max_gpus=None,  # TODO: fill with sensible information - where to get it from?
        min_lifetime=mapped_labels.min_lifetime or 0,
        volume_path=mapped_labels.volume_path,
        # TODO: add max_volume_size, max_replicas
    )

    try:
        if deployment.metadata.deletion_timestamp is not None:
            status = DeploymentStatus.TERMINATING.value
        else:
            # TODO: detect failed?
            # TODO: return RUNNING when at least MIN_REPLICAS is fulfilled
            # TODO: if no replica is started, return FAILED
            # TODO: if READY_REPLICAS < MIN_REPLICAS => check exit code of POD
            # TODO: set failed when creation_timestamp is high but still unavailable
            successful = (
                deployment.status.ready_replicas == deployment.status.replicas
                if hasattr(deployment.status, "ready_replicas")
                else deployment.status.succeeded
            )
            if successful:
                status = DeploymentStatus.RUNNING.value
            else:
                status = DeploymentStatus.PENDING.value
    except ValueError:
        status = DeploymentStatus.UNKNOWN.value

    started_at = deployment.metadata.creation_timestamp
    # stopped_at only relevant for Jobs
    stopped_at = (
        deployment.status.completion_time
        if hasattr(deployment.status, "completion_time")
        else 0
    )

    parameters = {}
    for env in container.env:
        parameters[env.name] = env.value if env.value else ""

    return {
        "container_image": container.image,
        "command": container.command,
        "args": container.args,
        "metadata": mapped_labels.metadata,
        "compute": compute_resources,
        "deployment_type": mapped_labels.deployment_type,
        "description": mapped_labels.description,
        # TODO: replicase __ logic => use annotations instead of labels for all metadata that we don't use for filtering
        "display_name": mapped_labels.display_name.replace("__", " ")
        if mapped_labels.display_name
        else "",
        "endpoints": mapped_labels.endpoints,
        # TODO: exit_code can only be queried on pod-level, but what if there are multiple replicas?
        # "exit_code": container.attrs.get("State", {}).get("ExitCode", -1),
        "icon": mapped_labels.icon,
        "id": deployment.metadata.name,
        "internal_id": f"{deployment.metadata.name}-{deployment.metadata.uid}",
        "parameters": parameters,
        "started_at": started_at,
        "status": status,
        "stopped_at": stopped_at,
    }


def map_kube_service(
    deployment: V1Deployment,
) -> Service:
    transformed_deployment = map_deployment(deployment=deployment)
    transformed_deployment = remove_none_values_from_dict(transformed_deployment)
    return Service(**transformed_deployment)


def map_kube_job(job: V1Job) -> Job:
    transformed_job = map_deployment(deployment=job)
    transformed_job = remove_none_values_from_dict(transformed_job)
    # TODO: add status SUCCESSFUL or FAILED
    return Job(**transformed_job)
