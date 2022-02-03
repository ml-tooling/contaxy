from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Callable, Generator, List

import pytest
import requests
from faker import Faker
from fastapi.testclient import TestClient

from contaxy import config
from contaxy.clients import AuthClient
from contaxy.clients.project import ProjectClient
from contaxy.clients.system import SystemClient
from contaxy.managers.auth import AuthManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.project import ProjectManager
from contaxy.operations.auth import AuthOperations
from contaxy.operations.project import ProjectOperations
from contaxy.schema.auth import (
    USERS_KIND,
    AccessLevel,
    AuthorizedAccess,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
    User,
    UserRegistration,
)
from contaxy.schema.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from contaxy.schema.project import (
    MAX_PROJECT_ID_LENGTH,
    Project,
    ProjectCreation,
    ProjectInput,
)
from contaxy.utils import auth_utils
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings
from .utils import ComponentManagerMock

DEFAULT_PASSWORD = "pwd"


class ProjectOperationsTests(ABC):
    @property
    @abstractmethod
    def project_manager(self) -> ProjectOperations:
        pass

    @property
    @abstractmethod
    def auth_manager(self) -> AuthOperations:
        pass

    @abstractmethod
    def login_user(self, username: str, password: str) -> User:
        pass

    def test_suggest_project_id(self, faker: Faker) -> None:
        for _ in range(10):
            project_id = self.project_manager.suggest_project_id(faker.bs())
            assert (
                len(project_id) <= MAX_PROJECT_ID_LENGTH
            ), f"Project id ({project_id}) should not be longer than the maximum allowed."
            # TODO additional tests

    @pytest.fixture(autouse=True)
    def create_project(self) -> Generator:
        _created_projects = []

        def inner_create_project(
            project_input: ProjectCreation, technical_project: bool = False
        ):
            new_project = self.project_manager.create_project(
                project_input, technical_project
            )
            _created_projects.append(new_project)
            return new_project

        yield inner_create_project
        for project in _created_projects:
            try:
                self.project_manager.delete_project(project.id)
            except ResourceNotFoundError:
                pass

    @pytest.fixture(autouse=True)
    def create_user(self) -> Generator:
        _created_users = []

        def inner_create_user(username=None):
            if username is None:
                username = Faker().simple_profile()["username"]
            new_user = self.auth_manager.create_user(
                UserRegistration(username=username, password=DEFAULT_PASSWORD)
            )
            _created_users.append(new_user)
            return new_user

        yield inner_create_user
        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        for user in _created_users:
            try:
                self.auth_manager.delete_user(user.id)
            except ResourceNotFoundError:
                pass

    def test_create_project(
        self, faker: Faker, create_user: Callable, create_project: Callable
    ) -> None:
        created_projects: List[Project] = []
        for _ in range(3):
            project_name = faker.bs()
            project_id = self.project_manager.suggest_project_id(project_name)

            created_project = create_project(
                ProjectCreation(
                    id=project_id,
                    display_name=project_name,
                    description=faker.sentence(),
                ),
                technical_project=False,
            )
            created_projects.append(created_project)
            assert created_project.id == project_id
            assert created_project.display_name == project_name
            assert created_project.technical_project is False
            assert (
                datetime.now(timezone.utc) - created_project.created_at
            ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."

        for created_project in created_projects:
            # Evaluate get project
            project = self.project_manager.get_project(created_project.id)
            assert created_project.id == project.id
            assert created_project.display_name == project.display_name

        with pytest.raises(ResourceNotFoundError):
            self.project_manager.get_project("foobar")

        # Create project with an already existing project ID
        with pytest.raises(ResourceAlreadyExistsError):
            create_project(
                ProjectCreation(
                    id=created_projects[0].id,
                    display_name=project_name,
                    description=faker.sentence(),
                )
            )

        # Create project with an authorized user
        user = create_user()
        self.login_user(username=user.username, password=DEFAULT_PASSWORD)

        project_name = faker.bs()
        project_id = self.project_manager.suggest_project_id(project_name)
        created_project = create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=faker.sentence(),
            )
        )

        assert (
            created_project.created_by
            == USERS_KIND + "/" + user.id  # TODO: use user.name
        ), "The authorized user should be set as creator"

    def test_list_project(
        self, faker: Faker, create_user: Callable, create_project: Callable
    ) -> None:
        # Set an authorized user in the request state
        user = create_user()
        self.login_user(username=user.username, password=DEFAULT_PASSWORD)

        prev_num_projects = len(self.project_manager.list_projects())
        created_projects_with_user: List[Project] = []
        for _ in range(3):
            project_name = faker.bs()
            project_id = self.project_manager.suggest_project_id(project_name)

            created_project = create_project(
                ProjectCreation(
                    id=project_id,
                    display_name=project_name,
                    description=faker.sentence(),
                ),
                technical_project=False,
            )
            created_projects_with_user.append(created_project)

        # This should only contain the projects the are created by the authorized user
        assert len(self.project_manager.list_projects()) == prev_num_projects + len(
            created_projects_with_user
        )

    def test_update_project(self, faker: Faker, create_project: Callable) -> None:
        # Create projects
        created_projects: List[Project] = []
        for _ in range(3):
            project_name = faker.bs()
            project_id = self.project_manager.suggest_project_id(project_name)
            created_project = create_project(
                ProjectCreation(
                    id=project_id,
                    display_name=project_name,
                    description=faker.sentence(),
                )
            )
            created_projects.append(created_project)

        for project in created_projects:
            self.project_manager.update_project(
                project.id,
                ProjectInput(
                    display_name=project.display_name + " - Updated",
                    description=project.description + " - Updated",
                ),
            )
            updated_project = self.project_manager.get_project(project.id)

            assert project.display_name != updated_project.display_name
            assert project.description != updated_project.description
            assert project.updated_at != updated_project.updated_at
            assert project.created_at == updated_project.created_at

    def test_delete_project(self, faker: Faker, create_project: Callable) -> None:
        project_name = faker.bs()
        project_id = self.project_manager.suggest_project_id(project_name)

        created_project = create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=faker.sentence(),
            ),
            technical_project=False,
        )

        self.project_manager.delete_project(created_project.id)
        with pytest.raises(ResourceNotFoundError):
            self.project_manager.get_project(created_project.id)

        assert not any(
            project.id == created_project.id
            for project in self.project_manager.list_projects()
        )

    def test_project_member_handling(
        self, faker: Faker, create_user: Callable, create_project: Callable
    ) -> None:
        project_name = faker.bs()
        project_id = self.project_manager.suggest_project_id(project_name)
        create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=faker.sentence(),
            ),
            technical_project=False,
        )

        user1 = create_user()

        self.project_manager.add_project_member(project_id, user1.id, AccessLevel.WRITE)
        assert user1.id in [
            user.id for user in self.project_manager.list_project_members(project_id)
        ]

        user2 = create_user()

        self.project_manager.add_project_member(project_id, user2.id, AccessLevel.ADMIN)
        assert user1.id in [
            user.id for user in self.project_manager.list_project_members(project_id)
        ]
        assert user2.id in [
            user.id for user in self.project_manager.list_project_members(project_id)
        ]
        self.login_user(username=user2.username, password=DEFAULT_PASSWORD)

        assert (
            len(self.project_manager.list_projects()) == 1
        ), "The authorized user should see 1 project"

        self.project_manager.remove_project_member(project_id, user2.id)
        assert (
            len(self.project_manager.list_projects()) == 0
        ), "The authorized user should see 0 projects"

        # Test that project can be deleted even if users don't exist anymore
        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        self.auth_manager.delete_user(user1.id)
        self.project_manager.delete_project(project_id)


