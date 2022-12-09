import ipaddress
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import docker
import docker.errors
import docker.models.containers
import docker.models.networks
import docker.types
import psutil
from docker import DockerClient
from loguru import logger

from contaxy.config import settings
from contaxy.managers.deployment.utils import (
    _MIN_MEMORY_DEFAULT_MB,
    DEFAULT_DEPLOYMENT_ACTION_ID,
    NO_LOGS_MESSAGE,
    Labels,
    get_gpu_info,
    get_label_string,
    get_network_name,
    get_project_selection_labels,
    get_volume_name,
    map_labels,
    map_list_to_string,
)
from contaxy.schema import ResourceAction
from contaxy.schema.deployment import (
    Deployment,
    DeploymentCompute,
    DeploymentStatus,
    DeploymentType,
    Job,
    JobInput,
    Service,
    ServiceInput,
)
from contaxy.schema.exceptions import ResourceNotFoundError, ServerBaseError

# we create networks in the range of 172.33-255.0.0/24
# Docker by default uses the range 172.17-32.0.0, so we should be save using that range
from contaxy.utils.utils import remove_none_values_from_dict

INITIAL_CIDR_FIRST_OCTET = 10
INITIAL_CIDR_SECOND_OCTET = 0
INITIAL_CIDR = f"{INITIAL_CIDR_FIRST_OCTET}.{INITIAL_CIDR_SECOND_OCTET}.0.0/24"

system_cpu_count = psutil.cpu_count()
system_memory_in_mb = round(psutil.virtual_memory().total / 1024 / 1024, 1)
system_gpu_count = get_gpu_info()


def map_container(
    container: docker.models.containers.Container,
) -> Dict[str, Any]:
    mapped_labels = map_labels(container.labels)

    host_config = container.attrs["HostConfig"]
    compute_resources = DeploymentCompute(
        max_cpus=host_config["NanoCpus"] / 1e9,
        max_memory=host_config["Memory"] / 1000 / 1000,
        max_gpus=None,  # TODO: fill with sensible information - where to get it from?
        min_lifetime=mapped_labels.min_lifetime or 0,
        volume_path=mapped_labels.volume_path,
        # TODO: add max_volume_size, max_replicas
    )

    try:
        container_status = container.status
        if container_status == "created":
            container_status = DeploymentStatus.PENDING.value
        elif container_status == "exited":
            exit_code = container.attrs.get("State", {}).get("ExitCode", 0)
            if exit_code == 0:
                container_status = DeploymentStatus.SUCCEEDED.value
            else:
                container_status = DeploymentStatus.FAILED.value
        status = DeploymentStatus(container_status).value
    except ValueError:
        status = DeploymentStatus.UNKNOWN.value

    started_at = container.attrs.get("State", {}).get("StartedAt", None)
    stopped_at = container.attrs.get("State", {}).get("FinishedAt", None)

    def transform_env_list(envs: list) -> Dict[str, str]:
        transformed_envs = {}
        for env in envs:
            split_env = env.split("=")
            transformed_envs[split_env[0]] = split_env[1] if len(split_env) == 2 else ""
        return transformed_envs

    parameters = transform_env_list(
        container.attrs.get("Config", {}).get("Env", [])
    )  # dict([x for x in [container_env.split("=") for container_env in container_envs]])
    image_tags = container.image.tags
    # Use the first image tag as name. If the image has no tags, use the id.
    if len(image_tags) > 0:
        container_image = image_tags[0]
    else:
        container_image = container.image.short_id

    return {
        "container_image": container_image,
        "command": container.attrs["Config"].get("Entrypoint", []),
        "args": container.attrs["Config"].get("Cmd", []),
        "compute": compute_resources,
        "metadata": mapped_labels.metadata,
        "deployment_type": mapped_labels.deployment_type,
        "description": mapped_labels.description,
        "display_name": mapped_labels.display_name,
        "endpoints": mapped_labels.endpoints,
        #         "exit_code": container.attrs.get("State", {}).get("ExitCode", -1),
        "icon": mapped_labels.icon,
        "id": container.name,
        "internal_id": container.id,
        "parameters": parameters,
        "started_at": started_at,
        "status": status,
        "stopped_at": stopped_at,
    }


def map_service(
    container: docker.models.containers.Container,
) -> Service:
    transformed_container = map_container(container=container)
    transformed_container = remove_none_values_from_dict(transformed_container)

    return Service(**transformed_container)


def map_job(container: docker.models.containers.Container) -> Job:
    transformed_container = map_container(container=container)
    transformed_container = remove_none_values_from_dict(transformed_container)
    return Job(**transformed_container)


