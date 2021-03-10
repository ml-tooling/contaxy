import os
import time
from typing import Union

import pytest

from ...src.contaxy.data_model import DeploymentType, ServiceInput
from ...src.contaxy.managers.deployment_managers import (
    DockerDeploymentManager,
    KubernetesDeploymentManager,
)
from ...src.contaxy.managers.deployment_managers.docker_utils import (
    get_network_name,
    get_this_container,
)

pytestmark = pytest.mark.unit

uid = str(int(time.time()))
test_project_name = f"test-project-{uid}"
service_name = f"Test Service-{uid}"


def create_test_service_input(_service_name: str = service_name) -> ServiceInput:
    return ServiceInput(
        container_image="tutum/hello-world",
        compute={"max_cpus": 2, "max_memory": 100, "volume_path": "/test_temp"},
        deployment_type=DeploymentType.SERVICE.value,
        display_name=_service_name,
        description="This is a test service",
        # TODO: to pass id here does not make sense but is required by Pydantic
        id=_service_name,
        endpoints=["8080", "8090/webapp"],
        parameters={"FOO": "bar", "FOO2": "bar2", "NVIDIA_VISIBLE_DEVICES": "2"},
        additional_metadata={"some-metadata": "some-metadata-value"},
    )


class DockerTestHandler:
    def __init__(self):
        self.deployment_manager = DockerDeploymentManager()

    def cleanup(self, service_id: str = service_name) -> None:
        is_deleted = self.deployment_manager.delete_service(service_id=service_id)

        # Wait until container is deleted
        while True:
            try:
                container = self.deployment_manager.client.containers.get(service_id)
                container.remove(force=True)
                time.sleep(5)
            except Exception:
                break
        try:
            network = self.deployment_manager.client.networks.get(
                get_network_name(project_id=test_project_name)
            )
            # only relevant for when the code runs within a container (as then the DockerDeploymentManager behaves slightly different)
            host_container = get_this_container(client=self.deployment_manager.client)
            if host_container:
                network.disconnect()
                network.remove()
        except Exception as e:
            pass


class KubeTestHandler:
    def __init__(self):
        # TODO: use KubernetesDeploymentManager here when it can be instantiated
        self.deployment_manager = (
            DockerDeploymentManager()
        )  # KubernetesDeploymentManager()

    def cleanup(self, service_id: str = "") -> None:
        # TODO: add Kube-specific cleanups, probably directly on client level and not on Spawner level (e.g. delete resources directly)
        pass


is_kube_available = os.getenv("KUBE_AVAILABLE", False)
pytest_handler_param = [
    DockerTestHandler(),
    pytest.param(
        KubeTestHandler(),
        marks=pytest.mark.skipif(
            not is_kube_available,
            reason="A Kubernetes cluster must be accessible to run the KubeSpawner tests",
        ),
    ),
]


@pytest.mark.parametrize("handler", pytest_handler_param)
class TestDeploymentManagers:
    @pytest.fixture(autouse=True, scope="session")
    def cleanup(self, handler: Union[DockerTestHandler, KubeTestHandler]):
        # do nothing as setup
        yield
        handler.cleanup()

    def test_hello(self, handler: Union[DockerTestHandler, KubeTestHandler]) -> None:
        print(type(handler))
        res = handler.deployment_manager.hello()
        assert res == "hello"

    def test_deploy_service(self, handler: Union[DockerTestHandler, KubeTestHandler]):
        test_service_input = create_test_service_input()
        service = handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )

        assert service.display_name == test_service_input.display_name
        assert service.internal_id != ""
        assert (
            service.additional_metadata.get("contaxy.projectName", "")
            == test_project_name
        )
        assert service.parameters.get("FOO", "") == "bar"
        assert (
            service.parameters.get("NVIDIA_VISIBLE_DEVICES", "Not allowed to set")
            == "Not allowed to set"
        )
        assert "some-metadata" in service.additional_metadata

        handler.cleanup(service_id=service.id)

    def test_get_service_metadata(
        self, handler: Union[DockerTestHandler, KubeTestHandler]
    ):
        test_service_input = create_test_service_input()
        service = handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )

        queried_service = handler.deployment_manager.get_service_metadata(
            service.internal_id
        )

        assert queried_service is not None
        assert queried_service.internal_id == service.internal_id
        assert "some-metadata" in queried_service.additional_metadata

        handler.cleanup(service_id=service.id)

        queried_service = handler.deployment_manager.get_service_metadata(
            service.internal_id
        )

        assert queried_service is None

    def test_list_services(self, handler: Union[DockerTestHandler, KubeTestHandler]):
        test_service_input = create_test_service_input()
        service = handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )
        services = handler.deployment_manager.list_services(
            project_id=test_project_name
        )
        assert len(services) == 1

        handler.cleanup(service_id=service.id)

        services = handler.deployment_manager.list_services(
            project_id=test_project_name
        )
        assert len(services) == 0

        handler.cleanup(service_id=service.id)

    def test_get_logs(self, handler: Union[DockerTestHandler, KubeTestHandler]):
        log_input = "foobar"
        service_input = ServiceInput(
            container_image="ubuntu:20.04",
            command=f"/bin/bash -c 'echo {log_input}'",
            deployment_type=DeploymentType.SERVICE.value,
            display_name=service_name,
            id=service_name,
            parameters={"FOO": "bar", "FOO2": "bar2"},
        )

        service = handler.deployment_manager.deploy_service(
            service=service_input, project_id=test_project_name
        )
        logs = handler.deployment_manager.get_service_logs(
            service_id=service.internal_id
        )

        assert logs.startswith(log_input.encode())
        handler.cleanup(service_id=service.id)


class TestDockerDeploymentManager:
    def test_container_object(self):
        handler = DockerTestHandler()
        _service_name = f"test-project-{int(time.time())}"
        test_service_input = create_test_service_input(_service_name)

        service = handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )
        container = handler.deployment_manager.client.containers.get(service.id)
        assert container is not None
        labels = container.labels

        handler.cleanup(service_id=service.id)

        assert labels.get("contaxy.endpoints", "") == "8080,8090/webapp"

        handler.cleanup(service_id=service.id)

