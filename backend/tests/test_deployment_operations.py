import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from random import randint
from typing import Generator, Tuple

import pytest
import requests
from fastapi.testclient import TestClient
from kubernetes import stream
from kubernetes.client.models import V1Namespace
from kubernetes.client.rest import ApiException

from contaxy import config
from contaxy.clients import AuthClient, DeploymentManagerClient, SystemClient
from contaxy.managers.auth import AuthManager
from contaxy.managers.deployment.docker import DockerDeploymentManager
from contaxy.managers.deployment.docker_utils import (
    get_network_name,
    get_this_container,
)
from contaxy.managers.deployment.kubernetes import KubernetesDeploymentManager
from contaxy.managers.deployment.manager import DeploymentManagerWithDB
from contaxy.managers.deployment.utils import _ENV_VARIABLE_CONTAXY_SERVICE_URL, Labels
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.system import SystemManager
from contaxy.operations.deployment import DeploymentOperations
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
)
from contaxy.schema.deployment import (
    DeploymentStatus,
    DeploymentType,
    Job,
    JobInput,
    Service,
    ServiceInput,
    ServiceUpdate,
)
from contaxy.schema.exceptions import (
    ClientBaseError,
    ClientValueError,
    ResourceNotFoundError,
)
from contaxy.schema.system import AllowedImageInfo
from contaxy.utils import auth_utils
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings
from .utils import ComponentManagerMock

TYPE_DOCKER = "docker"
TYPE_KUBERNETES = "kubernetes"


def get_random_resources() -> Tuple[int, str, str]:
    uid = randint(1, 100000)
    project_id = f"{uid}-dm-test-project"
    service_display_name = f"{uid}-dm-test-service"

    return uid, project_id, service_display_name


def create_test_service_input(display_name: str) -> ServiceInput:
    return ServiceInput(
        container_image="tutum/hello-world:latest",
        compute={
            "max_cpus": 2,
            "max_memory": 100,
        },  # TODO: Also test persistent volumes
        display_name=display_name,
        description="This is a test service",
        endpoints=["8080", "8090/webapp"],
        parameters={
            "FOO": "bar",
            "FOO2": "bar2",
            "NVIDIA_VISIBLE_DEVICES": "2",
            "BASE_URL": f"{{env.{_ENV_VARIABLE_CONTAXY_SERVICE_URL}}}",
        },
        metadata={"some-metadata": "some-metadata-value"},
    )


def create_test_echo_job_input(
    display_name: str,
    log_input: str = "",
) -> JobInput:
    return JobInput(
        container_image="ubuntu:20.04",
        command=["/bin/bash"],
        args=["-c", f"echo {log_input}"],
        display_name=display_name,
        parameters={"FOO": "bar", "FOO2": "bar2"},
        metadata={"some-metadata": "some-metadata-value"},
    )


