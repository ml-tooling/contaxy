from abc import ABC, abstractmethod
from typing import List

from contaxy.schema import AccessLevel, Project, ProjectCreation, ProjectInput
from contaxy.schema.auth import UserPermission


class ProjectOperations(ABC):
    @abstractmethod
    def list_projects(self) -> List[Project]:
        """Returns all projects visible to the authenticated user."""
        pass

    @abstractmethod
    def create_project(
        self, project_input: ProjectCreation, technical_project: bool = False
    ) -> Project:
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Project:
        pass

    @abstractmethod
    def update_project(self, project_id: str, project_input: ProjectInput) -> Project:
        pass

    @abstractmethod
    def suggest_project_id(self, display_name: str) -> str:
        pass

    @abstractmethod
    def delete_project(self, project_id: str) -> None:
        pass

    @abstractmethod
    def list_project_members(self, project_id: str) -> List[UserPermission]:
        pass

    @abstractmethod
    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        access_level: AccessLevel,
    ) -> List[UserPermission]:
        pass

    @abstractmethod
    def remove_project_member(
        self, project_id: str, user_id: str
    ) -> List[UserPermission]:
        pass

    @abstractmethod
    def get_project_token(
        self, project_id: str, access_level: AccessLevel = AccessLevel.WRITE
    ) -> str:
        """Create project token with permission to access all resources of the project.

        If a token for the specified project and access level already exists in the DB, it is returned instead of creating
        a new project token.

        Args:
            project_id: Id of the user for which the token should be created
            access_level: The access level of the user token (defaults to "write")

        Returns:
            User token for specified user id and access level.
        """
        pass
