import io
from typing import List

from faker import Faker
from pydantic import EmailStr, SecretStr

from contaxy.operations import AuthOperations, FileOperations, ProjectOperations
from contaxy.operations.seed import SeedOperations
from contaxy.schema import File, Project, User, UserRegistration
from contaxy.schema.project import ProjectCreation
from contaxy.utils.state_utils import GlobalState, RequestState

FAKER = Faker()
Faker.seed(0)


class SeedManager(SeedOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        auth_manager: AuthOperations,
        file_manager: FileOperations,
        project_manager: ProjectOperations,
    ):
        self.global_state = global_state
        self.request_state = request_state
        self.auth_manager = auth_manager
        self.file_manager = file_manager
        self.project_manager = project_manager

    def create_user(
        self,
        user_input: UserRegistration = UserRegistration(
            username="Foo", email=EmailStr("foo@bar.com"), password=SecretStr("Foobar")
        ),
    ) -> User:
        return self.auth_manager.create_user(user_input=user_input)

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

    def create_project(
        self,
        project_input: ProjectCreation = ProjectCreation(
            id="my-test-project", display_name="My Test Project!"
        ),
    ) -> Project:
        return self.project_manager.create_project(project_input=project_input)

    def create_projects(self, amount: int) -> List[Project]:
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
        file_stream = io.BytesIO(
            FAKER.text(max_nb_chars=max_number_chars).encode("UTF-8")
        )
        return self.file_manager.upload_file(
            project_id=project_id, file_key=file_key, file_stream=file_stream  # type: ignore
        )
