from datetime import datetime
from typing import Any, List, Literal, Optional

import docker
import docker.errors

from contaxy.managers.deployment.docker_utils import (
    create_container_config,
    delete_container,
    get_project_container,
    get_project_containers,
    handle_network,
    list_deploy_service_actions,
    map_job,
    map_service,
    read_container_logs,
    reconnect_to_all_networks,
    wait_for_container,
)
from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentType, ServiceUpdate
from contaxy.schema.exceptions import ClientValueError, ServerBaseError


class DockerDeploymentPlatform:
    _is_initialized = False

    def __init__(self) -> None:
        """Initializes the docker deployment manager."""

        self.client = docker.from_env()
        # Reconnect the backend to all existing docker networks on startup
        if not DockerDeploymentPlatform._is_initialized:
            reconnect_to_all_networks(self.client)
            DockerDeploymentPlatform._is_initialized = True

    def list_services(
        self,
        project_id: str,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> List[Service]:
        try:
            containers = get_project_containers(
                client=self.client,
                project_id=project_id,
                deployment_type=deployment_type,
            )

            return [map_service(container) for container in containers]
        except docker.errors.APIError:
            return []

    def deploy_service(
        self,
        project_id: str,
        service: Service,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Service:
        container_config = create_container_config(
            deployment=service,
            project_id=project_id,
        )
        handle_network(client=self.client, project_id=project_id)

        try:
            container = self.client.containers.run(**container_config)
            if wait:
                container = wait_for_container(container, self.client)
        except docker.errors.APIError as e:
            message = f"Could not deploy service '{service.display_name}'."
            if e.status_code == 400:
                raise ClientValueError(
                    message=message, explanation=e.explanation
                ) from e
            raise ServerBaseError(message) from e

        return map_service(container)

    def list_deploy_service_actions(
        self, project_id: str, service: ServiceInput
    ) -> List[ResourceAction]:
        return list_deploy_service_actions(project_id=project_id, deploy_input=service)

    def get_service_metadata(self, project_id: str, service_id: str) -> Service:
        container = get_project_container(
            client=self.client, project_id=project_id, deployment_id=service_id
        )
        return map_service(container)

    def update_service(
        self, project_id: str, service_id: str, service: ServiceUpdate
    ) -> Service:
        # Service update is only implemented on DeploymentManagerWithDB wrapper
        raise NotImplementedError()

    def update_service_access(self, project_id: str, service_id: str) -> None:
        # Service update is only implemented on DeploymentManagerWithDB wrapper
        raise NotImplementedError()

    def delete_service(
        self, project_id: str, service_id: str, delete_volumes: bool = False
    ) -> None:
        container = get_project_container(
            self.client, project_id=project_id, deployment_id=service_id
        )
        delete_container(
            client=self.client, container=container, delete_volumes=delete_volumes
        )

    def delete_services(
        self,
        project_id: str,
    ) -> None:
        containers = get_project_containers(client=self.client, project_id=project_id)
        for container in containers:
            container.remove(v=True, force=True)

    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        container = get_project_container(
            self.client, project_id=project_id, deployment_id=service_id
        )

        return read_container_logs(container=container, lines=lines, since=since)

    def list_jobs(self, project_id: str) -> List[Job]:
        containers = get_project_containers(
            self.client, project_id=project_id, deployment_type=DeploymentType.JOB
        )
        return [map_job(container) for container in containers]

    def deploy_job(
        self,
        project_id: str,
        job: Job,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Job:
        container_config = create_container_config(
            deployment=job,
            project_id=project_id,
        )
        handle_network(client=self.client, project_id=project_id)

        try:
            container = self.client.containers.run(**container_config)
            if wait:
                container = wait_for_container(container, self.client)
        except docker.errors.APIError as e:
            message = f"Could not deploy job '{job.display_name}'."
            if e.status_code == 400:
                raise ClientValueError(
                    message=message, explanation=e.explanation
                ) from e
            raise ServerBaseError(message) from e

        response_service = map_job(container)
        return response_service

    def list_deploy_job_actions(
        self,
        project_id: str,
        job: JobInput,
    ) -> List[ResourceAction]:
        return list_deploy_service_actions(project_id=project_id, deploy_input=job)

    def get_job_metadata(self, project_id: str, job_id: str) -> Job:
        container = get_project_container(
            client=self.client,
            project_id=project_id,
            deployment_id=job_id,
            deployment_type=DeploymentType.JOB,
        )

        return map_job(container)

    def delete_job(self, project_id: str, job_id: str) -> None:
        container = get_project_container(
            self.client,
            project_id=project_id,
            deployment_id=job_id,
            deployment_type=DeploymentType.JOB,
        )
        delete_container(client=self.client, container=container)

    def delete_jobs(
        self,
        project_id: str,
    ) -> None:
        containers = get_project_containers(
            self.client, project_id=project_id, deployment_type=DeploymentType.JOB
        )
        for container in containers:
            container.remove(v=True, force=True)

    def get_job_logs(
        self,
        project_id: str,
        job_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        container = get_project_container(
            self.client,
            project_id=project_id,
            deployment_id=job_id,
            deployment_type=DeploymentType.JOB,
        )

        return read_container_logs(container=container, lines=lines, since=since)

    def suggest_service_config(
        self, project_id: str, container_image: str
    ) -> ServiceInput:
        raise NotImplementedError()

    def list_service_actions(
        self, project_id: str, service_id: str
    ) -> List[ResourceAction]:
        raise NotImplementedError()

    def execute_service_action(
        self, project_id: str, service_id: str, action_id: str
    ) -> Any:
        raise NotImplementedError()

    def suggest_job_config(self, project_id: str, container_image: str) -> JobInput:
        raise NotImplementedError()

    def list_job_actions(self, project_id: str, job_id: str) -> List[ResourceAction]:
        raise NotImplementedError()

    def execute_job_action(self, project_id: str, job_id: str, action_id: str) -> Any:
        raise NotImplementedError()
