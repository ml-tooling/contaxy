import hashlib
from abc import ABC, abstractmethod
from random import randint
from typing import Generator, Optional

import pytest
import requests
from fastapi.testclient import TestClient

from contaxy import config
from contaxy.clients import AuthClient, JsonDocumentClient
from contaxy.clients.file import FileClient
from contaxy.clients.system import SystemClient
from contaxy.config import settings
from contaxy.managers.file.azure_blob import AzureBlobFileManager
from contaxy.managers.file.minio import MinioFileManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.seed import SeedManager
from contaxy.operations.file import FileOperations
from contaxy.operations.seed import SeedOperations
from contaxy.schema import FileInput
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
)
from contaxy.schema.exceptions import ResourceNotFoundError
from contaxy.utils import auth_utils
from contaxy.utils.minio_utils import delete_bucket, get_bucket_name
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings
from .utils import ComponentManagerMock


class FileOperationsTests(ABC):
    @property
    @abstractmethod
    def file_manager(self) -> FileOperations:
        pass

    @property
    @abstractmethod
    def seeder(self) -> SeedOperations:
        pass

    @property
    @abstractmethod
    def project_id(self) -> str:
        """Returns the project id for the given run."""
        pass

    def test_list_files(self) -> None:
        number_of_files = 3

        prefix_1 = "test-file"
        files_prefix_1 = self.seeder.create_files(
            self.project_id, number_of_files, prefix_1
        )
        prefix_2 = "file-test"
        files_prefix_2 = self.seeder.create_files(
            self.project_id, number_of_files, prefix_2
        )

        # Test - No files to selection
        result = self.file_manager.list_files(self.project_id, prefix="no-files")
        assert not result

        # Test - List all files
        result = self.file_manager.list_files(self.project_id)
        files_1 = list(filter(lambda file: file.key.startswith(prefix_1), result))
        files_2 = list(filter(lambda file: file.key.startswith(prefix_2), result))
        assert len(files_1) == len(files_prefix_1) and len(files_2) == len(
            files_prefix_2
        )

        # Test - By prefix
        result = self.file_manager.list_files(self.project_id, prefix=prefix_1)
        files_1 = list(filter(lambda file: file.key.startswith(prefix_1), result))
        files_2 = list(filter(lambda file: file.key.startswith(prefix_2), result))
        assert len(files_1) == len(files_prefix_1) and not files_2

        # Test - Include versions and validate available versions metadata
        update_file = files_prefix_1[0]
        self.seeder.create_file(self.project_id, update_file.key)
        result = self.file_manager.list_files(self.project_id, include_versions=True)
        file_versions = list(filter(lambda file: file.key == update_file.key, result))
        assert file_versions
        assert len(file_versions[0].available_versions) == 2
        assert (
            file_versions[0].available_versions == file_versions[1].available_versions
        )

        # Test - Recursive
        # TODO

        # Test - Externally uploaded file

    def test_get_file_metadata(self) -> None:
        version_1 = self.seeder.create_file(self.project_id)
        version_2 = self.seeder.create_file(self.project_id)

        # Test - File does not exist
        self._validate_file_not_found(self.project_id, "invalid-file")

        # Test - File exists
        #     -- Get latest version
        result_v2 = self.file_manager.get_file_metadata(self.project_id, version_1.key)
        assert result_v2.version == version_2.version
        assert result_v2.version != version_1.version
        assert len(result_v2.available_versions) == 2

        #     -- Get specific version
        result_v1 = self.file_manager.get_file_metadata(
            self.project_id, version_1.key, version_1.version
        )
        assert result_v1.version == version_1.version
        assert len(result_v2.available_versions) == 2

    def test_update_file_metadata(self) -> None:
        version_1 = self.seeder.create_file(self.project_id)
        version_2 = self.seeder.create_file(self.project_id)

        # Test - File does not exsists
        with pytest.raises(ResourceNotFoundError):
            self.file_manager.update_file_metadata(
                FileInput(key="invalid-file"), self.project_id, "invalid-file"
            )

        # Test - File exists
        #    -- Update latest version
        exp_description = "Updated description"
        exp_metadata = {"source": "http://fc.de"}
        updates = FileInput(
            key=version_1.key, description=exp_description, metadata=exp_metadata
        )
        updated_file = self.file_manager.update_file_metadata(
            updates, self.project_id, version_1.key
        )
        assert updated_file.version == version_2.version
        assert updated_file != version_1
        assert updated_file.description == exp_description
        assert updated_file.metadata == exp_metadata
        version_1 = self.file_manager.get_file_metadata(
            self.project_id, version_1.key, version_1.version
        )
        assert updated_file.description != version_1.description
        assert updated_file.metadata != version_1.metadata
        #    -- Update specific
        updated_file = self.file_manager.update_file_metadata(
            updates, self.project_id, version_1.key, version_1.version
        )
        assert updated_file.version == version_1.version
        assert updated_file.description == exp_description
        assert updated_file.metadata == exp_metadata

    def test_upload_file(self) -> None:
        file_stream = self.seeder.create_file_stream(max_number_chars=10000)
        file_key = "my-test.bin"

        # Test - File does not exist
        version_1 = self.file_manager.upload_file(
            self.project_id, file_key, file_stream
        )
        assert version_1.md5_hash == file_stream.hash
        assert version_1.key == file_key

        # Test - File exists
        file_stream = self.seeder.create_file_stream()
        version_2 = self.file_manager.upload_file(
            self.project_id, file_key, file_stream
        )
        assert version_1.version != version_2.version
        assert version_2.md5_hash == file_stream.hash

    def test_download_file(self) -> None:
        file_key = "test-download-file.bin"
        version_1 = self.seeder.create_file(self.project_id, file_key)
        version_2 = self.seeder.create_file(
            self.project_id, file_key, max_number_chars=10000
        )

        # Test - File does not exist
        with pytest.raises(ResourceNotFoundError):
            self.file_manager.download_file(self.project_id, "invalid-key")

        # Test - File exists
        #     -- Latest version
        hash = hashlib.md5()
        file_stream = self.file_manager.download_file(self.project_id, file_key)
        for chunk in file_stream:
            hash.update(chunk)
        assert version_2.md5_hash == hash.hexdigest()

        #     -- Specific version
        hash = hashlib.md5()
        file_stream = self.file_manager.download_file(
            self.project_id, file_key, version_1.version
        )
        for chunk in file_stream:
            hash.update(chunk)
        assert version_1.md5_hash == hash.hexdigest()

    def test_delete_file(self) -> None:

        # Test - File does not exist
        self.file_manager.delete_file(self.project_id, "invalid-key")

        # File exists
        file = self.seeder.create_file(self.project_id)
        self.file_manager.delete_file(self.project_id, file.key)
        self._validate_file_not_found(self.project_id, file.key)

        # Test - Multiple versions and no version specified
        file_key = "delete-1.bin"
        version_1 = self.seeder.create_file(self.project_id, file_key)
        version_2 = self.seeder.create_file(self.project_id, file_key)
        self.file_manager.delete_file(self.project_id, file_key)
        self._validate_file_not_found(self.project_id, file_key)

        # Test - Multiple versions and version specified
        file_key = "delete-2.bin"
        version_1 = self.seeder.create_file(self.project_id, file_key)
        version_2 = self.seeder.create_file(self.project_id, file_key)
        version_3 = self.seeder.create_file(self.project_id, file_key)

        # Delete latest version
        # Deletion of the currently active version is not possible on Azure Blob Storage
        if type(self.file_manager).__name__ not in ["AzureBlobFileManager"]:
            self.file_manager.delete_file(self.project_id, file_key, version_3.version)
            self._validate_file_not_found(self.project_id, file_key, version_3.version)
            file = self.file_manager.get_file_metadata(self.project_id, file_key)
            assert version_3.version not in file.available_versions
            assert version_2.version in file.available_versions
        else:
            with pytest.raises(ValueError):
                self.file_manager.delete_file(
                    self.project_id, file_key, version_3.version
                )

        # Delete oldest version
        self.file_manager.delete_file(self.project_id, file_key, version_1.version)
        self._validate_file_not_found(self.project_id, file_key, version_1.version)
        file = self.file_manager.get_file_metadata(self.project_id, file_key)
        assert version_1.version not in file.available_versions
        assert version_2.version in file.available_versions

        # Test - Keep latest version
        file_key = "delete-3.bin"
        version_1 = self.seeder.create_file(self.project_id, file_key)
        version_2 = self.seeder.create_file(self.project_id, file_key)
        version_3 = self.seeder.create_file(self.project_id, file_key)
        self.file_manager.delete_file(
            self.project_id, file_key, keep_latest_version=True
        )
        self._validate_file_not_found(self.project_id, file_key, version_1.version)
        self._validate_file_not_found(self.project_id, file_key, version_2.version)
        file = self.file_manager.get_file_metadata(self.project_id, file_key)
        assert file.version == version_3.version

    def test_delete_files(self) -> None:
        file_key = "delete-1.bin"
        self.seeder.create_file(self.project_id, file_key)
        self.seeder.create_file(self.project_id, file_key)
        file_key = "delete-2.bin"
        self.seeder.create_file(self.project_id, file_key)
        self.seeder.create_file(self.project_id, file_key)
        self.seeder.create_file(self.project_id, file_key)

        # Test - Delete all files including versions
        self.file_manager.delete_files(self.project_id)
        files = self.file_manager.list_files(self.project_id, include_versions=True)
        assert not files
        files = self.file_manager.list_files(
            self.project_id, include_versions=True, prefix="delete-1.bin"
        )
        assert not files
        files = self.file_manager.list_files(
            self.project_id, include_versions=True, prefix="delete-2.bin"
        )
        assert not files

        with pytest.raises(ResourceNotFoundError):
            self.file_manager.get_file_metadata(self.project_id, file_key)

        # Test - Try deleting an already deleted bucket
        self.file_manager.delete_files(self.project_id)
        files = self.file_manager.list_files(self.project_id, include_versions=True)
        assert not files

    def _validate_file_not_found(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> None:
        with pytest.raises(ResourceNotFoundError):
            self.file_manager.get_file_metadata(project_id, file_key, version)


@pytest.mark.skipif(
    not test_settings.MINIO_INTEGRATION_TESTS,
    reason="Minio Integration Tests are deactivated, use MINIO_INTEGRATION_TESTS to activate.",
)
@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestMinioFileManagerWithPostgres(FileOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        json_db = PostgresJsonDocumentManager(global_state, request_state)

        self._file_manager = MinioFileManager(
            ComponentManagerMock(global_state, request_state, json_db_manager=json_db)
        )
        self._seeder = SeedManager(
            ComponentManagerMock(
                global_state, request_state, file_manager=self._file_manager
            )
        )

        self._project_id = f"{randint(1, 100000)}-file-manager-test"
        self._bucket_name = get_bucket_name(self.project_id, settings.SYSTEM_NAMESPACE)
        yield
        # Cleanup project related entities
        delete_bucket(
            self._file_manager.client,
            self._bucket_name,
            force=True,
        )
        self._file_manager._json_db_manager.delete_json_collections(self.project_id)

    @property
    def file_manager(self) -> FileOperations:
        return self._file_manager

    @property
    def seeder(self) -> SeedOperations:
        return self._seeder

    @property
    def project_id(self) -> str:
        return self._project_id


@pytest.mark.skipif(
    not test_settings.AZURE_BLOB_INTEGRATION_TESTS,
    reason="Azure Blob Integration Tests are deactivated, use AZURE_BLOB_INTEGRATION_TESTS to activate.",
)
@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestAzureBlobFileManagerWithPostgres(FileOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        json_db = PostgresJsonDocumentManager(global_state, request_state)

        self._file_manager = AzureBlobFileManager(
            ComponentManagerMock(global_state, request_state, json_db_manager=json_db)
        )
        self._seeder = SeedManager(
            ComponentManagerMock(
                global_state, request_state, file_manager=self._file_manager
            )
        )

        self._project_id = f"{randint(1, 100000)}-file-manager-test"
        yield
        self._file_manager.delete_files(self.project_id)
        json_db.delete_json_collections(self.project_id)

    @property
    def file_manager(self) -> FileOperations:
        return self._file_manager

    @property
    def seeder(self) -> SeedOperations:
        return self._seeder

    @property
    def project_id(self) -> str:
        return self._project_id


@pytest.mark.skipif(
    not test_settings.MINIO_INTEGRATION_TESTS,
    reason="Minio Integration Tests are deactivated, use MINIO_INTEGRATION_TESTS to activate.",
)
@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestMinioFileManagerViaLocalEndpoints(FileOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self) -> Generator:
        from contaxy.api import app

        with TestClient(app=app, root_path="/") as test_client:
            self._test_client = test_client
            system_manager = SystemClient(self._test_client)
            self._json_db = JsonDocumentClient(self._test_client)
            self._auth_manager = AuthClient(self._test_client)
            self._file_manager = FileClient(self._test_client)
            self._seeder = SeedManager(
                ComponentManagerMock(file_manager=self._file_manager)
            )

            self._project_id = f"{randint(1, 100000)}-file-manager-test"
            system_manager.initialize_system()

            self.login_user(
                config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
            )
            yield
            # Login as admin again -> logged in user might have been changed
            self.login_user(
                config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
            )
            self._json_db.delete_json_collections(self._project_id)
            # TODO: Delete bucket

    @property
    def file_manager(self) -> FileOperations:
        return self._file_manager

    @property
    def seeder(self) -> SeedOperations:
        return self._seeder

    @property
    def project_id(self) -> str:
        return self._project_id

    def login_user(self, username: str, password: str) -> None:
        self._auth_manager.request_token(
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
class TestMinioFileManagerViaRemoteEndpoints(FileOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self, remote_client: requests.Session) -> Generator:
        self._endpoint_client = remote_client
        self._json_db = JsonDocumentClient(self._endpoint_client)
        self._auth_manager = AuthClient(self._endpoint_client)
        self._file_manager = FileClient(self._endpoint_client)
        self._seeder = SeedManager(
            ComponentManagerMock(file_manager=self._file_manager)
        )

        self._project_id = f"{randint(1, 100000)}-file-manager-test"

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        yield
        # Login as admin again -> logged in user might have been changed
        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        self._json_db.delete_json_collections(self._project_id)
        # TODO: Delete bucket

    @property
    def file_manager(self) -> FileOperations:
        return self._file_manager

    @property
    def seeder(self) -> SeedOperations:
        return self._seeder

    @property
    def project_id(self) -> str:
        """Returns the project id for the given run."""
        return self._project_id

    def login_user(self, username: str, password: str) -> None:
        self._auth_manager.request_token(
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
