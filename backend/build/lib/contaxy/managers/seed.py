import io
from random import randint
from typing import List, Optional

from faker import Faker
from pydantic import EmailStr

from contaxy.operations import AuthOperations, FileOperations, ProjectOperations
from contaxy.operations.seed import SeedOperations
from contaxy.schema import File, Project, User, UserRegistration
from contaxy.schema.project import ProjectCreation
from contaxy.utils.auth_utils import setup_user
from contaxy.utils.file_utils import FileStreamWrapper
from contaxy.utils.state_utils import GlobalState, RequestState

FAKER = Faker()
Faker.seed(0)

ERROR_NO_PROJECT_MANAGER = "Seeder needs to be initialized with a project manager"


class SeedManager(SeedOperations):
    def __init__(
        self,
        global_state: Optional[GlobalState] = None,
        request_state: Optional[RequestState] = None,
        auth_manager: Optional[AuthOperations] = None,
        file_manager: Optional[FileOperations] = None,
        project_manager: Optional[ProjectOperations] = None,
    ):
        self.global_state = global_state
        self.request_state = request_state
        self.auth_manager = auth_manager
        self.file_manager = file_manager
        self.project_manager = project_manager

    def create_user(
        self,
        user_input: UserRegistration = UserRegistration(
            username="Foo", email=EmailStr("foo@bar.com"), password="Foobar"
        ),
    ) -> User:
        if not self.auth_manager:
            raise RuntimeError("Seeder needs to be initialized with an auth manager")
        user = self.auth_manager.create_user(user_input=user_input)
        self.setup_user(user)
        return user

    def create_users(self, amount: int) -> List[User]:
        users = []
        for _ in range(amount):
            user = self.create_user(
                UserRegistration(
                    username=FAKER.user_name(),
                    email=FAKER.email(),
                    password=FAKER.password(),
                )
            )
            users.append(user)

        return users

    def setup_user(self, user: User) -> Project:
        if not self.project_manager:
            raise RuntimeError(ERROR_NO_PROJECT_MANAGER)
        if not self.auth_manager:
            raise RuntimeError("Seeder needs to be initialized with an auth manager")
        return setup_user(user, self.project_manager)

    def create_project(
        self,
        project_input: ProjectCreation = ProjectCreation(
            id="my-test-project", display_name="My Test Project!"
        ),
    ) -> Project:
        if not self.project_manager:
            raise RuntimeError(ERROR_NO_PROJECT_MANAGER)
        return self.project_manager.create_project(project_input=project_input)

    def create_projects(self, amount: int) -> List[Project]:
        if not self.project_manager:
            raise RuntimeError(ERROR_NO_PROJECT_MANAGER)
        projects = []
        for _ in range(amount):
            project = self.create_project(
                ProjectCreation(id=FAKER.ean(), display_name=FAKER.word())
            )
            projects.append(project)

        return projects

    def create_file(
        self,
        project_id: str,
        file_key: str = "my-test-file",
        max_number_chars: int = 200,
    ) -> File:
        if not self.file_manager:
            raise RuntimeError("Seeder needs to be initialized with a file manager")
        file_stream = FileStreamWrapper(
            io.BytesIO(FAKER.text(max_nb_chars=max_number_chars).encode("UTF-8"))
        )
        return self.file_manager.upload_file(
            project_id=project_id, file_key=file_key, file_stream=file_stream  # type: ignore
        )

    def create_files(
        self,
        project_id: str,
        number_of_files: int,
        prefix: Optional[str] = "my-test-file",
        max_number_chars: int = 200,
    ) -> List[File]:
        return [
            self.create_file(
                project_id,
                f"{prefix}-{randint(1,10000)}",
                max_number_chars,
            )
            for index in range(number_of_files)
        ]

    def create_file_stream(
        self,
        max_number_chars: int = 200,
    ) -> FileStreamWrapper:
        return FileStreamWrapper(
            io.BytesIO(FAKER.text(max_nb_chars=max_number_chars).encode("UTF-8"))
        )
