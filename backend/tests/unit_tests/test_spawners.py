import os
from typing import Union

import pytest

TEST_SPAWNER = os.getenv("TEST_SPAWNER", "docker")


class DockerSpawnManager:
    # TODO: replace with actual spawner from Contaxy
    def hello(self) -> str:
        return "hello"


class KubeSpawnManager:
    # TODO: replace with actual spawner from Contaxy
    def hello(self) -> str:
        return "hello"


class DockerTestHandler:
    def __init__(self):
        self.spawner = DockerSpawnManager()

    def cleanup(self, service_id: str = "") -> None:
        # TODO: add Docker-specific cleanups, probably directly on client level and not on Spawner level (e.g. delete resources directly)
        pass


class KubeTestHandler:
    def __init__(self):
        self.spawner = KubeSpawnManager()

    def cleanup(self, service_id: str = "") -> None:
        # TODO: add Kube-specific cleanups, probably directly on client level and not on Spawner level (e.g. delete resources directly)
        pass


@pytest.mark.unit
class TestSpawner:
    @pytest.fixture(scope="session")
    def handler(self) -> Union[DockerTestHandler, KubeTestHandler]:
        if "kube" == TEST_SPAWNER:
            print("Use KubeSpawner")
            return KubeTestHandler()

        print("Use DockerSpawner")
        return DockerTestHandler()

    def test_hello(self, handler: Union[DockerTestHandler, KubeTestHandler]) -> None:
        res = handler.spawner.hello()
        assert res == "hello"
        handler.cleanup()