# TODO: copied from ML Hub
def create_network(
    client: DockerClient, name: str, labels: Dict[str, str]
) -> docker.models.networks.Network:
    """Create a new network to put the new container into it.

    Containers are separated by networks to prevent them from seeing each other.
    Determine whether a new subnet has to be used. Otherwise, the default Docker subnet would be used
    and, as a result, the amount of networks that can be created is strongly limited.
    We create networks in the range of 172.33-255.0.0/24 whereby Docker by default uses the range 172.17-32.0.0
    See: https://stackoverflow.com/questions/41609998/how-to-increase-maximum-docker-network-on-one-server ; https://loomchild.net/2016/09/04/docker-can-create-only-31-networks-on-a-single-machine/

    Args:
        client (DockerClient): docker client that provides access to the docker API
        name (str): name of the network to be created
        labels (Dict[str, str]): labels that will be attached to the network
    Raises:
        docker.errors.APIError: Thrown by `docker.client.networks.create` upon error.

    Returns:
        docker.Network: the newly created network or the existing network with the given name

    """

    networks = client.networks.list()
    highest_cidr = ipaddress.IPv4Network(INITIAL_CIDR)

    # determine subnet for the network to be created by finding the highest subnet so far.
    # E.g. when you have three subnets 172.33.1.0, 172.33.2.0, and 172.33.3.0, highest_cidr will be 172.33.3.0
    for network in networks:
        if network.name.lower() == name.lower():
            logger.info(f"Network {name} already exists")
            return network

        has_all_properties = (
            network.attrs["IPAM"]
            and network.attrs["IPAM"]["Config"]
            and len(network.attrs["IPAM"]["Config"]) > 0
            and network.attrs["IPAM"]["Config"][0]["Subnet"]
        )
        if has_all_properties:
            cidr = ipaddress.IPv4Network(network.attrs["IPAM"]["Config"][0]["Subnet"])

            if (
                cidr.network_address.packed[0] == INITIAL_CIDR_FIRST_OCTET
                and cidr.network_address.packed[1] >= INITIAL_CIDR_SECOND_OCTET
                and cidr > highest_cidr
            ):
                highest_cidr = cidr

    # take the highest cidr and add bits used by it, so that if the highest subnet was 172.33.2.0, the new subnet is 172.33.3.0
    # or if the highest subnet was 10.88.0.0/16, the new subnet is 10.89.0.0/24
    next_cidr = ipaddress.IPv4Network(
        (highest_cidr.network_address + 2 ** (32 - highest_cidr.prefixlen)).exploded
        + "/24"
    )
    if next_cidr.network_address.packed[0] > INITIAL_CIDR_FIRST_OCTET:
        raise RuntimeError("No more possible subnet addresses exist")

    logger.info(f"Create network {name} with subnet {next_cidr.exploded}")
    ipam_pool = docker.types.IPAMPool(
        subnet=next_cidr.exploded, gateway=(next_cidr.network_address + 1).exploded
    )
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

    return client.networks.create(
        name=name, check_duplicate=True, ipam=ipam_config, labels=labels
    )


def handle_network(
    client: DockerClient, project_id: str
) -> docker.models.networks.Network:
    network_name = get_network_name(project_id)
    try:
        network = client.networks.get(network_id=network_name)
    except docker.errors.NotFound:
        network = create_network(
            client=client,
            name=network_name,
            labels={
                Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                Labels.PROJECT_NAME.value: project_id,
            },
        )
    connect_to_network(get_this_container(client), network)
    return network


def connect_to_network(
    container: docker.models.containers.Container,
    network: docker.models.networks.Network,
) -> None:
    # Note: connecting the backend container to the network will cause a connection drop on Macs, so the first service deploy call will be shown as failed, even though it succeeded. On Linux, this problem does not seem to exist
    if container:
        is_backend_connected_to_network = container.attrs["NetworkSettings"][
            "Networks"
        ].get(network.name, False)
        if not is_backend_connected_to_network:
            try:
                network.connect(container)
            except docker.errors.APIError as e:
                # Remove the network again as it is not connected to any service.
                network.remove()
                raise ServerBaseError(
                    f"Could not connect the {container.name} to the network {network.name}"
                ) from e


def reconnect_to_all_networks(
    client: DockerClient,
) -> None:
    """Connects the backend container to all networks that belong to the installation.

    A reconnect is required after the container was recreated (e.g. to update the image) and is therefore
    no longer part of all the networks.
    :param client: Docker client
    """
    networks = get_backend_networks(client)
    for network in networks:
        try:
            connect_to_network(get_this_container(client), network)
        except RuntimeError:
            logger.exception(
                "Error reconnecting backend to a network. "
                "This will cause some services to become unavailable."
            )


def get_backend_networks(client: DockerClient) -> List[docker.models.networks.Network]:
    try:
        networks = client.networks.list(
            filters={
                "label": get_label_string(
                    Labels.NAMESPACE.value, settings.SYSTEM_NAMESPACE
                )
            }
        )
    except docker.errors.APIError as e:
        raise ServerBaseError("Could not list backend networks.") from e

    return networks


