from abc import ABC, abstractmethod
from typing import List

from pydantic import EmailStr, SecretStr

from contaxy.schema import File, Project, ProjectCreation, User, UserRegistration


class SeedOperations(ABC):
    @abstractmethod
    def create_user(
        self,
        user_input: UserRegistration = UserRegistration(
            username="Foo", email=EmailStr("foo@bar.com"), password=SecretStr("Foobar")
        ),
    ) -> User:
        pass

    @abstractmethod
    def create_users(self, amount: int) -> List[User]:
        pass

    @abstractmethod
    def create_project(
        self,
        project_input: ProjectCreation = ProjectCreation(
            id="my-test-project", display_name="My Test Project!"
        ),
    ) -> Project:
        pass

    @abstractmethod
    def create_projects(self, amount: int) -> List[Project]:
        pass

    @abstractmethod
    def create_file(
        self,
        project_id: str,
        file_key: str = "my-test-file",
        max_number_chars: int = 200,
    ) -> File:
        pass
