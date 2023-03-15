from datetime import datetime
from typing import Dict, List, Literal, Optional

import requests
from pydantic.tools import parse_raw_as

from contaxy.clients.shared import handle_errors
from contaxy.operations.deployment import DeploymentOperations
from contaxy.schema import Job, JobInput, ResourceAction, Service, ServiceInput
from contaxy.schema.deployment import DeploymentType, ServiceUpdate
from contaxy.schema.shared import ResourceActionExecution


class DeploymentClient(DeploymentOperations):
    def __init__(self, client: requests.Session):
        self._client = client

    @property
    def client(self) -> requests.Session:
        return self._client

    def list_services(
        self,
        project_id: str,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
        request_kwargs: Dict = {},
    ) -> List[Service]:
        response = self.client.get(f"/projects/{project_id}/services", **request_kwargs)
        if deployment_type == DeploymentType.EXTENSION:
            raise ValueError("Use the ExtensionManager to list extensions!")
        handle_errors(response)
        return parse_raw_as(List[Service], response.text)

    def deploy_service(
        self,
        project_id: str,
        service_input: ServiceInput,
        action_id: Optional[str] = None,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
        wait: bool = False,
        request_kwargs: Dict = {},
    ) -> Service:
        params = {}
        if wait:
            params["wait"] = "true"
        if action_id:
            params["action_id"] = action_id
        if deployment_type == DeploymentType.EXTENSION:
            raise ValueError("Use the ExtensionManager to deploy extensions!")

        resource = self.client.post(
            f"/projects/{project_id}/services",
            params=params,
            data=service_input.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(Service, resource.text)

    def update_service(
        self,
        project_id: str,
        service_id: str,
        service_update: ServiceUpdate,
        request_kwargs: Dict = {},
    ) -> Service:
        resource = self.client.patch(
            f"/projects/{project_id}/services/{service_id}",
            data=service_update.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(Service, resource.text)

    def update_service_access(
        self,
        project_id: str,
        service_id: str,
        request_kwargs: Dict = {},
    ) -> None:
        resource = self.client.post(
            f"/projects/{project_id}/services/{service_id}:update-service-access",
            **request_kwargs,
        )
        handle_errors(resource)

    def list_deploy_service_actions(
        self,
        project_id: str,
        service: ServiceInput,
        request_kwargs: Dict = {},
    ) -> List[ResourceAction]:
        resources = self.client.post(
            f"/projects/{project_id}/services:deploy-actions",
            data=service.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resources)
        return parse_raw_as(List[ResourceAction], resources.text)

    def get_service_metadata(
        self,
        project_id: str,
        service_id: str,
        request_kwargs: Dict = {},
    ) -> Service:
        resource = self.client.get(
            f"/projects/{project_id}/services/{service_id}", **request_kwargs
        )
        handle_errors(resource)
        return parse_raw_as(Service, resource.text)

    def delete_service(
        self,
        project_id: str,
        service_id: str,
        delete_volumes: bool = False,
        request_kwargs: Dict = {},
    ) -> None:
        response = self.client.delete(
            f"/projects/{project_id}/services/{service_id}",
            params={"delete_volumes": delete_volumes},
            **request_kwargs,
        )
        handle_errors(response)

    def delete_services(
        self,
        project_id: str,
        request_kwargs: Dict = {},
    ) -> None:
        response = self.client.delete(
            f"/projects/{project_id}/services",
            **request_kwargs,
        )
        handle_errors(response)

    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int],
        since: Optional[datetime],
        request_kwargs: Dict = {},
    ) -> str:
        params = {}
        if lines:
            params["lines"] = str(lines)
        if since:
            params["since"] = since.__str__()
        response = self.client.get(
            f"/projects/{project_id}/services/{service_id}/logs",
            params=params,
            **request_kwargs,
        )
        handle_errors(response)
        return response.json()

    def suggest_service_config(
        self,
        project_id: str,
        container_image: str,
        request_kwargs: Dict = {},
    ) -> ServiceInput:
        resource = self.client.get(
            f"/projects/{project_id}/services:suggest-config",
            params={"container_image": container_image},
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(ServiceInput, resource.text)

    def list_service_actions(
        self,
        project_id: str,
        service_id: str,
        request_kwargs: Dict = {},
    ) -> List[ResourceAction]:
        resources = self.client.get(
            f"/projects/{project_id}/services/{service_id}/actions", **request_kwargs
        )
        handle_errors(resources)
        return parse_raw_as(List[ResourceAction], resources.text)

    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
        action_execution: ResourceActionExecution = ResourceActionExecution(),
        request_kwargs: Dict = {},
    ) -> None:
        response = self.client.post(
            f"/projects/{project_id}/services/{service_id}/actions/{action_id}",
            data=action_execution.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(response)
        # TODO: Return response?

    def access_service(
        self,
        project_id: str,
        service_id: str,
        endpoint: str,
        request_kwargs: Dict = {},
    ) -> None:
        response = self.client.get(
            f"/projects/{project_id}/services/{service_id}/access/{endpoint}",
            **request_kwargs,
        )
        handle_errors(response)
        # TODO: Return response?

    def list_jobs(
        self,
        project_id: str,
        request_kwargs: Dict = {},
    ) -> List[Job]:
        resources = self.client.get(f"/projects/{project_id}/jobs", **request_kwargs)
        handle_errors(resources)
        return parse_raw_as(List[Job], resources.text)

    def deploy_job(
        self,
        project_id: str,
        job_input: JobInput,
        action_id: Optional[str] = None,
        wait: bool = False,
        request_kwargs: Dict = {},
    ) -> Job:
        params = {}
        if wait:
            params["wait"] = "true"
        if action_id:
            params["action_id"] = action_id
        resource = self.client.post(
            f"/projects/{project_id}/jobs",
            params=params,
            data=job_input.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(Job, resource.text)

    def list_deploy_job_actions(
        self,
        project_id: str,
        job: JobInput,
        request_kwargs: Dict = {},
    ) -> List[ResourceAction]:
        resources = self.client.post(
            f"/projects/{project_id}/jobs:deploy-actions",
            data=job.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resources)
        return parse_raw_as(List[ResourceAction], resources.text)

    def suggest_job_config(
        self,
        project_id: str,
        container_image: str,
        request_kwargs: Dict = {},
    ) -> JobInput:
        resource = self.client.get(
            f"/projects/{project_id}/jobs:suggest-config",
            params={"container_image": container_image},
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(JobInput, resource.text)

    def get_job_metadata(
        self,
        project_id: str,
        job_id: str,
        request_kwargs: Dict = {},
    ) -> Job:
        resource = self.client.get(
            f"/projects/{project_id}/jobs/{job_id}", **request_kwargs
        )
        handle_errors(resource)
        return parse_raw_as(Job, resource.text)

    def delete_job(
        self,
        project_id: str,
        job_id: str,
        request_kwargs: Dict = {},
    ) -> None:
        response = self.client.delete(
            f"/projects/{project_id}/jobs/{job_id}",
            **request_kwargs,
        )
        handle_errors(response)

    def delete_jobs(
        self,
        project_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        request_kwargs: Dict = {},
    ) -> None:
        query_params: Dict = {"date_from": date_from, "date_to": date_to}
        response = self.client.delete(
            f"/projects/{project_id}/jobs",
            params=query_params,
            **request_kwargs,
        )
        handle_errors(response)

    def get_job_logs(
        self,
        project_id: str,
        job_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
        request_kwargs: Dict = {},
    ) -> str:
        params = {}
        if lines:
            params["lines"] = str(lines)
        if since:
            params["since"] = since.__str__()
        response = self.client.get(
            f"/projects/{project_id}/jobs/{job_id}/logs",
            params=params,
            **request_kwargs,
        )
        handle_errors(response)
        return response.json()

    def list_job_actions(
        self,
        project_id: str,
        job_id: str,
        request_kwargs: Dict = {},
    ) -> List[ResourceAction]:
        resources = self.client.get(
            f"/projects/{project_id}/jobs/{job_id}/actions", **request_kwargs
        )
        handle_errors(resources)
        return parse_raw_as(List[ResourceAction], resources.text)

    def execute_job_action(
        self,
        project_id: str,
        job_id: str,
        action_id: str,
        action_execution: ResourceActionExecution = ResourceActionExecution(),
        request_kwargs: Dict = {},
    ) -> None:
        response = self.client.post(
            f"/projects/{project_id}/jobs/{job_id}/actions/{action_id}",
            **request_kwargs,
            data=action_execution.json(exclude_unset=True),
        )
        handle_errors(response)
        # TODO: Return response?
