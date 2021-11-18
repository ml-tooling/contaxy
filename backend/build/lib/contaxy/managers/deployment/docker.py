from datetime import datetime
from typing import List, Literal, Optional

import docker
from loguru import logger

from contaxy.managers.auth import AuthManager
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
)
from contaxy.managers.deployment.manager import DeploymentManager
from contaxy.managers.deployment.utils import Labels, split_image_name_and_tag
from contaxy.managers.system import SystemManager
from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentType
from contaxy.schema.exceptions import ClientBaseError, ClientValueError
from contaxy.utils.auth_utils import parse_userid_from_resource_name
from contaxy.utils.state_utils import GlobalState, RequestState


class DockerDeploymentManager(DeploymentManager):
    _is_initialized = False

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        system_manager: SystemManager,
        auth_manager: AuthManager,
    ):
        """Initializes the docker deployment manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            system_manager: The system manager used for getting the list of allowed images.
            auth_manager: The auth manager is used to generate api tokens that a passed to services and jobs.
        """
        self.global_state = global_state
        self.request_state = request_state
        self._system_manager = system_manager
        self._auth_manager = auth_manager

        self.client = docker.from_env()
        # Reconnect the backend to all existing docker networks on startup
        if not DockerDeploymentManager._is_initialized:
            reconnect_to_all_networks(self.client)
            DockerDeploymentManager._is_initialized = True

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
        service: ServiceInput,
        action_id: Optional[str] = None,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> Service:
        image_name, image_tag = split_image_name_and_tag(service.container_image)
        self._system_manager.check_image(image_name, image_tag)
        container_config = create_container_config(
            service=service,
            project_id=project_id,
            auth_manager=self._auth_manager,
            user_id=parse_userid_from_resource_name(
                self.request_state.authorized_subject
            ),
        )
        container_config["labels"][Labels.DEPLOYMENT_TYPE.value] = deployment_type.value
        handle_network(client=self.client, project_id=project_id)

        try:
            container = self.client.containers.run(**container_config)
        except docker.errors.APIError as e:
            logger.error(f"Error in deploy service '{service.display_name}': {e}")
            raise ClientValueError(
                f"Could not deploy service '{service.display_name}'."
            )

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

    def delete_service(
        self, project_id: str, service_id: str, delete_volumes: bool = False
    ) -> None:
        container = get_project_container(
            self.client, project_id=project_id, deployment_id=service_id
        )
        delete_container(container=container, delete_volumes=delete_volumes)

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
        job: JobInput,
        action_id: Optional[str] = None,
    ) -> Job:
        image_name, image_tag = split_image_name_and_tag(job.container_image)
        self._system_manager.check_image(image_name, image_tag)
        container_config = create_container_config(
            service=job,
            project_id=project_id,
            auth_manager=self._auth_manager,
            user_id=parse_userid_from_resource_name(
                self.request_state.authorized_subject
            ),
        )
        container_config["labels"][
            Labels.DEPLOYMENT_TYPE.value
        ] = DeploymentType.JOB.value
        handle_network(client=self.client, project_id=project_id)

        try:
            container = self.client.containers.run(**container_config)
        except docker.errors.APIError:
            raise ClientBaseError(
                status_code=500, message=f"Could not deploy job '{job.display_name}'."
            )

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
        delete_container(container=container)

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
