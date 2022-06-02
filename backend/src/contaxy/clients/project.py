from typing import Dict, List

import requests
from pydantic import parse_raw_as

from contaxy.clients.shared import handle_errors
from contaxy.operations import ProjectOperations
from contaxy.schema import AccessLevel, Project, ProjectCreation, ProjectInput
from contaxy.schema.auth import UserPermission


class ProjectClient(ProjectOperations):
    def __init__(self, client: requests.Session):
        self._client = client

    def list_projects(
        self,
        request_kwargs: Dict = {},
    ) -> List[Project]:
        response = self._client.get("/projects", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[Project], response.text)

    def create_project(
        self,
        project_input: ProjectCreation,
        technical_project: bool = False,
        request_kwargs: Dict = {},
    ) -> Project:
        resource = self._client.post(
            "/projects",
            params={"technical_project": technical_project},
            data=project_input.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(Project, resource.text)

    def get_project(self, project_id: str, request_kwargs: Dict = {}) -> Project:
        resource = self._client.get(f"/projects/{project_id}", **request_kwargs)
        handle_errors(resource)
        return parse_raw_as(Project, resource.text)

    def update_project(
        self, project_id: str, project_input: ProjectInput, request_kwargs: Dict = {}
    ) -> Project:
        response = self._client.patch(
            f"/projects/{project_id}",
            data=project_input.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(Project, response.text)

    def suggest_project_id(self, display_name: str, request_kwargs: Dict = {}) -> str:
        response = self._client.get(
            "/projects:suggest-id",
            params={"display_name": display_name},
            **request_kwargs,
        )
        handle_errors(response)
        return response.json()

    def delete_project(self, project_id: str, request_kwargs: Dict = {}) -> None:
        response = self._client.delete(f"/projects/{project_id}", **request_kwargs)
        handle_errors(response)

    def list_project_members(
        self, project_id: str, request_kwargs: Dict = {}
    ) -> List[UserPermission]:
        response = self._client.get(f"/projects/{project_id}/users", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[UserPermission], response.text)

    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        access_level: AccessLevel,
        request_kwargs: Dict = {},
    ) -> List[UserPermission]:
        resource = self._client.put(
            f"/projects/{project_id}/users/{user_id}",
            params={"access_level": access_level.value},
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(List[UserPermission], resource.text)

    def remove_project_member(
        self, project_id: str, user_id: str, request_kwargs: Dict = {}
    ) -> List[UserPermission]:
        resource = self._client.delete(
            f"/projects/{project_id}/users/{user_id}", **request_kwargs
        )
        handle_errors(resource)
        return parse_raw_as(List[UserPermission], resource.text)

    def get_project_token(
        self,
        project_id: str,
        access_level: AccessLevel = AccessLevel.WRITE,
        request_kwargs: Dict = {},
    ) -> str:
        if len(project_id) == 0:
            raise ValueError("Parameter project_id must not be empty!")
        response = self._client.get(
            f"/projects/{project_id}/token",
            params={"access_level": access_level.value},
            **request_kwargs,
        )
        handle_errors(response)
        return response.json()
