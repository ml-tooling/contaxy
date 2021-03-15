import sys
import time

import docker
import pytest

from contaxy.config import Settings

pytestmark = pytest.mark.unit


def start_db(settings: dict) -> None:

    client = docker.from_env()

    container_name = settings.get("container_name")
    assert container_name

    delete_container(container_name, client)

    container_config = {
        "name": container_name,
        "detach": True,
        "environment": {
            "POSTGRES_USER": settings.get("user"),
            "POSTGRES_PASSWORD": settings.get("pw"),
            "POSTGRES_DB": settings.get("db_name"),
        },
    }

    if settings.get("docker_network"):
        # Docker outside Docker case e.g. when developing in the workspace
        container_config.update({"network": settings.get("docker_network")})
    else:
        # Port needs to be exposed
        port = settings.get("port")
        assert port
        container_config.update({"ports": {"5432": port}})

    try:
        client.containers.run(settings.get("docker_image"), **container_config)
        wait_until_db_is_started(container_name, client)
    except docker.errors.APIError:
        print("Delete Container!!")
        delete_container(container_name, client)
        sys.exit(-1)


def destroy_db(settings: Settings) -> None:
    client = docker.from_env()
    delete_container(settings.get("container_name"), client)


def delete_container(
    name: str, client: docker.DockerClient, delete_volume: bool = True
) -> None:
    try:
        container = client.containers.get(name)
    except docker.errors.NotFound:
        return
    try:
        container.remove(force=True, v=delete_volume)
    except docker.errors.APIError:
        return


def container_is_running(name: str, client: docker.DockerClient) -> bool:
    try:
        container = client.containers.get(name)
    except docker.errors.NotFound:
        return False

    exit_code, output = container.exec_run("pg_isready -U postgres")

    return True if exit_code == 0 else False


def wait_until_db_is_started(name: str, client: docker.DockerClient) -> None:

    MAX_RETRY = 30

    for index in range(MAX_RETRY):
        if container_is_running(name, client):
            break
        time.sleep(2)

    if index == MAX_RETRY:
        print(f"Container {name} did not start")
        sys.exit(-1)

    time.sleep(2)
