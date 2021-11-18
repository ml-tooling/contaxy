from abc import ABC, abstractmethod
from typing import List

from contaxy.schema import AccessLevel, Project, ProjectCreation, ProjectInput, User


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
    def list_project_members(self, project_id: str) -> List[User]:
        pass

    @abstractmethod
    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        access_level: AccessLevel,
    ) -> List[User]:
        pass

    @abstractmethod
    def remove_project_member(self, project_id: str, user_id: str) -> List[User]:
        pass
