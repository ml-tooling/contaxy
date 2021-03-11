import ipaddress
import os
import subprocess
from typing import Any, Dict

import docker

from ... import data_model
from .utils import log, map_labels

# we create networks in the range of 172.33-255.0.0/24
# Docker by default uses the range 172.17-32.0.0, so we should be save using that range
INITIAL_CIDR_FIRST_OCTET = 10
INITIAL_CIDR_SECOND_OCTET = 0
INITIAL_CIDR = f"{INITIAL_CIDR_FIRST_OCTET}.{INITIAL_CIDR_SECOND_OCTET}.0.0/24"


def transform_container(
    container: docker.models.containers.Container,
) -> Dict[str, Any]:
    labels = map_labels(container.labels)

    host_config = container.attrs["HostConfig"]
    compute_resources = data_model.DeploymentCompute(
        max_cpus=host_config["NanoCpus"] / 1e9,
        max_memory=host_config["Memory"] / 1000 / 1000,
        max_gpus=None,  # TODO: fill with sensible information - where to get it from?
        min_lifetime=labels.min_lifetime,
        volume_Path=labels.volume_path,
        # TODO: add max_volume_size, max_replicas
    )

    try:
        status = data_model.DeploymentStatus(container.status).value
    except ValueError:
        status = data_model.DeploymentStatus.UNKNOWN.value

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

    return {
        "container_image": container.image.tags[0],
        "command": " ".join(container.attrs.get("Args", [])),
        "compute": compute_resources,
        "additional_metadata": labels.additional_metadata,
        "deployment_type": labels.deployment_type,
        "description": labels.description,
        "display_name": labels.display_name,
        "endpoints": labels.endpoints,
        #         "exit_code": container.attrs.get("State", {}).get("ExitCode", -1),
        "icon": labels.icon,
        "id": container.id,
        "internal_id": container.id,
        "parameters": parameters,
        "started_at": started_at,
        "status": status,
        "stopped_at": stopped_at,
    }


def transform_service(
    container: docker.models.containers.Container,
) -> data_model.Service:
    transformed_container = transform_container(container=container)
    return data_model.Service(**transformed_container)


def transform_job(container: docker.models.containers.Container) -> data_model.Job:
    transformed_container = transform_container(container=container)
    return data_model.Job(**transformed_container)


# TODO: copied from ML Hub
def create_network(
    client: docker.client, name: str, labels: Dict[str, str]
) -> docker.models.networks.Network:
    """Create a new network to put the new container into it.
    Containers are separated by networks to prevent them from seeing each other.
    Determine whether a new subnet has to be used. Otherwise, the default Docker subnet would be used
    and, as a result, the amount of networks that can be created is strongly limited.
    We create networks in the range of 172.33-255.0.0/24 whereby Docker by default uses the range 172.17-32.0.0
    See: https://stackoverflow.com/questions/41609998/how-to-increase-maximum-docker-network-on-one-server ; https://loomchild.net/2016/09/04/docker-can-create-only-31-networks-on-a-single-machine/

    Args:
        network_name (str): name of the network to be created
        network_labels (Dict[str, str]): labels that will be attached to the network
    Raises:
        docker.errors.APIError: Thrown by `docker.client.networks.create` upon error.
    Returns:
        docker.Network: the newly created network or the existing network with the given name

    """

    networks = client.networks.list()
    highest_cidr = ipaddress.ip_network(INITIAL_CIDR)

    # determine subnet for the network to be created by finding the highest subnet so far.
    # E.g. when you have three subnets 172.33.1.0, 172.33.2.0, and 172.33.3.0, highest_cidr will be 172.33.3.0
    for network in networks:
        if network.name.lower() == name.lower():
            log(f"Network {name} already exists")
            return network

        has_all_properties = (
            network.attrs["IPAM"]
            and network.attrs["IPAM"]["Config"]
            and len(network.attrs["IPAM"]["Config"]) > 0
            and network.attrs["IPAM"]["Config"][0]["Subnet"]
        )
        if has_all_properties:
            cidr = ipaddress.ip_network(network.attrs["IPAM"]["Config"][0]["Subnet"])

            if (
                cidr.network_address.packed[0] == INITIAL_CIDR_FIRST_OCTET
                and cidr.network_address.packed[1] >= INITIAL_CIDR_SECOND_OCTET
                and cidr > highest_cidr
            ):
                highest_cidr = cidr

    # take the highest cidr and add 256 bits, so that if the highest subnet was 172.33.2.0, the new subnet is 172.33.3.0
    next_cidr = ipaddress.ip_network(
        (highest_cidr.network_address + 256).exploded + "/24"
    )
    if next_cidr.network_address.packed[0] > INITIAL_CIDR_FIRST_OCTET:
        raise Exception("No more possible subnet addresses exist")

    log(f"Create network {name} with subnet {next_cidr.exploded}")
    ipam_pool = docker.types.IPAMPool(
        subnet=next_cidr.exploded, gateway=(next_cidr.network_address + 1).exploded
    )
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

    return client.networks.create(
        name=name, check_duplicate=True, ipam=ipam_config, labels=labels
    )


def get_network_name(project_id: str) -> str:
    # TODO: follow naming concept for networks
    return f"{project_id}-network"


def get_gpu_info() -> int:
    count_gpu = 0
    try:
        # NOTE: this approach currently only works for nvidia gpus.
        ps = subprocess.Popen(
            ("find", "/proc/irq/", "-name", "nvidia"), stdout=subprocess.PIPE
        )
        output = subprocess.check_output(("wc", "-l"), stdin=ps.stdout)
        ps.wait()
        count_gpu = int(output.decode("utf-8"))
    except Exception:
        pass

    return count_gpu


def get_this_container(client: docker.client) -> docker.models.containers.Container:
    """This function returns the Docker container in which this code is running or None if it does not run in a container.

    Args:
        client (docker.client): The Docker client object

    Returns:
        docker.models.containers.Container: If this code runs in a container, it returns this container otherwise None
    """

    hostname = os.getenv("HOSTNAME", None)
    if hostname is None:
        return None
    return client.containers.get(hostname)
