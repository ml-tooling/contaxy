"""Used for Locust stress tests."""
import random
from logging import error

from faker import Faker
from locust import HttpUser, between, tag, task
from loguru import logger

from contaxy.clients import AuthClient, JsonDocumentClient, ProjectClient
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
    UserRegistration,
)
from contaxy.schema.project import Project, ProjectCreation, ProjectInput
from contaxy.schema.shared import CoreOperations
from contaxy.utils import auth_utils, id_utils
from tests.unit_tests.conftest import test_settings

TEST_RESOURCE_PREFIX = "lt-"
JSON_COLLECTION_OPTIONS = [f"{TEST_RESOURCE_PREFIX}coll-{i}" for i in range(5)]

fake = Faker()


class CommonUser(HttpUser):
    wait_time = between(1, 2.5)
    # For Locust, the base_url is set via the `--host` flag when running `locust`
    host: str

    def on_start(self) -> None:
        if not self.host:
            # If host is not set, use remote backend endpoint from test settings
            assert test_settings.REMOTE_BACKEND_ENDPOINT is not None
            if test_settings.REMOTE_BACKEND_ENDPOINT is not None:
                self.host = test_settings.REMOTE_BACKEND_ENDPOINT
            else:
                error(
                    "For stress testing, the host/endpoint has to be provided. Either provide the endpoint via `--host` argument or set the `REMOTE_BACKEND_ENDPOINT` environment variable (e.g `REMOTE_BACKEND_ENDPOINT=http://localhost:8000`)."
                )
                self.environment.runner.quit()
                return
        logger.info("Logging in user.")
        username = (
            TEST_RESOURCE_PREFIX
            + fake.simple_profile()["username"]
            + id_utils.generate_short_uuid()
        )
        password = fake.password(length=12)

        auth_client = AuthClient(self.client)
        # Create user
        auth_client.create_user(
            UserRegistration(username=username, password=password),
            request_kwargs={"name": CoreOperations.CREATE_USER.value},
        )
        # Login user -> this sets the user cookie
        auth_client.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=username,
                password=password,
                scope=auth_utils.construct_permission(
                    "*", AccessLevel.ADMIN
                ),  # Get full scope
                set_as_cookie=True,
            ),
            request_kwargs={"name": CoreOperations.REQUEST_TOKEN.value},
        )

    def _get_user_project(self) -> Project:
        """Returns a random user project."""
        project_client = ProjectClient(self.client)
        user_projects = project_client.list_projects(
            request_kwargs={"name": CoreOperations.LIST_PROJECTS.value},
        )
        if user_projects:
            return random.choice(user_projects)

        logger.debug("User does not have any projects.")
        # Creating a new user project
        project_name = (
            TEST_RESOURCE_PREFIX + id_utils.generate_short_uuid()
        )  # fake.bs()
        project_id = project_client.suggest_project_id(
            project_name,
            request_kwargs={"name": CoreOperations.SUGGEST_PROJECT_ID.value},
        )
        return project_client.create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=fake.sentence(),
            ),
            technical_project=False,
            request_kwargs={"name": CoreOperations.CREATE_PROJECT.value},
        )

    @task(2)
    @tag("projects")
    def create_project(self) -> None:
        project_client = ProjectClient(self.client)
        project_name = (
            TEST_RESOURCE_PREFIX + id_utils.generate_short_uuid()
        )  # + fake.bs()
        project_id = project_client.suggest_project_id(
            project_name,
            request_kwargs={"name": CoreOperations.SUGGEST_PROJECT_ID.value},
        )
        project_client.create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=fake.sentence(),
            ),
            technical_project=False,
            request_kwargs={"name": CoreOperations.CREATE_PROJECT.value},
        )

    @task(1)
    @tag("projects")
    def delete_project(self) -> None:
        project_client = ProjectClient(self.client)
        selected_project = self._get_user_project()
        project_client.delete_project(
            selected_project.id,
            request_kwargs={"name": CoreOperations.DELETE_PROJECT.value},
        )

    @task(10)
    @tag("projects")
    def list_projects(self) -> None:
        project_client = ProjectClient(self.client)
        project_client.list_projects(
            request_kwargs={"name": CoreOperations.LIST_PROJECTS.value},
        )

    @task(20)
    @tag("projects")
    def get_project(self) -> None:
        project_client = ProjectClient(self.client)
        selected_project = self._get_user_project()
        project_client.get_project(
            selected_project.id,
            request_kwargs={"name": CoreOperations.GET_PROJECT.value},
        )

    @task(2)
    @tag("projects")
    def list_project_members(self) -> None:
        project_client = ProjectClient(self.client)
        selected_project = self._get_user_project()
        project_client.list_project_members(
            selected_project.id,
            request_kwargs={"name": CoreOperations.LIST_PROJECT_MEMBERS.value},
        )

    @task(20)
    @tag("projects")
    def update_project(self) -> None:
        project_client = ProjectClient(self.client)
        selected_project = self._get_user_project()
        project_client.update_project(
            selected_project.id,
            ProjectInput(description=fake.sentence()),
            request_kwargs={"name": CoreOperations.UPDATE_PROJECT.value},
        )

    # TODO: add/remove project members

    @tag("json-db")
    @task(25)
    def create_json_document(self) -> None:
        json_db_client = JsonDocumentClient(self.client)
        selected_project = self._get_user_project()
        collection_id = random.choice(JSON_COLLECTION_OPTIONS)
        key = id_utils.generate_short_uuid()
        json_db_client.create_json_document(
            selected_project.id,
            collection_id,
            key,
            json_document=fake.json(
                data_columns={
                    "ID": "pyint",
                    "Details": {"Name": "name", "Address": "address"},
                },
                num_rows=1,
            ),
            request_kwargs={"name": CoreOperations.CREATE_JSON_DOCUMENT.value},
        )

    @tag("json-db")
    @task(5)
    def update_json_document(self) -> None:
        json_db_client = JsonDocumentClient(self.client)
        selected_project = self._get_user_project()
        collection_id = random.choice(JSON_COLLECTION_OPTIONS)
        json_documents = json_db_client.list_json_documents(
            selected_project.id,
            collection_id,
            request_kwargs={"name": CoreOperations.LIST_JSON_DOCUMENTS.value},
        )
        if json_documents:
            # Only update if user has json documents
            selected_document = random.choice(json_documents)
            json_db_client.update_json_document(
                selected_project.id,
                collection_id,
                selected_document.key,
                json_document=fake.json(
                    data_columns={
                        "ID": "pyint",
                        "Details": {"Name": "name", "Address": "address"},
                    },
                    num_rows=1,
                ),
                request_kwargs={"name": CoreOperations.UPDATE_JSON_DOCUMENT.value},
            )

    @tag("json-db")
    @task(10)
    def get_json_document(self) -> None:
        json_db_client = JsonDocumentClient(self.client)
        selected_project = self._get_user_project()
        collection_id = random.choice(JSON_COLLECTION_OPTIONS)
        json_documents = json_db_client.list_json_documents(
            selected_project.id,
            collection_id,
            request_kwargs={"name": CoreOperations.LIST_JSON_DOCUMENTS.value},
        )
        if json_documents:
            # Only update if user has json documents
            selected_document = random.choice(json_documents)
            json_db_client.get_json_document(
                selected_project.id,
                collection_id,
                selected_document.key,
                request_kwargs={"name": CoreOperations.GET_JSON_DOCUMENT.value},
            )

    @tag("json-db")
    @task(5)
    def delete_json_document(self) -> None:
        json_db_client = JsonDocumentClient(self.client)
        selected_project = self._get_user_project()
        collection_id = random.choice(JSON_COLLECTION_OPTIONS)
        json_documents = json_db_client.list_json_documents(
            selected_project.id,
            collection_id,
            request_kwargs={"name": CoreOperations.LIST_JSON_DOCUMENTS.value},
        )
        if json_documents:
            # Only update if user has json documents
            selected_document = random.choice(json_documents)
            json_db_client.delete_json_document(
                selected_project.id,
                collection_id,
                selected_document.key,
                request_kwargs={"name": CoreOperations.DELETE_JSON_DOCUMENT.value},
            )
