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
        pass

    @abstractmethod
    def deploy_service(
        self,
        project_id: str,
        service: ServiceInput,
        action_id: Optional[str] = None,
    ) -> Service:
        pass

    @abstractmethod
    def list_deploy_service_actions(
        self,
        project_id: str,
        service: ServiceInput,
    ) -> ResourceAction:
        pass

    @abstractmethod
    def get_service_metadata(
        self,
        project_id: str,
        service_id: str,
    ) -> Service:
        pass

    @abstractmethod
    def delete_service(
        self,
        project_id: str,
        service_id: str,
        delete_volumes: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int],
        since: Optional[datetime],
    ) -> str:
        pass

    @abstractmethod
    def suggest_service_config(
        self,
        project_id: str,
        container_image: str,
    ) -> ServiceInput:
        pass

    @abstractmethod
    def list_service_actions(
        self,
        project_id: str,
        service_id: str,
        extension_id: Optional[str],
    ) -> ResourceAction:
        pass

    @abstractmethod
    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
    ) -> Response:
        pass

    @abstractmethod
    def access_service(
        self,
        project_id: str,
        service_id: str,
        endpoint: str,
    ) -> Response:
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
