import os
import time
from typing import Generator, Union

import pytest
from kubernetes import stream
from kubernetes.client.models import V1Namespace
from kubernetes.client.rest import ApiException

from contaxy.managers.deployment.docker import DockerDeploymentManager
from contaxy.managers.deployment.docker_utils import (
    get_network_name,
    get_this_container,
)
from contaxy.managers.deployment.kubernetes import KubernetesDeploymentManager
from contaxy.managers.deployment.utils import get_deployment_id
from contaxy.schema.deployment import (
    DeploymentType,
    Job,
    JobInput,
    Service,
    ServiceInput,
)

pytestmark = pytest.mark.unit

# use a uid here to create unique resources that do not clash with existing resources
uid = str(int(time.time()))
test_project_name = f"test-project-{uid}"
test_service_display_name = f"Test Service-{uid}"
test_service_id = get_deployment_id(
    project_id=test_project_name,
    deployment_name=test_service_display_name,
    deployment_type=DeploymentType.SERVICE,
)

is_kube_available = os.getenv("KUBE_AVAILABLE", "")
if is_kube_available != "true":
    is_kube_available = ""


def create_test_service_input(
    _service_id: str = test_service_id, display_name: str = test_service_display_name
) -> ServiceInput:
    return ServiceInput(
        container_image="tutum/hello-world",
        compute={"max_cpus": 2, "max_memory": 100, "volume_path": "/test_temp"},
        deployment_type=DeploymentType.SERVICE.value,
        display_name=display_name,
        description="This is a test service",
        # TODO: to pass id here does not make sense but is required by Pydantic
        id=_service_id,
        endpoints=["8080", "8090/webapp"],
        parameters={"FOO": "bar", "FOO2": "bar2", "NVIDIA_VISIBLE_DEVICES": "2"},
        metadata={"some-metadata": "some-metadata-value"},
    )


class DockerTestHandler:
    def __init__(self) -> None:
        self.deployment_manager = DockerDeploymentManager(
            request_state=None, global_state=None
        )

    def setup(self) -> str:
        return test_service_id

    def cleanup(self, setup_id: str) -> None:
        try:
            self.deployment_manager.delete_service(
                project_id=test_project_name, service_id=setup_id
            )
        except RuntimeError:
            # service not found
            return

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

    def deploy_service(self, project_id: str, service: ServiceInput) -> Service:
        deployed_service = self.deployment_manager.deploy_service(
            project_id=project_id, service=service
        )
        time.sleep(2)
        return deployed_service

    def deploy_job(self, project_id: str, job: JobInput) -> Job:
        deployed_job = self.deployment_manager.deploy_job(
            project_id=project_id, job=job
        )
        time.sleep(3)
        return deployed_job