def get_project_container_selection_labels(
    project_id: str, deployment_type: DeploymentType = DeploymentType.SERVICE
) -> List[str]:
    return [
        get_label_string(selection_label[0], selection_label[1])
        for selection_label in get_project_selection_labels(
            project_id=project_id, deployment_type=deployment_type
        )
    ]


def get_project_containers(
    client: DockerClient,
    project_id: str,
    deployment_type: DeploymentType = DeploymentType.SERVICE,
) -> List[docker.models.containers.Container]:
    labels = get_project_container_selection_labels(
        project_id=project_id, deployment_type=deployment_type
    )

    try:
        containers = client.containers.list(all=True, filters={"label": labels})
    except docker.errors.APIError as e:
        raise ServerBaseError(
            f"Could not list Docker containers for project '{project_id}'."
        ) from e

    return containers


def get_project_container(
    client: DockerClient,
    project_id: str,
    deployment_id: str,
    deployment_type: DeploymentType = DeploymentType.SERVICE,
) -> docker.models.containers.Container:
    labels = get_project_container_selection_labels(
        project_id=project_id, deployment_type=deployment_type
    )
    labels.append(
        get_label_string(Labels.DEPLOYMENT_ID.value, deployment_id),
    )
    try:
        containers = client.containers.list(all=True, filters={"label": labels})
    except docker.errors.APIError as e:
        raise ServerBaseError(
            f"Could not list Docker containers for project '{project_id}' and service '{deployment_id}'."
        ) from e

    if len(containers) == 0:
        raise ResourceNotFoundError(
            f"Could not find service '{deployment_id}' of project '{project_id}'."
        )

    return containers[0]


def get_this_container(
    client: DockerClient,
) -> docker.models.containers.Container:
    """This function returns the Docker container in which this code is running or None if it does not run in a container.

    Args:
        client (DockerClient): The Docker client object

    Returns:
        docker.models.containers.Container: If this code runs in a container, it returns this container otherwise None
    """

    # "Detect" whether it runs in a container by checking the following environment variables
    hostname = os.getenv("HOSTNAME", False)
    if not os.getenv("IS_CONTAXY_CONTAINER", False) or hostname is None:
        return None
    return client.containers.get(hostname)


def delete_container(
    client: DockerClient,
    container: docker.models.containers.Container,
    delete_volumes: bool = False,
) -> None:
    try:
        container.stop()
    except docker.errors.APIError:
        pass

    try:
        container.remove(v=delete_volumes)
    except docker.errors.APIError as e:
        if e.status_code == 409:
            # Deletion is already in progress
            return
        raise ServerBaseError(
            f"Could not delete deployment '{container.name}'.",
        ) from e

    # Named volumes must be deleted manually
    if delete_volumes:
        for mount in container.attrs.get("Mounts", []):
            if mount.get("Type") == "volume" and "Name" in mount:
                try:
                    client.api.remove_volume(mount["Name"])
                except docker.errors.APIError:
                    raise ServerBaseError(
                        f"Could not delete volume {mount['Name']} of deployment '{container.name}'.",
                    )


def check_minimal_resources(
    min_cpus: float,
    min_memory: int,
    min_gpus: int,
    compute_resources: Optional[DeploymentCompute] = None,
) -> None:
    if min_cpus > system_cpu_count:
        raise RuntimeError(
            f"The minimal amount of cpus of {min_cpus} cannot be fulfilled as the system has only {system_cpu_count} cpus."
        )
    if min_memory > system_memory_in_mb:
        raise RuntimeError(
            f"The minimal amount of memory of {min_memory}MB cannot be fulfilled as the system has only {system_memory_in_mb}MB memory"
        )
    if min_gpus > system_gpu_count:
        raise RuntimeError(
            f"The minimal amount of gpus of {min_gpus} cannot be fulfilled as the system has only {system_gpu_count} gpus."
        )

    if compute_resources is None:
        return

    if compute_resources.max_replicas is not None:
        raise RuntimeError("Replicas are not supported in Docker-mode")


def extract_minimal_resources(
    compute_resources: DeploymentCompute,
) -> Tuple[float, int, int]:
    min_cpus = (
        compute_resources.min_cpus if compute_resources.min_cpus is not None else 0
    )
    min_memory = (
        compute_resources.min_memory if compute_resources.min_memory is not None else 0
    )
    min_gpus = (
        compute_resources.min_gpus if compute_resources.min_gpus is not None else 0
    )

    return min_cpus, min_memory, min_gpus


