from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from ... import data_model
from .utils import DEFAULT_DEPLOYMENT_ACTION_ID


class ServiceDeploymentManager(ABC):
    @abstractmethod
    def list_services(self, project_id: str) -> Any:
        raise NotImplementedError

    def suggest_service_config(self, project_id: str, container_image: str) -> Any:
        """Manager independent"""
        raise NotImplementedError

    @abstractmethod
    def get_service_metadata(self, service_id: str) -> Any:
        raise NotImplementedError

    # TODO: project_id removed - is it really needed here?
    def list_service_deploy_actions(self, service: data_model.ServiceInput) -> Any:
        # TODO: check whether service can theoretically be deployed (at least a node with the required resources exists)
        # return ResourceAction (with id and display_name: "Deploy on KubeCore")

        return [
            data_model.ResourceAction(
                action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
                display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
            )
        ]

    @abstractmethod
    def deploy_service(self, service: data_model.ServiceInput, project_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def delete_service(self, service_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_service_logs(self, service_id: str, lines: Optional[int] = None) -> Any:
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
        """Manager independent"""
        return []

    def execute_service_action(self, project_id: str, service_id: str) -> Any:
        """Manager independent"""
        raise ValueError("Action not supported")

    def hello(self) -> str:
        return "hello"


class JobDeploymentManager(ABC):
    @abstractmethod
    def list_jobs(self, project_id: str) -> Any:
        raise NotImplementedError

    def get_job_metadata(self, job_id: str):
        raise NotImplementedError

    def suggest_job_config(self, project_id: str, container_image: str) -> Any:
        """manager Independent"""
        raise NotImplementedError

    @abstractmethod
    def list_job_deploy_actions(self, service: data_model.JobInput) -> Any:
        raise NotImplementedError

    @abstractmethod
    def deploy_job(self, job: data_model.Job, project_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def delete_job(self, job_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_job_logs(
        self, job_id: str, lines: Optional[int] = None, since: Optional[datetime] = None
    ) -> Any:
        raise NotImplementedError
