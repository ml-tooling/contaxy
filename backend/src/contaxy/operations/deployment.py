from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from starlette.responses import Response

from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput


class ServiceOperations(ABC):
    @abstractmethod
    def list_services(
        self,
        project_id: str,
    ) -> List[Service]:
        """Lists all services associated with the given project.

        Args:
            project_id (str): The project ID to filter the services.

        Returns:
            List[Service]: The list of services associated with the project.
        """
        pass

    @abstractmethod
    def deploy_service(
        self,
        project_id: str,
        service: ServiceInput,
        action_id: Optional[str] = None,
    ) -> Service:
        """Deploys a service for the specified project.

        If no `action_id` is provided, the system will automatically select the best deployment option.

        Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
        If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

        The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions).

        Args:
            project_id (str): [description]
            service (ServiceInput): [description]
            action_id (Optional[str], optional): [description]. Defaults to None.

        Returns:
            Service: [description]
        """
        pass

    @abstractmethod
    def list_deploy_service_actions(
        self,
        project_id: str,
        service: ServiceInput,
    ) -> List[ResourceAction]:
        """Lists all available service deployment options (actions).

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.

        Returns:
            List[ResourceAction]: Available deployment actions.
        """
        pass

    @abstractmethod
    def get_service_metadata(
        self,
        project_id: str,
        service_id: str,
    ) -> Service:
        """Returns the metadata of a single service.

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.

        Returns:
            Service: The service metadata.
        """
        pass

    @abstractmethod
    def delete_service(
        self,
        project_id: str,
        service_id: str,
        delete_volumes: bool = False,
    ) -> None:
        """Deletes a service.

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.
            delete_volumes (bool, optional): If `True`, all attached volumes will be deleted. Defaults to `False`.

        Raises:
            RuntimeError: If an error occurs during the deletion of the service.
        """
        pass

    @abstractmethod
    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int],
        since: Optional[datetime],
    ) -> str:
        """Returns the logs of a service.

        Args:
            project_id (str): The ID of the project into which the service is deployed in.
            service_id (str): The ID of the service.
            lines (Optional[int]): If provided, just the last `n` lines are returned from the log. Defaults to `None`.
            since (Optional[datetime]): If provided, just the logs since the given timestamp are returned. Defaults to `None`.

        Raises:
            NotImplementedError: [description]
            RuntimeError: If reading the logs of the given service fails.

        Returns:
            str: The logs of the service.
        """
        pass

    @abstractmethod
    def suggest_service_config(
        self,
        project_id: str,
        container_image: str,
    ) -> ServiceInput:
        """[summary]

        Args:
            project_id (str): [description]
            container_image (str): [description]

        Returns:
            ServiceInput: [description]
        """
        pass

    @abstractmethod
    def list_service_actions(
        self,
        project_id: str,
        service_id: str,
        extension_id: Optional[str],
    ) -> ResourceAction:
        """[summary]

        Args:
            project_id (str): [description]
            service_id (str): [description]
            extension_id (Optional[str]): [description]

        Returns:
            ResourceAction: [description]
        """
        pass

    @abstractmethod
    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
    ) -> Response:
        """[summary]

        Args:
            project_id (str): [description]
            service_id (str): [description]
            action_id (str): [description]

        Returns:
            Response: [description]
        """
        pass

    @abstractmethod
    def access_service(
        self,
        project_id: str,
        service_id: str,
        endpoint: str,
    ) -> Response:
        """[summary]

        Args:
            project_id (str): [description]
            service_id (str): [description]
            endpoint (str): [description]

        Returns:
            Response: [description]
        """
        pass


class JobOperations(ABC):
    @abstractmethod
    def list_jobs(self, project_id: str) -> Job:
        pass

    @abstractmethod
    def deploy_job(
        self,
        project_id: str,
        job: JobInput,
        action_id: Optional[str] = None,
    ) -> Job:
        pass

    @abstractmethod
    def list_deploy_job_actions(
        self,
        project_id: str,
        job: JobInput,
    ) -> ResourceAction:
        pass

    @abstractmethod
    def suggest_job_config(self, project_id: str, container_image: str) -> JobInput:
        pass

    @abstractmethod
    def get_job_metadata(self, project_id: str, job_id: str) -> Job:
        pass

    @abstractmethod
    def delete_job(self, project_id: str, job_id: str) -> None:
        pass

    @abstractmethod
    def get_job_logs(
        self,
        project_id: str,
        job_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        pass

    @abstractmethod
    def list_job_actions(
        self,
        project_id: str,
        job_id: str,
    ) -> ResourceAction:
        pass

    @abstractmethod
    def execute_job_action(
        self, project_id: str, job_id: str, action_id: str
    ) -> Response:
        pass


class DeploymentOperations(ServiceOperations, JobOperations, ABC):
    pass
