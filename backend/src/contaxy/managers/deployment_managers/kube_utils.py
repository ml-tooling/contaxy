from typing import Any, Dict, List, Tuple, Union

from kubernetes.client.models import V1Deployment, V1Job

from ... import data_model
from .utils import Labels, get_label_string


def get_label_selector(label_pairs: List[Tuple[str, str]]) -> str:
    """Bring label tuples into the form required by the Kubernetes client, e.g. 'key1=value1,key2=value2,key3=value3)'"""
    return ",".join([get_label_string(pair[0], pair[1]) for pair in label_pairs])


# TODO: name sth. "map_from_x_to_y"
def transform_deployment(deployment: Union[V1Deployment, V1Job]) -> Dict[str, Any]:
    # We assume a 1:1 mapping between deployment/pod & containers
    container = deployment.spec.template.spec.containers[0]
    labels = deployment.metadata.labels

    resources = container.resources
    compute_resources = data_model.DeploymentCompute(
        min_cpus=resources.requests["cpu"],  # / 1e9,
        max_cpus=resources.limits["cpu"],  # / 1e9,
        min_memory=resources.requests["memory"].replace("M", ""),  # / 1000 / 1000,
        max_memory=resources.limits["memory"].replace("M", ""),  # / 1000 / 1000,
        max_gpus=None,  # TODO: fill with sensible information - where to get it from?
        min_lifetime=labels.get(Labels.MIN_LIFETIME.value),
        volume_Path=labels.get(Labels.VOLUME_PATH.value),
        # TODO: add max_volume_size, max_replicas
    )

    try:
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
            status = data_model.DeploymentStatus.RUNNING.value
        else:
            status = data_model.DeploymentStatus.PENDING.value
    except ValueError:
        status = data_model.DeploymentStatus.UNKNOWN.value

    started_at = deployment.metadata.creation_timestamp
    # stopped_at only relevant for Jobs
    stopped_at = (
        deployment.status.completion_time
        if hasattr(deployment.status, "completion_time")
        else 0
    )

    parameters = {env.name: env.value for env in container.env}

    return {
        "container_image": container.image,
        # In kubernetes, command is an array
        "command": container.command[0]
        if container.command is not None and len(container.command) > 0
        else "",
        "compute": compute_resources,
        "deployment_labels": labels,
        "deployment_type": labels.get(Labels.DEPLOYMENT_TYPE.value),
        "description": labels.get(Labels.DESCRIPTION.value),
        # TODO: replicase __ logic => use annotations instead of labels for all metadata that we don't use for filtering
        "display_name": labels.get(Labels.DISPLAY_NAME.value).replace("__", " "),
        "endpoints": labels.get(Labels.ENDPOINTS.value),
        # TODO: exit_code can only be queried on pod-level, but what if there are multiple replicas?
        # "exit_code": container.attrs.get("State", {}).get("ExitCode", -1),
        "icon": labels.get(Labels.ICON.value),
        "id": deployment.metadata.name,
        "internal_id": deployment.metadata.name,
        "parameters": parameters,
        "started_at": started_at,
        "status": status,
        "stopped_at": stopped_at,
    }


def transform_kube_service(deployment: V1Deployment,) -> data_model.Service:
    transformed_deployment = transform_deployment(deployment=deployment)
    return data_model.Service(**transformed_deployment)


def transform_kube_job(job: V1Job) -> data_model.Job:
    transformed_job = transform_deployment(deployment=job)
    # TODO: add status SUCCESSFUL or FAILED
    return data_model.Job(**transformed_job)
