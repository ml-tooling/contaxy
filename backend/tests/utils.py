import sys
import time

import docker
from pymongo import MongoClient

from contaxy.config import Settings


def start_mongo_db(settings: Settings) -> None:
    client = docker.from_env()
    delete_container(settings.mongo_host, client)
    try:
        client.containers.run(
            "mongo:4.2", name=settings.mongo_host, network="ml-workspace", detach=True
        )
        wait_until_container_started(settings.mongo_host, client)
    except docker.errors.APIError:
        delete_container(settings.mongo_host, client)
        sys.exit(-1)

    _seed_mongo_db(settings)


def remove_mongo_db(settings: Settings) -> None:
    client = docker.from_env()
    delete_container(settings.mongo_host, client)


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
