import sys
import time

import docker
from pymongo import MongoClient

from contaxy.config import Settings

MONGO_CONTAINER_NAME = "contaxy-test-mongo"


def start_mongo_db(settings: Settings) -> None:

    client = docker.from_env()

    delete_container(MONGO_CONTAINER_NAME, client)

    container_config = {"name": MONGO_CONTAINER_NAME, "detach": True}

    if settings.local_test_docker_network:
        # Docker outside Docker case e.g. when developing in the workspace
        container_config.update({"network": settings.local_test_docker_network})
    else:
        # Port needs to be exposed
        container_config.update({"ports": {"27017": settings.mongo_port}})

    try:
        client.containers.run(settings.mongo_image, **container_config)
        wait_until_container_started(MONGO_CONTAINER_NAME, client)
    except docker.errors.APIError:
        delete_container(MONGO_CONTAINER_NAME, client)
        sys.exit(-1)

    _seed_mongo_db(settings)


def remove_mongo_db(settings: Settings) -> None:
    client = docker.from_env()
    delete_container(MONGO_CONTAINER_NAME, client)


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
    container = client.containers.get(name)
    return True if container else False


def wait_until_container_started(name: str, client: docker.DockerClient) -> None:

    for index in range(15):
        if container_is_running(name, client):
            break
        time.sleep(1)

    if index == 15:
        print(f"Container {name} did not start")
        sys.exit(-1)


def _seed_mongo_db(settings: Settings):
    client = MongoClient(settings.mongo_host, settings.mongo_port)
    fake_users_db = [
        {
            "id": "1",
            "username": "admin",
            "email": "admin@mltooling.org",
            "display_name": "Lukas Podolski",
            "password": "$2b$12$zzWEQiyZ6BWAprjS9Wg90eOA3QlS1nBrKWVhhNKGR9rSNaY0Z6JZ.",
            "permissions": ["admin"],
        },
    ]
    client[settings.mongo_db_name].users.insert_many(fake_users_db)
