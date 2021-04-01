"""Used for endpoint stress tests via locust."""
import random
from logging import error
from typing import Dict, List, Tuple

from faker import Faker
from locust import HttpUser, between, tag, task

from contaxy.clients import AuthClient, FileClient, JsonDocumentClient, ProjectClient
from contaxy.managers.seed import SeedManager
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
    UserRegistration,
)
from contaxy.schema.file import File
from contaxy.schema.project import Project, ProjectCreation, ProjectInput
from contaxy.schema.shared import CoreOperations
from contaxy.utils import auth_utils, id_utils

TEST_RESOURCE_PREFIX = "lt-"
JSON_COLLECTION_OPTIONS = [f"{TEST_RESOURCE_PREFIX}coll-{i}" for i in range(5)]

fake = Faker()


class CommonUser(HttpUser):
    wait_time = between(0.5, 5)
    # For Locust, the base_url is set via the `--host` flag when running `locust`
    host: str

    authorized_user: str
    file_prefix: str

    def on_start(self) -> None:
        if not self.host:
            error(
                "For stress testing, the host/endpoint has to be provided. Please provide the endpoint via `--host` argument "
            )
            self.environment.runner.quit()
            return

            # TODO: is the setting via env variable required?
            # Either provide the endpoint via `--host` argument or set the `REMOTE_BACKEND_ENDPOINT` environment variable (e.g `REMOTE_BACKEND_ENDPOINT=http://localhost:8000`).
            # If host is not set, use remote backend endpoint from test settings
            # assert test_settings.REMOTE_BACKEND_ENDPOINT is not None
            # if test_settings.REMOTE_BACKEND_ENDPOINT is not None:
            #    self.host = test_settings.REMOTE_BACKEND_ENDPOINT
        username = (
            TEST_RESOURCE_PREFIX
            + fake.simple_profile()["username"]
            + id_utils.generate_short_uuid()
        )
        password = fake.password(length=12)

        auth_client = AuthClient(self.client)
        # Create user
        created_user = auth_client.create_user(
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
        self.authorized_user = created_user.id
        self.user_projects: Dict[str, Project] = {}
        self.file_prefix = "my-test"

    def _get_user_project(self) -> Project:
        """Returns a random user project."""
        if len(self.user_projects.keys()) > 0:
            selected_project_id = random.choice(list(self.user_projects.keys()))
            return self.user_projects[selected_project_id]

        # Creating a new user project
        project_client = ProjectClient(self.client)
        project_name = (
            id_utils.generate_short_uuid()
        )  # TEST_RESOURCE_PREFIX +  fake.bs()
        project_id = project_client.suggest_project_id(
            project_name,
            request_kwargs={"name": CoreOperations.SUGGEST_PROJECT_ID.value},
        )
        created_project = project_client.create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=fake.sentence(),
            ),
            technical_project=False,
            request_kwargs={"name": CoreOperations.CREATE_PROJECT.value},
        )
        self.user_projects[created_project.id] = created_project
        return created_project

    @task(2)
    @tag("projects")
    def create_project(self) -> None:
        project_client = ProjectClient(self.client)
        project_name = (
            id_utils.generate_short_uuid()
        )  # TEST_RESOURCE_PREFIX +  fake.bs()
        project_id = project_client.suggest_project_id(
            project_name,
            request_kwargs={"name": CoreOperations.SUGGEST_PROJECT_ID.value},
        )
        created_project = project_client.create_project(
            ProjectCreation(
                id=project_id,
                display_name=project_name,
                description=fake.sentence(),
            ),
            technical_project=False,
            request_kwargs={"name": CoreOperations.CREATE_PROJECT.value},
        )
        self.user_projects[created_project.id] = created_project

    @task(1)
    @tag("projects")
    def delete_project(self) -> None:
        project_client = ProjectClient(self.client)
        selected_project = self._get_user_project()
        project_client.delete_project(
            selected_project.id,
            request_kwargs={"name": CoreOperations.DELETE_PROJECT.value},
        )
        del self.user_projects[selected_project.id]

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

    @task(2)
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

    @task(25)
    @tag("json-db")
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

    @task(5)
    @tag("json-db")
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

    @task(10)
    @tag("json-db")
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

    @task(5)
    @tag("json-db")
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

    @task(5)  # TODO: Check weight
    @tag("file")
    def upload_file(self) -> None:
        file_client = FileClient(self.client)
        project = self._get_user_project()

        file_stream = SeedManager.create_file_stream(
            max_number_chars=random.randint(2000000, 8000000)
        )

        # This might create some file versions as well
        file_key = (
            f"{self.file_prefix}.bin"
            if random.randint(1, 10) % 3 == 0
            else f"{self.file_prefix}-{random.randint(1,100000)}.bin"
        )

        file_client.upload_file(project.id, file_key, file_stream)

    @task(5)  # TODO: Check weight
    @tag("file")
    def download_file(self) -> None:
        file_client, project, files = self._get_file_test_setup()
        if not files:
            return

        file = random.choice(files)
        version = file.version if bool(random.getrandbits(1)) else None
        file_stream = file_client.download_file(project.id, file.key, version)
        for chunk in file_stream:
            pass

    @task(5)  # TODO: Check weight
    @tag("file")
    def get_file_metadata(self) -> None:
        file_client, project, files = self._get_file_test_setup()
        if not files:
            return

        file = random.choice(files)
        version = file.version if bool(random.getrandbits(1)) else None
        file_client.get_file_metadata(project.id, file.key, version)

    @task(5)  # TODO: Check weight
    @tag("file")
    def update_file_metadata(self) -> None:
        file_client, project, files = self._get_file_test_setup()
        if not files:
            return

        file = random.choice(files)
        version = file.version if bool(random.getrandbits(1)) else None
        file = file_client.get_file_metadata(project.id, file.key, version)
        file.description = "Viva Colonia!"
        file_client.update_file_metadata(file, project.id, file.key, version)

    @task(2)  # TODO: Check weight
    @tag("file")
    def delete_file(self) -> None:
        file_client, project, files = self._get_file_test_setup()
        if not files:
            return

        file = random.choice(files)
        version = file.version if bool(random.getrandbits(1)) else None
        keep_latest_version = random.randint(1, 10) % 3 == 0 if not version else False
        file_client.delete_file(project.id, file.key, version, keep_latest_version)

    @task(1)  # TODO: Check weight
    @tag("file")
    def delete_files(self) -> None:
        file_client = FileClient(self.client)
        project = self._get_user_project()
        file_client.delete_files(project.id)

    def _get_file_test_setup(self) -> Tuple[FileClient, Project, List[File]]:
        file_client = FileClient(self.client)

        project = self._get_user_project()

        include_versions = bool(random.getrandbits(1))
        recursive = bool(random.getrandbits(1))
        prefix = self.file_prefix if bool(random.getrandbits(1)) else None

        files = file_client.list_files(project.id, recursive, include_versions, prefix)
        return file_client, project, files