def define_mounts(
    project_id: str,
    container_name: str,
    compute_resources: DeploymentCompute,
    service_requirements: Optional[List[str]] = [],
) -> list:
    mounts = []
    # if service_requirements and "docker" in service_requirements:
    #     # TODO: IMPORTANT mark container as having extended privileges so that on a higher level the platform
    #     # can prevent that a non-admin creates a container with the Docker socket mounted
    #     mounts.append(
    #         docker.types.Mount(
    #             target="/var/run/docker.sock", source="/var/run/docker.sock"
    #         )
    #     )

    if (
        compute_resources.volume_path is not None
        and compute_resources.volume_path != ""
    ):
        if settings.HOST_DATA_ROOT_PATH is None:
            mount_type = "volume"
            prefix = ""
        else:
            mount_type = "bind"
            prefix = settings.HOST_DATA_ROOT_PATH
        mounts.append(
            docker.types.Mount(
                target=str(compute_resources.volume_path),
                source=f"{prefix}{get_volume_name(project_id, container_name)}",
                labels={
                    Labels.NAMESPACE.value: settings.SYSTEM_NAMESPACE,
                    Labels.PROJECT_NAME.value: project_id,
                    Labels.DEPLOYMENT_ID.value: container_name,
                },
                type=mount_type,
            )
        )

    return mounts


def create_container_config(
    deployment: Deployment,
    project_id: str,
) -> Dict[str, Any]:
    compute_resources = deployment.compute
    (
        min_cpus,
        min_memory,
        min_gpus,
    ) = extract_minimal_resources(compute_resources=compute_resources)
    check_minimal_resources(
        min_cpus=min_cpus,
        min_memory=min_memory,
        min_gpus=min_gpus,
    )
    max_cpus = (
        compute_resources.max_cpus if compute_resources.max_cpus is not None else 1
    )
    max_memory = (
        compute_resources.max_memory if compute_resources.max_memory is not None else 6
    )
    # Make sure that the user-entered compute requirements are not bigger than the system's maximum available
    nano_cpus = min(max_cpus, system_cpu_count) * 1e9
    # With regards to memory, Docker requires at least 6MB for a container
    mem_limit = f"{max(_MIN_MEMORY_DEFAULT_MB, min(max_memory, system_memory_in_mb))}MB"

    container_name = deployment.id
    mounts = define_mounts(
        project_id=project_id,
        container_name=container_name,
        compute_resources=compute_resources,
        service_requirements=deployment.requirements,
    )

    return {
        "image": deployment.container_image,
        "entrypoint": deployment.command,
        "command": deployment.args,
        "detach": True,
        "environment": deployment.parameters,
        "labels": {
            **deployment.metadata,
            Labels.DISPLAY_NAME.value: deployment.display_name,
            Labels.DEPLOYMENT_TYPE.value: deployment.deployment_type.value,
            Labels.DESCRIPTION.value: deployment.description,
            Labels.ENDPOINTS.value: map_list_to_string(deployment.endpoints),
            Labels.REQUIREMENTS.value: map_list_to_string(deployment.requirements),
            Labels.ICON.value: deployment.icon,
            Labels.MIN_LIFETIME.value: str(compute_resources.min_lifetime),
            Labels.CREATED_BY.value: deployment.created_by,
            Labels.VOLUME_PATH.value: compute_resources.volume_path,
        },
        "name": container_name,
        "nano_cpus": int(nano_cpus),
        "mem_limit": mem_limit,
        "network": get_network_name(project_id),
        "restart_policy": {"Name": "on-failure", "MaximumRetryCount": 10},
        "mounts": mounts if mounts != [] else None,
    }


def read_container_logs(
    container: docker.models.containers.Container,
    lines: Optional[int] = None,
    since: Optional[datetime] = None,
) -> str:
    try:
        logs = container.logs(tail=lines or "all", since=since)
    except docker.errors.APIError:
        logger.error(f"Could not read logs of container {container.name}.")

    if logs:
        logs = logs.decode("utf-8")
    else:
        logs = NO_LOGS_MESSAGE

    return logs


def wait_for_container(
    container: docker.models.containers.Container,
    client: DockerClient,
    timeout: int = 60,
) -> docker.models.containers.Container:
    start = time.time()
    while time.time() - start < timeout:
        container_info = client.containers.get(container.id)
        if container_info.status.lower() != "created":
            return container_info
        else:
            time.sleep(2)

    raise RuntimeError(f"Timeout while waiting for container {container.id}.")


def list_deploy_service_actions(
    project_id: str, deploy_input: Union[ServiceInput, JobInput]
) -> List[ResourceAction]:
    compute_resources = deploy_input.compute or DeploymentCompute()
    min_cpus, min_memory, min_gpus = extract_minimal_resources(compute_resources)
    try:
        check_minimal_resources(
            min_cpus=min_cpus, min_memory=min_memory, min_gpus=min_gpus
        )
    except RuntimeError:
        return []

    return [
        ResourceAction(
            action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
            display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
        )
    ]