class KubeTestHandler:
    def setup(self) -> str:
        test_namespace_name = f"test-namespace-{int(time.time())}"
        self.deployment_manager = KubernetesDeploymentManager(
            global_state=None, request_state=None, kube_namespace=test_namespace_name
        )
        namespace = V1Namespace(metadata={"name": test_namespace_name})
        self.deployment_manager.core_api.create_namespace(body=namespace)
        return test_namespace_name

    def cleanup(self, setup_id: str) -> None:
        if self.deployment_manager is None:
            return

        self.deployment_manager.core_api.delete_namespace(
            setup_id, propagation_policy="Foreground"
        )

        start = time.time()
        timeout = 60
        while time.time() - start < timeout:
            try:
                self.deployment_manager.core_api.read_namespace(name=setup_id)
                time.sleep(2)
            except ApiException:
                break

    def deploy_service(self, project_id: str, service: ServiceInput) -> Service:
        return self.deployment_manager.deploy_service(
            project_id=project_id, service=service, wait=True
        )

    def deploy_job(self, project_id: str, job: JobInput) -> Job:
        return self.deployment_manager.deploy_job(
            project_id=project_id, job=job, wait=True
        )


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
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, handler: Union[DockerTestHandler, KubeTestHandler]) -> Generator:
        self.handler = handler
        # do nothing as setup
        setup_id = handler.setup()
        yield
        handler.cleanup(setup_id)

    def test_deploy_service(self) -> None:
        test_service_input = create_test_service_input()
        service = self.handler.deploy_service(
            project_id=test_project_name,
            service=test_service_input,
        )
        assert service.display_name == test_service_input.display_name
        assert service.internal_id != ""
        assert service.metadata.get("ctxy.projectName", "") == test_project_name
        assert service.parameters.get("FOO", "") == "bar"
        assert (
            service.parameters.get("NVIDIA_VISIBLE_DEVICES", "Not allowed to set")
            == "Not allowed to set"
        )
        assert "some-metadata" in service.metadata

    def test_get_service_metadata(self) -> None:
        test_service_input = create_test_service_input()
        service = self.handler.deploy_service(
            project_id=test_project_name,
            service=test_service_input,
        )

        queried_service = self.handler.deployment_manager.get_service_metadata(
            project_id=test_project_name, service_id=service.id
        )

        assert queried_service is not None
        assert queried_service.internal_id == service.internal_id
        assert "some-metadata" in queried_service.metadata

        self.handler.deployment_manager.delete_service(
            project_id=test_project_name, service_id=service.id
        )

        with pytest.raises(RuntimeError):
            self.handler.deployment_manager.get_service_metadata(
                project_id=test_project_name, service_id=service.id
            )

    def test_list_services(self) -> None:
        test_service_input = create_test_service_input()
        service = self.handler.deploy_service(
            project_id=test_project_name,
            service=test_service_input,
        )
        services = self.handler.deployment_manager.list_services(
            project_id=test_project_name
        )
        assert len(services) == 1

        self.handler.deployment_manager.delete_service(
            project_id=test_project_name, service_id=service.id
        )
        services = self.handler.deployment_manager.list_services(
            project_id=test_project_name
        )
        assert len(services) == 0

    def test_get_logs(self) -> None:
        log_input = "foobar"
        job_input = JobInput(
            container_image="ubuntu:20.04",
            command=f"/bin/bash -c 'echo {log_input}'",
            deployment_type=DeploymentType.SERVICE.value,
            display_name=test_service_display_name,
            id=test_service_id,
            parameters={"FOO": "bar", "FOO2": "bar2"},
        )

        service = self.handler.deploy_job(job=job_input, project_id=test_project_name)

        logs = self.handler.deployment_manager.get_service_logs(
            project_id=test_project_name, service_id=service.internal_id
        )
        assert logs
        assert logs.startswith(log_input)

    def test_project_isolation(self) -> None:
        """Test that services of the same project can reach each others' endpoints and services of different projects cannot."""

        def create_wget_command(target_ip: str) -> str:
            return f"wget -T 10 -qO/dev/stdout {target_ip}:80"

        project_1 = f"{test_project_name}-1"
        project_2 = f"{test_project_name}-2"
        test_service_input_1 = create_test_service_input(
            _service_id=f"{test_service_id}-1",
            display_name=f"{test_service_display_name}-1",
        )
        test_service_input_2 = create_test_service_input(
            _service_id=f"{test_service_id}-2",
            display_name=f"{test_service_display_name}-2",
        )
        test_service_input_3 = create_test_service_input(
            _service_id=f"{test_service_id}-3",
            display_name=f"{test_service_display_name}-3",
        )

        service_1 = self.handler.deploy_service(
            project_id=project_1,
            service=test_service_input_1,
        )
        service_2 = self.handler.deploy_service(
            project_id=project_1,
            service=test_service_input_2,
        )
        service_3 = self.handler.deploy_service(
            project_id=project_2,
            service=test_service_input_3,
        )

        if type(self.handler) == DockerTestHandler:
            container_1 = self.handler.deployment_manager.client.containers.get(
                service_1.id
            )
            container_2 = self.handler.deployment_manager.client.containers.get(
                service_2.id
            )
            container_3 = self.handler.deployment_manager.client.containers.get(
                service_3.id
            )
            assert container_1
            assert container_2
            assert container_3

            exit_code, output = container_1.exec_run(
                create_wget_command(container_2.attrs["Config"]["Hostname"])
            )
            assert exit_code == 0
            assert b"Hello world!" in output

            exit_code, output = container_1.exec_run(
                create_wget_command(container_3.attrs["Config"]["Hostname"])
            )
            assert exit_code == 1
            assert b"wget: bad address" in output

            exit_code, output = container_3.exec_run(
                create_wget_command(container_2.attrs["Config"]["Hostname"])
            )
            assert exit_code == 1
            assert b"wget: bad address" in output
        elif type(self.handler) == KubeTestHandler:
            namespace = self.handler.deployment_manager.kube_namespace
            pod_1 = self.handler.deployment_manager.core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"ctxy.deploymentName={service_1.id},ctxy.projectName={project_1}",
            ).items[0]

            pod_2 = self.handler.deployment_manager.core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"ctxy.deploymentName={service_2.id},ctxy.projectName={project_1}",
            ).items[0]

            pod_3 = self.handler.deployment_manager.core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"ctxy.deploymentName={service_3.id},ctxy.projectName={project_2}",
            ).items[0]

            _command_prefix = ["/bin/sh", "-c"]
            output = stream.stream(
                self.handler.deployment_manager.core_api.connect_get_namespaced_pod_exec,
                pod_1.metadata.name,
                namespace,
                command=[
                    *_command_prefix,
                    create_wget_command(pod_2.status.pod_ip),
                ],
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            assert output
            assert "Hello world!" in output

            output = stream.stream(
                self.handler.deployment_manager.core_api.connect_get_namespaced_pod_exec,
                pod_1.metadata.name,
                namespace,
                command=[
                    *_command_prefix,
                    create_wget_command(pod_3.status.pod_ip),
                ],
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            assert output
            assert "wget: download timed out" in output

            output = stream.stream(
                self.handler.deployment_manager.core_api.connect_get_namespaced_pod_exec,
                pod_3.metadata.name,
                namespace,
                command=[
                    *_command_prefix,
                    create_wget_command(pod_2.status.pod_ip),
                ],
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            assert output
            assert "wget: download timed out" in output

        self.handler.deployment_manager.delete_service(
            project_id=project_1, service_id=service_1.id, delete_volumes=True
        )
        self.handler.deployment_manager.delete_service(
            project_id=project_1, service_id=service_2.id, delete_volumes=True
        )
        self.handler.deployment_manager.delete_service(
            project_id=project_2, service_id=service_3.id, delete_volumes=True
        )


class TestDockerDeploymentManager:
    def test_container_object(self) -> None:
        handler = DockerTestHandler()
        _service_id = f"test-project-{int(time.time())}"
        test_service_input = create_test_service_input(_service_id=_service_id)

        service = handler.deploy_service(
            project_id=test_project_name,
            service=test_service_input,
        )
        container = handler.deployment_manager.client.containers.get(service.id)
        assert container is not None
        labels = container.labels

        assert labels.get("ctxy.endpoints", "") == "8080,8090/webapp"
        container.remove(force=True)
