from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Literal, Optional

from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentType, ServiceUpdate
from contaxy.schema.shared import ResourceActionExecution


class ServiceOperations(ABC):
    @abstractmethod
    def list_services(
        self,
        project_id: str,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> List[Service]:
        """Lists all services associated with the given project.

        Args:
            project_id (str): The project ID to filter the services.
            deployment_type (One of [DeploymentType.SERVICE, DeploymentType.JOB]): The deployment type of either Service or Extension (which is a subtype of Service).

        Returns:
            List[Service]: The list of services associated with the project.
        """
        pass

    @abstractmethod
    def deploy_service(
        self,
        project_id: str,
        service_input: ServiceInput,
        action_id: Optional[str] = None,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
        wait: bool = False,
    ) -> Service:
        """Deploys a service for the specified project.

        If no `action_id` is provided, the system will automatically select the best deployment option.

        Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
        If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

        The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions).

        Args:
            project_id (str): The id of the project that the service should be assigned to.
            service_input (ServiceInput): The service input which can be used to configure the deployed service.
            action_id (Optional[str], optional): The ID of the selected action. Defaults to `None`.
            deployment_type (One of [DeploymentType.SERVICE, DeploymentType.JOB]): The deployment type of either Service or Extension (which is a subtype of Service).
            wait (bool, optional): If set to True, the function will wait until the service was successfully created.

        Returns:
            Service: The metadata of the deployed service.
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
    def update_service(
        self, project_id: str, service_id: str, service_update: ServiceUpdate
    ) -> Service:
        """Updates the service.

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.
            service_update (ServiceUpdate): Updates that should be applied to the service
        Returns:
            Service: The updated service metadata
        """
        pass

    @abstractmethod
    def update_service_access(self, project_id: str, service_id: str) -> None:
        """Updates the last time the service was accessed and by which user.

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.
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
    def delete_services(
        self,
        project_id: str,
    ) -> None:
        """Deletes all services associated with a project.

        Args:
            project_id (str): The project ID.
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
        """Suggests an input configuration based on the provided `container_image`.

        The suggestion is based on metadata extracted from the container image (e.g. labels)
        as well as suggestions based on previous project deployments with the same image.

        Args:
            project_id (str): The project ID associated with the service.
            container_image (str): The container image to use as context for the suggestion.

        Returns:
            ServiceInput: The suggested service configuration.
        """
        pass

    @abstractmethod
    def list_service_actions(
        self,
        project_id: str,
        service_id: str,
    ) -> List[ResourceAction]:
        """Lists all actions available for the specified service.

        See the endpoint documentation for more information on the action mechanism.

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.

        Returns:
            List[ResourceAction]: Available actions for given services.
        """
        pass

    @abstractmethod
    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
        action_execution: ResourceActionExecution = ResourceActionExecution(),
    ) -> Any:
        """Executes the selected service action.

        The actions need to be first requested from the list_service_actions operation.
        If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

        Args:
            project_id (str): The project ID associated with the service.
            service_id (str): The ID of the service.
            action_id (str): The ID of the selected action.
            action_execution (ResourceActionExecution): The action execution request which contains the action parameters

        Returns:
            `None` or a redirect response to another URL.
        """
        pass


class JobOperations(ABC):
    @abstractmethod
    def list_jobs(self, project_id: str) -> List[Job]:
        pass

    @abstractmethod
    def deploy_job(
        self,
        project_id: str,
        job_input: JobInput,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Job:
        pass

    @abstractmethod
    def list_deploy_job_actions(
        self,
        project_id: str,
        job: JobInput,
    ) -> List[ResourceAction]:
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
    def delete_jobs(
        self,
        project_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> None:
        """Delete all files and storage resources related to a project.

        Args:
            project_id (str): Project ID associated with the files.
            date_from (Optional[datetime], optional): The start date to delete the files. If not specified, all files will be deleted.
            date_to (Optional[datetime], optional): The end date to delete the files. If not specified, all files will be deleted.
        """
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
    ) -> List[ResourceAction]:
        pass

    @abstractmethod
    def execute_job_action(
        self,
        project_id: str,
        job_id: str,
        action_id: str,
        action_execution: ResourceActionExecution = ResourceActionExecution(),
    ) -> Any:
        pass


class DeploymentOperations(ServiceOperations, JobOperations, ABC):
    pass
