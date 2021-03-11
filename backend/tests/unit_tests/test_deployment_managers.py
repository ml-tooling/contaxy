import os
import time
from typing import Generator, Union

import pytest
from kubernetes.client.models import V1Namespace, V1Status

from contaxy.data_model import DeploymentType, ServiceInput
from contaxy.managers.deployment_managers import (
    DockerDeploymentManager,
    KubernetesDeploymentManager,
)
from contaxy.managers.deployment_managers.docker_utils import (
    get_network_name,
    get_this_container,
)
from contaxy.managers.deployment_managers.utils import normalize_service_name

pytestmark = pytest.mark.unit

# use a uid here to create unique resources that do not clash with existing resources
uid = str(int(time.time()))
test_project_name = f"test-project-{uid}"
test_service_display_name = f"Test Service-{uid}"
test_namespace = f"test-namespace-{int(time.time())}"
test_service_id = normalize_service_name(
    project_id=test_project_name, display_name=test_service_display_name
)

is_kube_available = os.getenv("KUBE_AVAILABLE", False)


def create_test_service_input(_service_id: str = test_service_id) -> ServiceInput:
    return ServiceInput(
        container_image="tutum/hello-world",
        compute={"max_cpus": 2, "max_memory": 100, "volume_path": "/test_temp"},
        deployment_type=DeploymentType.SERVICE.value,
        display_name=test_service_display_name,
        description="This is a test service",
        # TODO: to pass id here does not make sense but is required by Pydantic
        id=_service_id,
        endpoints=["8080", "8090/webapp"],
        parameters={"FOO": "bar", "FOO2": "bar2", "NVIDIA_VISIBLE_DEVICES": "2"},
        additional_metadata={"some-metadata": "some-metadata-value"},
    )


class DockerTestHandler:
    def __init__(self) -> None:
        self.deployment_manager = DockerDeploymentManager()

    def setup(self) -> str:
        return test_service_id

    def cleanup(self, setup_id: str) -> None:
        self.deployment_manager.delete_service(service_id=setup_id)
        time.sleep(2.5)
        # Wait until container is deleted
        while True:
            try:
                container = self.deployment_manager.client.containers.get(setup_id)
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
        except Exception:
            pass


class KubeTestHandler:
    def __init__(self, test_kube_namespace: str) -> None:
        # Don't try to instantiate the Kubernetes Manager if Kubernetes is not available
        if not is_kube_available:
            return

        self.deployment_manager = KubernetesDeploymentManager(
            kube_namespace=test_kube_namespace
        )

    def setup(self) -> str:
        namespace = V1Namespace(metadata={"name": test_namespace})
        self.deployment_manager.core_api.create_namespace(body=namespace)
        return test_namespace

    def cleanup(self, setup_id: str) -> None:
        if self.deployment_manager is None:
            return

        status: V1Status = self.deployment_manager.core_api.delete_namespace(setup_id)

        if status.code != 200:
            # Try again
            self.deployment_manager.core_api.delete_namespace(setup_id)


pytest_handler_param = [
    DockerTestHandler(),
    pytest.param(
        KubeTestHandler(test_kube_namespace=test_namespace),
        marks=pytest.mark.skipif(
            not is_kube_available,
            reason="A Kubernetes cluster must be accessible to run the KubeSpawner tests",
        ),
    ),
]


@pytest.mark.parametrize("handler", pytest_handler_param)
class TestDeploymentManagers:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, handler: Union[DockerTestHandler, KubeTestHandler]) -> Generator:
        self.handler = handler
        # do nothing as setup
        setup_id = handler.setup()
        yield
        handler.cleanup(setup_id)

    def test_deploy_service(self) -> None:
        test_service_input = create_test_service_input()
        service = self.handler.deployment_manager.deploy_service(
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

    def test_get_service_metadata(self) -> None:
        test_service_input = create_test_service_input()
        service = self.handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )

        queried_service = self.handler.deployment_manager.get_service_metadata(
            service.internal_id
        )

        assert queried_service is not None
        assert queried_service.internal_id == service.internal_id
        assert "some-metadata" in queried_service.additional_metadata

        self.handler.deployment_manager.delete_service(service_id=service.id)
        time.sleep(5)
        queried_service = self.handler.deployment_manager.get_service_metadata(
            service.internal_id
        )

        assert queried_service is None

    def test_list_services(self) -> None:
        test_service_input = create_test_service_input()
        service = self.handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )
        services = self.handler.deployment_manager.list_services(
            project_id=test_project_name
        )
        assert len(services) == 1

        self.handler.deployment_manager.delete_service(service_id=service.id)
        time.sleep(5)
        services = self.handler.deployment_manager.list_services(
            project_id=test_project_name
        )
        assert len(services) == 0

    def test_get_logs(self) -> None:
        log_input = "foobar"
        service_input = ServiceInput(
            container_image="ubuntu:20.04",
            command=f"/bin/bash -c 'echo {log_input}'",
            deployment_type=DeploymentType.SERVICE.value,
            display_name=test_service_display_name,
            id=test_service_id,
            parameters={"FOO": "bar", "FOO2": "bar2"},
        )

        service = self.handler.deployment_manager.deploy_service(
            service=service_input, project_id=test_project_name
        )
        time.sleep(3)
        logs = self.handler.deployment_manager.get_service_logs(
            service_id=service.internal_id
        )
        assert logs
        assert logs.startswith(log_input)


class TestDockerDeploymentManager:
    def test_container_object(self) -> None:
        handler = DockerTestHandler()
        _service_name = f"test-project-{int(time.time())}"
        test_service_input = create_test_service_input(_service_name)

        service = handler.deployment_manager.deploy_service(
            test_service_input, test_project_name
        )
        container = handler.deployment_manager.client.containers.get(service.id)
        assert container is not None
        labels = container.labels

        assert labels.get("contaxy.endpoints", "") == "8080,8090/webapp"
        container.remove(force=True)
