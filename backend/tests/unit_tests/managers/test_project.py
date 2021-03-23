from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

import pytest
from faker import Faker
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.project import ProjectManager
from contaxy.operations.project import ProjectOperations
from contaxy.schema.auth import AuthorizedAccess
from contaxy.schema.exceptions import ResourceAlreadyExistsError
from contaxy.schema.project import MAX_PROJECT_ID_LENGTH, Project, ProjectCreation
from contaxy.utils import id_utils
from contaxy.utils.state_utils import GlobalState, RequestState
from tests.unit_tests.conftest import test_settings


@pytest.fixture()
def global_state() -> GlobalState:
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    return RequestState(State())


class ProjectOperationsTests(ABC):
    @property
    @abstractmethod
    def project_manager(self) -> ProjectManager:
        pass

    def test_suggest_project_id(self, faker: Faker) -> None:
        for _ in range(10):
            project_id = self.project_manager.suggest_project_id(faker.bs())
            assert len(project_id) <= MAX_PROJECT_ID_LENGTH
            # TODO additional tests

    def test_create_project(self, faker: Faker) -> None:
        created_projects: List[Project] = []
        for _ in range(10):
            project_name = faker.bs()
            project_id = self.project_manager.suggest_project_id(project_name)

            created_project = self.project_manager.create_project(
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
                datetime.today() - created_project.created_at
            ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."

        # Create project with an already existing project ID
        with pytest.raises(ResourceAlreadyExistsError):
            self.project_manager.create_project(
                ProjectCreation(
                    id=created_projects[0].id,
                    display_name=project_name,
                    description=faker.sentence(),
                )
            )

        # Create project with an authorized user
        USER = "users/" + id_utils.generate_short_uuid()
        self.project_manager._request_state.authorized_access = AuthorizedAccess(
            authorized_subject=USER
        )
        project_name = faker.bs()
        project_id = self.project_manager.suggest_project_id(project_name)
        created_project = self.project_manager.create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=faker.sentence(),
            )
        )

        assert (
            created_project.created_by == USER
        ), "The authorized user should be set as creator"

    def test_get_project(self, faker: Faker) -> None:
        pass

    def test_list_project(self, faker: Faker) -> None:
        # Create 10 projects without authorized user
        created_projects_without_user: List[Project] = []
        for _ in range(10):
            project_name = faker.bs()
            project_id = self.project_manager.suggest_project_id(project_name)

            created_project = self.project_manager.create_project(
                ProjectCreation(
                    id=project_id,
                    display_name=project_name,
                    description=faker.sentence(),
                ),
                technical_project=False,
            )
            created_projects_without_user.append(created_project)

        assert len(self.project_manager.list_projects()) == len(
            created_projects_without_user
        )

        # Set an authorized user in the request state
        USER = "users/" + id_utils.generate_short_uuid()
        self.project_manager._request_state.authorized_access = AuthorizedAccess(
            authorized_subject=USER
        )
        #
        created_projects_with_user: List[Project] = []
        for _ in range(5):
            project_name = faker.bs()
            project_id = self.project_manager.suggest_project_id(project_name)

            created_project = self.project_manager.create_project(
                ProjectCreation(
                    id=project_id,
                    display_name=project_name,
                    description=faker.sentence(),
                ),
                technical_project=False,
            )
            created_projects_with_user.append(created_project)

        # This should only contain the projects the are created by the authorized user
        assert len(self.project_manager.list_projects()) == len(
            created_projects_with_user
        )


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestProjectManagerWithPostgresDB(ProjectOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_project_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> None:
        json_db = PostgresJsonDocumentManager(global_state, request_state)
        auth_manager = AuthManager(global_state, request_state, json_db)
        self._project_manager = ProjectManager(
            global_state, request_state, json_db, auth_manager
        )

    @property
    def project_manager(self) -> ProjectManager:
        return self._project_manager


@pytest.mark.unit
class TestProjectManagerWithInMemoryDB(ProjectOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_project_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> None:
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        auth_manager = AuthManager(global_state, request_state, json_db)
        self._project_manager = ProjectManager(
            global_state, request_state, json_db, auth_manager
        )

    @property
    def project_manager(self) -> ProjectOperations:
        return self._project_manager
