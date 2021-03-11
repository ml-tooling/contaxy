from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from ... import data_model
from .utils import DEFAULT_DEPLOYMENT_ACTION_ID


class ServiceDeploymentManager(ABC):
    @abstractmethod
    def list_services(self, project_id: str) -> List[data_model.Service]:
        """List the services that belong to the given project id.

        Classes that implement this function must also consider the namespace of the running instance.

        Args:
            project_id (str): Unique id of a project for which the services should be listed.

        Raises:
            NotImplementedError: Must be implemented by the specific DeploymentManagers

        Returns:
            List[data_model.Service]: List of found services belonging to the project or an empty list.
        """
        raise NotImplementedError

    def suggest_service_config(self, project_id: str, container_image: str) -> Any:
        """Manager independent."""
        raise NotImplementedError

    @abstractmethod
    def get_service_metadata(self, service_id: str) -> Any:
        raise NotImplementedError

    # TODO: project_id removed - is it really needed here?
    def list_service_deploy_actions(self, service: data_model.ServiceInput) -> Any:
        return [
            data_model.ResourceAction(
                action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
                display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
            )
        ]

    @abstractmethod
    def deploy_service(
        self, service: data_model.ServiceInput, project_id: str
    ) -> data_model.Service:
        """Deploy a service using the DeploymentManager activated by the system.

        Args:
            service (data_model.ServiceInput): The ServiceInput object that contains the service settings.
            project_id (str): Unique id of the project in which the service should be deployed.

        Raises:
            NotImplementedError: When the manager does not implement the function.
            DeploymentError: When an error occurs during the deployment process.

        Returns:
            data_model.Service: If the deployment was successful, the information about the service is returned. It is similar to the passed ServiceInput but might contain runtime information.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_service(self, service_id: str) -> None:
        """Delete the service with the given service id.

        Args:
            service_id (str): The service id uniquely identifying the service in the system.

        Raises:
            NotImplementedError
            RuntimeError: If an error occurs during the deletion of the service.
        """
        raise NotImplementedError

    @abstractmethod
    def get_service_logs(
        self,
        service_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        """Read the logs of the service.

        Args:
            service_id (str): Unique service id.
            lines (Optional[int], optional): If provided, just the last X lines are returned from the log. Defaults to None.
            since (Optional[datetime], optional): If provided, just the logs since the given timestamp are returned. Defaults to None.

        Raises:
            NotImplementedError: [description]
            RuntimeError: If reading the logs of the given service fails.

        Returns:
            str: The logs of the service.
        """
        raise NotImplementedError

    def get_service_token(
        self, project_id: str, service_id: str, extension_id: str, token_type: Any
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> Any:
        """Call regularly to perform landscape cleanups such as remove unused networks etc."""
        raise NotImplementedError

    def list_service_actions(self, project_id: str, service_id: str) -> Any:
        """Manager independent."""
        return []

    def execute_service_action(self, project_id: str, service_id: str) -> Any:
        """Manager independent."""
        raise ValueError("Action not supported")


class JobDeploymentManager(ABC):
    @abstractmethod
    def list_jobs(self, project_id: str) -> List[data_model.Job]:
        """Return a list of Jobs belonging to the project with the given project id.

        Args:
            project_id (str): Unique id of the project.

        Raises:
            NotImplementedError

        Returns:
            List[data_model.Job]: List of found jobs belonging to the project or empty list.
        """
        raise NotImplementedError

    def get_job_metadata(self, job_id: str) -> Any:
        raise NotImplementedError

    def suggest_job_config(self, project_id: str, container_image: str) -> Any:
        """Manager independent."""
        raise NotImplementedError

    @abstractmethod
    def list_job_deploy_actions(self, job_input: data_model.JobInput) -> Any:
        raise NotImplementedError

    @abstractmethod
    def deploy_job(self, job: data_model.Job, project_id: str) -> data_model.Job:
        """Deploy a service using the DeploymentManager activated by the system.

        Args:
            job (data_model.Job): The configuration of the job to be deployed.
            project_id (str): The id of the project to which the job will belong.

        Raises:
            NotImplementedError
            DeploymentError: When an error occurs during the deployment process.

        Returns:
            data_model.Job: If the deployment was successful, the information about the job is returned. It is similar to the passed JobInput but might contain runtime information.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_job(self, job_id: str) -> None:
        """Deletes the job with the given id.

        Args:
            job_id (str): The id of the job to be deleted.

        Raises:
            NotImplementedError
            RuntimeError: If an error occurs during the deletion process.

        """
        raise NotImplementedError

    @abstractmethod
    def get_job_logs(
        self, job_id: str, lines: Optional[int] = None, since: Optional[datetime] = None
    ) -> Any:
        raise NotImplementedError
