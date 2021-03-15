from datetime import datetime
from typing import List, Optional

import docker
import psutil

from contaxy.config import settings
from contaxy.managers.deployment.docker_utils import (
    check_minimal_resources,
    create_container_config,
    extract_minimal_resources,
    handle_network,
    transform_job,
    transform_service,
)
from contaxy.managers.deployment.utils import (
    DEFAULT_DEPLOYMENT_ACTION_ID,
    NO_LOGS_MESSAGE,
    Labels,
    get_gpu_info,
    get_label_string,
)
from contaxy.operations import DeploymentOperations
from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentCompute, DeploymentType
from contaxy.utils.state_utils import GlobalState, RequestState


class DockerDeploymentManager(DeploymentOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the docker deployment manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self.global_state = global_state
        self.request_state = request_state

        self.client = docker.from_env()
        self.system_cpu_count = psutil.cpu_count()
        self.system_memory_in_mb = round(psutil.virtual_memory().total / 1024 / 1024, 1)
        self.system_gpu_count = get_gpu_info()

    def list_services(self, project_id: str) -> List[Service]:
        try:
            containers = self.client.containers.list(
                filters={
                    "label": [
                        get_label_string(
                            Labels.NAMESPACE.value, settings.SYSTEM_NAMESPACE
                        ),
                        get_label_string(Labels.PROJECT_NAME.value, project_id),
                        get_label_string(
                            Labels.DEPLOYMENT_TYPE.value,
                            DeploymentType.SERVICE.value,
                        ),
                    ]
                }
            )

            return [transform_service(container) for container in containers]
        except docker.errors.APIError:
            return []

    def deploy_service(
        self,
        project_id: str,
        service: ServiceInput,
        action_id: Optional[str] = None,
    ) -> Service:
        container_config = create_container_config(
            service=service, project_id=project_id
        )
        container_config["labels"][
            Labels.DEPLOYMENT_TYPE.value
        ] = DeploymentType.SERVICE.value
        handle_network(project_id=project_id)

        try:
            container = self.client.containers.run(**container_config)
        except docker.errors.APIError:
            raise RuntimeError(f"Could not deploy service '{service.display_name}'.")

        return transform_service(container)

    def list_deploy_service_actions(
        self, project_id: str, service: ServiceInput
    ) -> List[ResourceAction]:
        compute_resources = service.compute or DeploymentCompute()
        min_cpus, min_memory, min_gpus = extract_minimal_resources(compute_resources)
        try:
            check_minimal_resources(
                min_cpus=min_cpus, min_memory=min_memory, min_gpus=min_gpus
            )
        except RuntimeError:
            return []

        return [
            ResourceAction(
                action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
                display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
            )
        ]

    def get_service_metadata(self, project_id: str, service_id: str) -> Service:
        try:
            container = self.client.containers.get(service_id)
        except docker.errors.NotFound:
            raise RuntimeError(f"Could not get metadata of service '{service_id}'.")

        return transform_service(container)

    def delete_service(
        self, project_id: str, service_id: str, delete_volumes: bool = False
    ) -> None:
        try:
            container = self.client.containers.get(service_id)
        except docker.errors.NotFound:
            raise RuntimeError(f"Could not find service '{service_id}' to delete.")

        try:
            container.stop()
        except docker.errors.APIError:
            pass

        try:
            container.remove(v=delete_volumes)
        except docker.errors.APIError:
            raise RuntimeError(f"Could not delete service {service_id}")

    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        try:
            container = self.client.containers.get(service_id)
        except docker.errors.NotFound:
            raise RuntimeError(
                f"Could not find service {service_id} to read logs from."
            )

        try:
            logs = container.logs(tail=lines or "all", since=since)
        except docker.errors.APIError:
            raise RuntimeError(f"Could not read logs of service {service_id}.")

        if logs:
            logs = logs.decode("utf-8")
        else:
            logs = NO_LOGS_MESSAGE

        return logs

    def list_jobs(self, project_id: str) -> Job:
        containers = self.client.containers.list(
            filters={
                "label": [
                    get_label_string(Labels.NAMESPACE.value, settings.SYSTEM_NAMESPACE),
                    get_label_string(Labels.PROJECT_NAME.value, project_id),
                    get_label_string(
                        Labels.DEPLOYMENT_TYPE.value,
                        DeploymentType.JOB.value,
                    ),
                ]
            }
        )
        return [transform_service(container) for container in containers]

    def deploy_job(
        self,
        project_id: str,
        job: JobInput,
        action_id: Optional[str] = None,
    ) -> Job:
        container_config = self.create_container_config(
            service=job, project_id=project_id
        )
        container_config["labels"][
            Labels.DEPLOYMENT_TYPE.value
        ] = DeploymentType.JOB.value
        self.handle_network(project_id=project_id)

        try:
            container = self.client.containers.run(**container_config)
        except docker.errrors.APIError:
            raise RuntimeError(f"Could not deploy job '{job.display_name}'.")

        response_service = transform_job(container)
        return response_service

    def list_deploy_job_actions(
        self,
        project_id: str,
        job: JobInput,
    ) -> List[ResourceAction]:
        return self.list_service_deploy_actions(project_id=project_id, service=job)

    def get_job_metadata(self, project_id: str, job_id: str) -> Job:
        return self.get_service_metadata(project_id=project_id, service_id=job_id)

    def delete_job(self, project_id: str, job_id: str) -> None:
        return self.delete_service(
            project_id=project_id, service_id=job_id, delete_volumes=True
        )

    def get_job_logs(
        self,
        project_id: str,
        job_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        return self.get_service_logs(
            project_id=project_id, service_id=job_id, lines=lines, since=since
        )