class DeploymentOperationsTests(ABC):
    @property
    @abstractmethod
    def deployment_manager(self) -> DeploymentOperations:
        pass

    @property
    @abstractmethod
    def system_manager(self) -> SystemManager:
        pass

    @property
    @abstractmethod
    def project_id(self) -> str:
        pass

    @property
    @abstractmethod
    def service_display_name(self) -> str:
        pass

    @pytest.fixture(autouse=True)
    def reset_deployed_services(self):
        self._deployed_services = []

    def deploy_service(self, project_id: str, service: ServiceInput) -> Service:
        service = self.deployment_manager.deploy_service(
            project_id=project_id, service=service, wait=True
        )
        self._deployed_services.append(service.id)
        return service

    def deploy_job(self, project_id: str, job: JobInput) -> Job:
        deployed_job = self.deployment_manager.deploy_job(
            project_id=project_id, job=job, wait=True
        )
        return deployed_job

    def test_deploy_service(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        assert service.display_name == test_service_input.display_name
        assert service.internal_id != ""
        assert service.metadata.get(Labels.PROJECT_NAME.value, "") == self.project_id
        assert service.parameters.get("FOO", "") == "bar"
        assert "some-metadata" in service.metadata

    def test_update_service(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        assert service.parameters.get("FOO", "") == "bar"
        updated_service_input = ServiceUpdate(
            parameters={"FOO": "updated", "BASE_URL": None},
            metadata={"some-metadata": None},
            description="Updated service",
        )
        service = self.deployment_manager.update_service(
            project_id=self.project_id,
            service_id=service.id,
            service=updated_service_input,
        )
        assert service.display_name == test_service_input.display_name
        assert service.container_image == test_service_input.container_image
        assert service.metadata.get(Labels.PROJECT_NAME.value, "") == self.project_id
        assert service.parameters.get("FOO", "") == "updated"
        assert service.parameters.get("FOO2", "") == "bar2"
        assert "BASE_URL" not in service.parameters
        assert "some-metadata" not in service.metadata

    def test_invalid_update_service(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        # Update of display name should not be possible
        updated_service_input = ServiceUpdate(display_name="new-display-name")
        with pytest.raises(ClientValueError):
            self.deployment_manager.update_service(
                project_id=self.project_id,
                service_id=service.id,
                service=updated_service_input,
            )

    def test_update_service_access(self):
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        assert service.last_access_time is None
        assert service.last_access_user is None

        self.deployment_manager.update_service_access(
            project_id=self.project_id,
            service_id=service.id,
        )
        service = self.deployment_manager.get_service_metadata(
            project_id=self.project_id,
            service_id=service.id,
        )
        assert service.last_access_time <= datetime.now(timezone.utc)
        assert service.last_access_user == ""
        # TODO: Test with authenticated user which should be set in last_access_user

        self.deployment_manager.update_service_access(
            project_id=self.project_id,
            service_id=service.id,
        )
        service_updated = self.deployment_manager.get_service_metadata(
            project_id=self.project_id,
            service_id=service.id,
        )
        assert service.last_access_time <= service_updated.last_access_time

    @pytest.fixture
    def add_allowed_image(self) -> Generator:
        self.system_manager.add_allowed_image(
            AllowedImageInfo(
                image_name="allowed-image",
                image_tags=["0.1"],
            )
        )
        yield
        self.system_manager.delete_allowed_image("allowed-image")

    @pytest.mark.usefixtures("add_allowed_image")
    def test_cannot_deploy_disallowed_image(self) -> None:
        with pytest.raises(ClientValueError):
            self.deploy_service(
                project_id=self.project_id,
                service=ServiceInput(container_image="disallowed-image:0.1"),
            )
        with pytest.raises(ClientValueError):
            self.deploy_job(
                project_id=self.project_id,
                job=JobInput(container_image="disallowed-image:0.1"),
            )

    def test_stop_and_start_service(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        # Running service should provide stop action but not start action
        service_action_ids = [
            service.action_id
            for service in self.deployment_manager.list_service_actions(
                self.project_id, service.id
            )
        ]
        assert service.status == DeploymentStatus.RUNNING
        assert "stop" in service_action_ids
        assert "start" not in service_action_ids
        # Execute stop action to stop service
        self.deployment_manager.execute_service_action(
            self.project_id, service.id, "stop"
        )
        # Check that status is now stopped
        service = self.deployment_manager.get_service_metadata(
            self.project_id, service.id
        )
        assert service.status == DeploymentStatus.STOPPED
        # Stopped service should provide start action but not stop action
        service_action_ids = [
            service.action_id
            for service in self.deployment_manager.list_service_actions(
                self.project_id, service.id
            )
        ]
        assert "start" in service_action_ids
        assert "stop" not in service_action_ids
        # Execute start action to start service again
        self.deployment_manager.execute_service_action(
            self.project_id, service.id, "start"
        )
        # Check that status is now running
        service = self.deployment_manager.get_service_metadata(
            self.project_id, service.id
        )
        assert service.status == DeploymentStatus.RUNNING

    def test_restart_service(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        # Running service should provide restart action
        service_action_ids = [
            service.action_id
            for service in self.deployment_manager.list_service_actions(
                self.project_id, service.id
            )
        ]
        assert service.status == DeploymentStatus.RUNNING
        assert "restart" in service_action_ids
        # Execute restart action
        self.deployment_manager.execute_service_action(
            self.project_id, service.id, "restart"
        )
        # Check that status is now stopped
        restarted_service = self.deployment_manager.get_service_metadata(
            self.project_id, service.id
        )
        # Service should still be running after restart
        assert restarted_service.status == DeploymentStatus.RUNNING
        # Internal id should change after a restart
        assert restarted_service.internal_id != service.internal_id

    def test_delete_services(self) -> None:
        project_1 = f"{self.project_id}-1"
        test_service_input_1 = create_test_service_input(
            display_name=f"{self.service_display_name}-1",
        )
        test_service_input_2 = create_test_service_input(
            display_name=f"{self.service_display_name}-2",
        )
        test_service_input_3 = create_test_service_input(
            display_name=f"{self.service_display_name}-3",
        )

        self.deploy_service(
            project_id=project_1,
            service=test_service_input_1,
        )
        self.deploy_service(
            project_id=project_1,
            service=test_service_input_2,
        )
        self.deploy_service(
            project_id=project_1,
            service=test_service_input_3,
        )

        services = self.deployment_manager.list_services(project_id=project_1)
        assert len(services) == 3

        self.deployment_manager.delete_services(project_id=project_1)
        time.sleep(15)
        services = self.deployment_manager.list_services(project_id=project_1)
        assert len(services) == 0

    def test_delete_jobs(self) -> None:
        project_1 = f"{self.project_id}-1"
        test_job_input_1 = create_test_echo_job_input(
            display_name=f"{self.service_display_name}-1",
        )
        test_job_input_2 = create_test_echo_job_input(
            display_name=f"{self.service_display_name}-2",
        )
        test_job_input_3 = create_test_echo_job_input(
            display_name=f"{self.service_display_name}-3",
        )

        self.deploy_job(
            project_id=project_1,
            job=test_job_input_1,
        )
        self.deploy_job(
            project_id=project_1,
            job=test_job_input_2,
        )
        self.deploy_job(
            project_id=project_1,
            job=test_job_input_3,
        )

        jobs = self.deployment_manager.list_jobs(project_id=project_1)
        assert len(jobs) == 3

        self.deployment_manager.delete_jobs(project_id=project_1)
        time.sleep(10)
        jobs = self.deployment_manager.list_jobs(project_id=project_1)
        assert len(jobs) == 0

    def test_removal_of_system_params(self) -> None:
        user_set_project = "this-should-be-forbidden"
        min_lifetime_via_metadata = 10
        min_lifetime_via_compute_resources = 20
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        test_service_input.compute.min_lifetime = min_lifetime_via_compute_resources
        test_service_input.metadata[Labels.PROJECT_NAME.value] = user_set_project
        test_service_input.metadata[
            Labels.MIN_LIFETIME.value
        ] = min_lifetime_via_metadata

        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )

        assert (
            service.metadata.get(Labels.PROJECT_NAME.value, user_set_project)
            != user_set_project
        )
        assert service.metadata.get(Labels.MIN_LIFETIME.value, None) is None
        assert service.compute.min_lifetime == 20
        assert (
            service.parameters.get("NVIDIA_VISIBLE_DEVICES", "Not allowed to set")
            == "Not allowed to set"
        )

    def test_replacement_of_template_variables(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )

        service = self.deploy_service(
            project_id=self.project_id, service=test_service_input
        )

        assert "BASE_URL" in service.parameters
        assert (
            service.parameters["BASE_URL"]
            == f"/projects/{self.project_id}/services/{service.id}/access/{{endpoint}}"
        )

    def test_get_service_metadata(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )

        queried_service = self.deployment_manager.get_service_metadata(
            project_id=self.project_id, service_id=service.id
        )

        assert queried_service is not None
        assert queried_service.internal_id == service.internal_id
        assert "some-metadata" in queried_service.metadata

        self.deployment_manager.delete_service(
            project_id=self.project_id, service_id=service.id
        )

        with pytest.raises(ResourceNotFoundError):
            self.deployment_manager.get_service_metadata(
                project_id=self.project_id, service_id=service.id
            )

    def test_get_job_metadata(self) -> None:
        job_input = create_test_echo_job_input(display_name=self.service_display_name)
        job = self.deploy_job(project_id=self.project_id, job=job_input)

        queried_job = self.deployment_manager.get_job_metadata(
            project_id=self.project_id, job_id=job.id
        )

        assert queried_job is not None
        assert queried_job.internal_id == job.internal_id
        assert "some-metadata" in queried_job.metadata

        self.deployment_manager.delete_job(project_id=self.project_id, job_id=job.id)

        with pytest.raises(ResourceNotFoundError):
            self.deployment_manager.get_job_metadata(
                project_id=self.project_id, job_id=job.id
            )

    def test_list_services(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        services = self.deployment_manager.list_services(project_id=self.project_id)
        assert len(services) == 1

        self.deployment_manager.delete_service(
            project_id=self.project_id, service_id=service.id
        )
        services = self.deployment_manager.list_services(project_id=self.project_id)
        assert len(services) == 0

    def test_list_jobs(self) -> None:
        test_job_input = create_test_echo_job_input(
            display_name=self.service_display_name
        )
        job = self.deploy_job(project_id=self.project_id, job=test_job_input)
        jobs = self.deployment_manager.list_jobs(project_id=self.project_id)
        assert len(jobs) == 1
        self.deployment_manager.delete_job(project_id=self.project_id, job_id=job.id)
        jobs = self.deployment_manager.list_jobs(project_id=self.project_id)
        assert len(jobs) == 0

    def test_get_logs(self) -> None:
        log_input = "foobar"
        job_input = create_test_echo_job_input(
            display_name=self.service_display_name,
            log_input=log_input,
        )

        job = self.deploy_job(job=job_input, project_id=self.project_id)

        logs = self.deployment_manager.get_job_logs(
            project_id=self.project_id, job_id=job.id
        )
        self.deployment_manager.delete_job(project_id=self.project_id, job_id=job.id)
        assert logs
        assert logs.startswith(log_input)

    def test_list_service_access_actions(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        resource_actions = self.deployment_manager.list_service_actions(
            project_id=self.project_id, service_id=service.id
        )

        assert len(resource_actions) >= 2
        assert f"access-{service.endpoints[0]}" in [
            ra.action_id for ra in resource_actions
        ]
        assert f"access-{service.endpoints[1].replace('/', '')}" in [
            ra.action_id for ra in resource_actions
        ]

    def test_list_deploy_service_actions(self) -> None:
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        resource_actions = self.deployment_manager.list_deploy_service_actions(
            project_id=self.project_id, service=test_service_input
        )
        assert len(resource_actions) == 1
        assert resource_actions[0].action_id == "default"

    def test_list_deploy_job_actions(self) -> None:
        test_job_input = create_test_echo_job_input(
            display_name=self.service_display_name
        )
        resource_actions = self.deployment_manager.list_deploy_job_actions(
            project_id=self.project_id, job=test_job_input
        )
        assert len(resource_actions) == 1
        assert resource_actions[0].action_id == "default"


@pytest.mark.skipif(
    not test_settings.DOCKER_INTEGRATION_TESTS,
    reason="Docker integration tests are disabled",
)
@pytest.mark.integration
class TestDockerDeploymentManager(DeploymentOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        # Only use in memory database as the DB is not main the focus of this test
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        component_manager_mock = ComponentManagerMock(
            global_state, request_state, json_db_manager=json_db
        )
        self._auth_manager = AuthManager(component_manager_mock)
        component_manager_mock.auth_manager = self._auth_manager
        self._system_manager = SystemManager(component_manager_mock)
        component_manager_mock.system_manager = self._system_manager

        self._docker_deployment_manager = DockerDeploymentManager(
            component_manager_mock
        )
        self._deployment_manager = DeploymentManagerWithDB(
            self._docker_deployment_manager, component_manager_mock
        )
        component_manager_mock.deployment_manager = self._deployment_manager

        (
            _,
            self._project_id,
            self._service_display_name,
        ) = get_random_resources()

        yield

        for service_id in self._deployed_services:
            try:
                self._deployment_manager.delete_service(
                    project_id=self._project_id,
                    service_id=service_id,
                    delete_volumes=True,
                )
                # Wait until container is deleted
                while True:
                    try:
                        container = (
                            self._docker_deployment_manager.client.containers.get(
                                service_id
                            )
                        )
                        container.remove(force=True)
                        time.sleep(5)
                    except Exception:
                        break
            except (ResourceNotFoundError, ClientBaseError):
                # service not found
                return

        try:
            network = self._docker_deployment_manager.client.networks.get(
                get_network_name(project_id=self._project_id)
            )
            # only relevant for when the code runs within a container (as then the DockerDeploymentManager behaves slightly different)
            host_container = get_this_container(
                client=self._docker_deployment_manager.client
            )
            if host_container:
                network.disconnect()
                network.remove()
        except Exception:
            pass

    @property
    def deployment_manager(self) -> DeploymentOperations:
        return self._deployment_manager

    @property
    def system_manager(self) -> SystemManager:
        return self._system_manager

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def service_display_name(self) -> str:
        return self._service_display_name

    def test_missing_docker_container(self):
        test_service_input = create_test_service_input(
            display_name=self.service_display_name
        )
        service = self.deploy_service(
            project_id=self.project_id,
            service=test_service_input,
        )
        self._docker_deployment_manager.delete_service(
            self.project_id, service.id, True
        )
        time.sleep(2)
        service = self.deployment_manager.get_service_metadata(
            self.project_id, service.id
        )
        assert service.status == DeploymentStatus.STOPPED

    def test_project_isolation(self) -> None:
        """Test that services of the same project can reach each others' endpoints and services of different projects cannot."""

        def create_wget_command(target_ip: str) -> str:
            return f"wget -T 10 -qO/dev/stdout {target_ip}:80"

        project_1 = f"{self.project_id}-1"
        project_2 = f"{self.project_id}-2"
        test_service_input_1 = create_test_service_input(
            display_name=f"{self.service_display_name}-1",
        )
        test_service_input_2 = create_test_service_input(
            display_name=f"{self.service_display_name}-2",
        )
        test_service_input_3 = create_test_service_input(
            display_name=f"{self.service_display_name}-3",
        )

        service_1 = self.deploy_service(
            project_id=project_1,
            service=test_service_input_1,
        )
        service_2 = self.deploy_service(
            project_id=project_1,
            service=test_service_input_2,
        )
        service_3 = self.deploy_service(
            project_id=project_2,
            service=test_service_input_3,
        )

        container_1 = self._docker_deployment_manager.client.containers.get(
            service_1.id
        )
        container_2 = self._docker_deployment_manager.client.containers.get(
            service_2.id
        )
        container_3 = self._docker_deployment_manager.client.containers.get(
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

        self.deployment_manager.delete_service(
            project_id=project_1, service_id=service_1.id, delete_volumes=True
        )
        self.deployment_manager.delete_service(
            project_id=project_1, service_id=service_2.id, delete_volumes=True
        )
        self.deployment_manager.delete_service(
            project_id=project_2, service_id=service_3.id, delete_volumes=True
        )


@pytest.mark.skipif(
    not test_settings.KUBERNETES_INTEGRATION_TESTS,
    reason="A Kubernetes cluster must be accessible to run the KubeSpawner tests",
)
@pytest.mark.integration
class TestKubernetesDeploymentManager(DeploymentOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        # Only use in memory database as the DB is not main the focus of this test
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        component_manager_mock = ComponentManagerMock(
            global_state, request_state, json_db_manager=json_db
        )
        self._auth_manager = AuthManager(component_manager_mock)
        component_manager_mock.auth_manager = self._auth_manager
        self._system_manager = SystemManager(component_manager_mock)
        component_manager_mock.system_manager = self._system_manager

        (
            uid,
            self._project_id,
            self._service_display_name,
        ) = get_random_resources()
        _kube_namespace = f"{uid}-deployment-manager-test-namespace"

        self._kubernetes_deployment_manager = KubernetesDeploymentManager(
            component_manager_mock, kube_namespace=_kube_namespace
        )
        self._deployment_manager = DeploymentManagerWithDB(
            self._kubernetes_deployment_manager, component_manager_mock
        )
        component_manager_mock.deployment_manager = self._deployment_manager

        self._kubernetes_deployment_manager.core_api.create_namespace(
            V1Namespace(metadata={"name": _kube_namespace})
        )

        yield

        for service_id in self._deployed_services:
            try:
                self._deployment_manager.delete_service(
                    project_id=self._project_id,
                    service_id=service_id,
                    delete_volumes=True,
                )
            except (ResourceNotFoundError, ClientBaseError):
                # service not found
                return

        self._kubernetes_deployment_manager.core_api.delete_namespace(
            _kube_namespace, propagation_policy="Foreground"
        )

        start = time.time()
        timeout = 60
        while time.time() - start < timeout:
            try:
                self._kubernetes_deployment_manager.core_api.read_namespace(
                    name=_kube_namespace
                )
                time.sleep(2)
            except ApiException:
                break

    @property
    def deployment_manager(self) -> DeploymentOperations:
        return self._deployment_manager

    @property
    def system_manager(self) -> SystemManager:
        return self._system_manager

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def service_display_name(self) -> str:
        return self._service_display_name

    def test_project_isolation(self) -> None:
        """Test that services of the same project can reach each others' endpoints and services of different projects cannot."""

        def create_wget_command(target_ip: str) -> str:
            return f"wget -T 10 -qO/dev/stdout {target_ip}:80"

        project_1 = f"{self.project_id}-1"
        project_2 = f"{self.project_id}-2"
        project_core = f"{self.project_id}-core"
        test_service_input_1 = create_test_service_input(
            display_name=f"{self.service_display_name}-1",
        )
        test_service_input_2 = create_test_service_input(
            display_name=f"{self.service_display_name}-2",
        )
        test_service_input_3 = create_test_service_input(
            display_name=f"{self.service_display_name}-3",
        )
        test_service_input_core = create_test_service_input(
            display_name=f"{self.service_display_name}-core",
        )

        service_1 = self.deploy_service(
            project_id=project_1,
            service=test_service_input_1,
        )
        service_2 = self.deploy_service(
            project_id=project_1,
            service=test_service_input_2,
        )
        service_3 = self.deploy_service(
            project_id=project_2,
            service=test_service_input_3,
        )
        service_core = self.deploy_service(
            project_id=project_core, service=test_service_input_core
        )

        namespace = self._kubernetes_deployment_manager.kube_namespace
        pod_1 = self._kubernetes_deployment_manager.core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"ctxy.deploymentName={service_1.id},ctxy.projectName={project_1}",
        ).items[0]

        pod_2 = self._kubernetes_deployment_manager.core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"ctxy.deploymentName={service_2.id},ctxy.projectName={project_1}",
        ).items[0]

        pod_3 = self._kubernetes_deployment_manager.core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"ctxy.deploymentName={service_3.id},ctxy.projectName={project_2}",
        ).items[0]

        pod_core = self._kubernetes_deployment_manager.core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=f"ctxy.deploymentName={service_core.id},ctxy.projectName={project_core}",
        ).items[0]
        # modify the deployment type. Note that it cannot be done during deployment via the Contaxy API due to security reasons.
        pod_core.metadata.labels[
            "ctxy.deploymentType"
        ] = DeploymentType.CORE_BACKEND.value
        self._kubernetes_deployment_manager.core_api.patch_namespaced_pod(
            name=pod_core.metadata.name, namespace=namespace, body=pod_core
        )

        _command_prefix = ["/bin/sh", "-c"]
        output = stream.stream(
            self._kubernetes_deployment_manager.core_api.connect_get_namespaced_pod_exec,
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
            self._kubernetes_deployment_manager.core_api.connect_get_namespaced_pod_exec,
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
            self._kubernetes_deployment_manager.core_api.connect_get_namespaced_pod_exec,
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

        # The core service can reach all services, no matter the project
        output = stream.stream(
            self._kubernetes_deployment_manager.core_api.connect_get_namespaced_pod_exec,
            pod_core.metadata.name,
            namespace,
            command=[
                *_command_prefix,
                create_wget_command(pod_1.status.pod_ip),
            ],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        assert output
        assert "Hello world!" in output

        self.deployment_manager.delete_service(
            project_id=project_1, service_id=service_1.id, delete_volumes=True
        )
        self.deployment_manager.delete_service(
            project_id=project_1, service_id=service_2.id, delete_volumes=True
        )
        self.deployment_manager.delete_service(
            project_id=project_2, service_id=service_3.id, delete_volumes=True
        )
        self.deployment_manager.delete_service(
            project_id=project_core, service_id=service_core.id, delete_volumes=True
        )


class DeploymentOperationsEndpointTests(DeploymentOperationsTests):
    @pytest.fixture(autouse=True)
    def _client(self, remote_client: requests.Session) -> requests.Session:
        if test_settings.REMOTE_BACKEND_TESTS:
            return remote_client
        else:
            from contaxy.api import app

            client = TestClient(app=app, root_path="/")
            client.__enter__()
            return client

    @pytest.fixture(autouse=True)
    def _init_managers(self, _client: requests.Session) -> Generator:
        self._endpoint_client = _client
        self._system_manager = SystemClient(self._endpoint_client)
        self._deployment_manager = DeploymentManagerClient(client=self._endpoint_client)
        self._auth_manager = AuthClient(self._endpoint_client)

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )

        (
            uid,
            self._project_id,
            self._service_display_name,
        ) = get_random_resources()

        yield

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )

        for service_id in self._deployed_services:
            try:
                self._deployment_manager.delete_service(
                    project_id=self._project_id,
                    service_id=service_id,
                    delete_volumes=True,
                )
            except (ResourceNotFoundError, ClientBaseError):
                # service not found
                return

        if type(_client) == TestClient:
            _client.__exit__()

    @property
    def deployment_manager(self) -> DeploymentOperations:
        return self._deployment_manager

    @property
    def system_manager(self) -> SystemManager:
        return self._system_manager

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def service_display_name(self) -> str:
        return self._service_display_name

    def login_user(self, username: str, password: str) -> None:
        self._auth_manager.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=username,
                password=password,
                scope=auth_utils.construct_permission(
                    "*", AccessLevel.ADMIN
                ),  # Get full scope
                set_as_cookie=True,
            )
        )


@pytest.mark.skipif(
    config.settings.DEPLOYMENT_MANAGER != "docker",
    reason="Docker must be set as the deployment manager for DockerLocalEndpoint tests",
)
@pytest.mark.skipif(
    not test_settings.DOCKER_INTEGRATION_TESTS, reason="Docker tests are disabled."
)
@pytest.mark.skipif(
    test_settings.REMOTE_BACKEND_TESTS,
    reason="If remote backend tests are enabled, don't run the local endpoint tests",
)
@pytest.mark.integration
class TestDockerDeploymentManagerViaLocalEndpoint(DeploymentOperationsEndpointTests):
    pass


@pytest.mark.skipif(
    config.settings.DEPLOYMENT_MANAGER != "kubernetes",
    reason="Kubernetes must be set as the deployment manager for KubernetesLocalEndpoint tests",
)
@pytest.mark.skipif(
    not test_settings.KUBERNETES_INTEGRATION_TESTS,
    reason="Kubernetes tests are not enabled",
)
@pytest.mark.skipif(
    test_settings.REMOTE_BACKEND_TESTS,
    reason="If remote backend tests are enabled, don't run the local endpoint tests",
)
@pytest.mark.integration
class TestKubernetesDeploymentManagerViaLocalEndpoint(
    DeploymentOperationsEndpointTests
):
    pass


@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_TESTS,
    reason="Remote Backend Tests are deactivated, use REMOTE_BACKEND_TESTS to activate.",
)
@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_ENDPOINT,
    reason="No remote backend is configured (via REMOTE_BACKEND_ENDPOINT).",
)
@pytest.mark.integration
class TestDeploymentManagerViaRemoteEndpoint(DeploymentOperationsEndpointTests):
    """Test with a remote backend connection.

    There is no need to differentiate between Docker and Kubernetes, because the client executes against a remote backend which uses either of them.
    """

    pass