class ProjectOperationsEndpointTests(ProjectOperationsTests, ABC):
    def test_create_technical_user_project(self, create_user: Callable) -> None:
        user = create_user()

        project = self.project_manager.get_project(user.id)
        assert project
        assert project.technical_project is True

    def test_list_projects_as_admin(self, faker: Faker) -> None:
        # TODO: add a test that checks that `list_project` also returns the technical user project. This cannot be tested currently as for technical users no user-project is created and for a new user, no endpoint exists yet to add the permission to see also technical projects.
        pass


@pytest.mark.unit
class TestProjectManagerWithInMemoryDB(ProjectOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        create_user: Callable,
    ) -> Generator:
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        component_manager_mock = ComponentManagerMock(
            global_state, request_state, json_db_manager=json_db
        )
        self._auth_manager = AuthManager(component_manager_mock)
        component_manager_mock.auth_manager = self._auth_manager
        self._project_manager = ProjectManager(component_manager_mock)
        # Make sure admin user exists in InMemoryDict DB
        create_user("admin")
        yield

    @property
    def project_manager(self) -> ProjectManager:
        return self._project_manager

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager

    def login_user(self, username: str, password: str) -> None:
        user_id = self.auth_manager._get_user_id_by_login_id(username)
        self.project_manager._request_state.authorized_access = AuthorizedAccess(
            authorized_subject=USERS_KIND + "/" + user_id  # TODO: use resource name
        )


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestProjectManagerWithPostgresDB(ProjectOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        json_db = PostgresJsonDocumentManager(global_state, request_state)
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        component_manager_mock = ComponentManagerMock(
            global_state, request_state, json_db_manager=json_db
        )
        self._auth_manager = AuthManager(component_manager_mock)
        component_manager_mock.auth_manager = self._auth_manager
        self._project_manager = ProjectManager(component_manager_mock)

        yield

    @property
    def project_manager(self) -> ProjectOperations:
        return self._project_manager

    @property
    def auth_manager(self) -> AuthOperations:
        return self._auth_manager

    def login_user(self, username: str, password: str) -> None:
        user_id = self.auth_manager._get_user_id_by_login_id(username)
        self.project_manager._request_state.authorized_access = AuthorizedAccess(
            authorized_subject=USERS_KIND + "/" + user_id  # TODO: use resource name
        )


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestProjectOperationsViaLocalEndpoints(ProjectOperationsEndpointTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self) -> Generator:
        from contaxy.api import app

        with TestClient(app=app, root_path="/") as test_client:
            self._endpoint_client = test_client
            system_manager = SystemClient(self._endpoint_client)
            self._auth_manager = AuthClient(self._endpoint_client)
            self._project_manager = ProjectClient(self._endpoint_client)

            # system_manager.cleanup_system()
            system_manager.initialize_system()

            self.login_user(
                config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
            )
            yield

    @property
    def project_manager(self) -> ProjectOperations:
        return self._project_manager

    @property
    def auth_manager(self) -> AuthOperations:
        return self._auth_manager

    def login_user(self, username: str, password: str) -> None:
        self.auth_manager.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=username,
                password=password,
                scope=auth_utils.construct_permission(
                    "*", AccessLevel.ADMIN
                ),  # Get full scope
                set_as_cookie=True,
            )
        )


@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_ENDPOINT,
    reason="No remote backend is configured (via REMOTE_BACKEND_ENDPOINT).",
)
@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_TESTS,
    reason="Remote Backend Tests are deactivated, use REMOTE_BACKEND_TESTS to activate.",
)
@pytest.mark.integration
class TestProjectOperationsViaRemoteEndpoints(ProjectOperationsEndpointTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self, remote_client: requests.Session) -> Generator:
        self._endpoint_client = remote_client
        self._auth_manager = AuthClient(self._endpoint_client)
        self._project_manager = ProjectClient(self._endpoint_client)

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        yield

    @property
    def project_manager(self) -> ProjectOperations:
        return self._project_manager

    @property
    def auth_manager(self) -> AuthOperations:
        return self._auth_manager

    def login_user(self, username: str, password: str) -> None:
        self.auth_manager.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=username,
                password=password,
                scope=auth_utils.construct_permission(
                    "*", AccessLevel.ADMIN
                ),  # Get full scope
                set_as_cookie=True,
            )
        )
