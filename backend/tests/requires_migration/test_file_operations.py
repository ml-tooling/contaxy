import hashlib
from random import randint
from typing import Generator, Optional

import pytest
from minio import Minio
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.file.minio import MinioFileManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.seed import SeedManager
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema import FileInput
from contaxy.schema.exceptions import ResourceNotFoundError
from contaxy.utils.minio_utils import (
    create_minio_client,
    delete_bucket,
    get_bucket_name,
)
from contaxy.utils.state_utils import GlobalState, RequestState

from ..conftest import test_settings


@pytest.fixture()
def global_state() -> GlobalState:
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    return RequestState(State())


@pytest.fixture()
def minio_file_manager(
    global_state: GlobalState, request_state: RequestState
) -> MinioFileManager:
    if not test_settings.POSTGRES_INTEGRATION_TESTS:
        json_db: JsonDocumentOperations = InMemoryDictJsonDocumentManager(
            global_state, request_state
        )
    else:
        json_db = PostgresJsonDocumentManager(global_state, request_state)
    return MinioFileManager(global_state, request_state, json_db)


@pytest.fixture()
def seeder(minio_file_manager: MinioFileManager) -> SeedManager:
    return SeedManager(file_manager=minio_file_manager)


@pytest.fixture(scope="session")
def minio_client() -> Minio:
    return create_minio_client(settings)


@pytest.fixture(scope="function")
def project_id(minio_file_manager: MinioFileManager) -> Generator[str, None, None]:
    project_id = f"{randint(1, 100000)}-file-manager-test"
    bucket_name = get_bucket_name(project_id, settings.SYSTEM_NAMESPACE)
    yield project_id
    # Cleanup project related entities
    if test_settings.MINIO_INTEGRATION_TESTS:
        delete_bucket(
            minio_file_manager.client,
            bucket_name,
            force=True,
        )
    if test_settings.POSTGRES_INTEGRATION_TESTS:
        jdm = minio_file_manager.json_db_manager
        jdm.delete_json_collections(project_id)


@pytest.mark.skipif(
    test_settings.MINIO_INTEGRATION_TESTS is None,
    reason="Minio Integration Tests are deactivated, use MINIO_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestMinioFileManager:
    def test_list_files(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:
        number_of_files = 3

        prefix_1 = "test-file"
        files_prefix_1 = seeder.create_files(project_id, number_of_files, prefix_1)
        prefix_2 = "file-test"
        files_prefix_2 = seeder.create_files(project_id, number_of_files, prefix_2)

        # Test - No files to selection
        result = minio_file_manager.list_files(project_id, prefix="no-files")
        assert not result

        # Test - List all files
        result = minio_file_manager.list_files(project_id)
        files_1 = list(filter(lambda file: file.key.startswith(prefix_1), result))
        files_2 = list(filter(lambda file: file.key.startswith(prefix_2), result))
        assert len(files_1) == len(files_prefix_1) and len(files_2) == len(
            files_prefix_2
        )

        # Test - By prefix
        result = minio_file_manager.list_files(project_id, prefix=prefix_1)
        files_1 = list(filter(lambda file: file.key.startswith(prefix_1), result))
        files_2 = list(filter(lambda file: file.key.startswith(prefix_2), result))
        assert len(files_1) == len(files_prefix_1) and not files_2

        # Test - Include versions and validate available versions metadata
        update_file = files_prefix_1[0]
        seeder.create_file(project_id, update_file.key)
        result = minio_file_manager.list_files(project_id, include_versions=True)
        file_versions = list(filter(lambda file: file.key == update_file.key, result))
        assert file_versions
        assert len(file_versions[0].available_versions) == 2
        assert (
            file_versions[0].available_versions == file_versions[1].available_versions
        )

        # Test - Recursive
        # TODO

        # Test - Externally uploaded file

    def test_get_file_metadata(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:
        version_1 = seeder.create_file(project_id)
        version_2 = seeder.create_file(project_id)

        # Test - File does not exsists
        self._validate_file_not_found(minio_file_manager, project_id, "invalid-file")

        # Test - File exists
        #     -- Get latest version
        result_v2 = minio_file_manager.get_file_metadata(project_id, version_1.key)
        assert result_v2.version == version_2.version
        assert result_v2.version != version_1.version
        assert len(result_v2.available_versions) == 2

        #     -- Get specific version
        result_v1 = minio_file_manager.get_file_metadata(
            project_id, version_1.key, version_1.version
        )
        assert result_v1.version == version_1.version
        assert len(result_v2.available_versions) == 2

    def test_update_file_metadata(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:
        version_1 = seeder.create_file(project_id)
        version_2 = seeder.create_file(project_id)

        # Test - File does not exsists
        try:
            minio_file_manager.update_file_metadata(
                FileInput(key="invalid-file"), project_id, "invalid-file"
            )
            assert False
        except ResourceNotFoundError:
            pass

        # Test - File exists
        #    -- Update latest version
        exp_description = "Updated description"
        exp_metadata = {"source": "http://fc.de"}
        updates = FileInput(
            key=version_1.key, description=exp_description, metadata=exp_metadata
        )
        updated_file = minio_file_manager.update_file_metadata(
            updates, project_id, version_1.key
        )
        assert updated_file.version == version_2.version
        assert updated_file != version_1
        assert updated_file.description == exp_description
        assert updated_file.metadata == exp_metadata
        version_1 = minio_file_manager.get_file_metadata(
            project_id, version_1.key, version_1.version
        )
        assert updated_file.description != version_1.description
        assert updated_file.metadata != version_1.metadata
        #    -- Update specific
        updated_file = minio_file_manager.update_file_metadata(
            updates, project_id, version_1.key, version_1.version
        )
        assert updated_file.version == version_1.version
        assert updated_file.description == exp_description
        assert updated_file.metadata == exp_metadata

    def test_upload_file(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:
        file_stream = seeder.create_file_stream()
        file_key = "my-test.bin"

        # Test - File does not exist
        version_1 = minio_file_manager.upload_file(project_id, file_key, file_stream)
        assert version_1.md5_hash == file_stream.hash
        assert version_1.key == file_key

        # Test - File exists
        file_stream = seeder.create_file_stream()
        version_2 = minio_file_manager.upload_file(project_id, file_key, file_stream)
        assert version_1.version != version_2.version
        assert version_2.md5_hash == file_stream.hash

        # Test - Bucket does not exist
        # TODO

    def test_download_file(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:
        file_key = "test-download-file.bin"
        version_1 = seeder.create_file(project_id, file_key)
        version_2 = seeder.create_file(project_id, file_key)

        # Test - File does not exist
        try:
            minio_file_manager.download_file(project_id, "invalid-key")
            assert False
        except ResourceNotFoundError:
            pass

        # Test - File exists
        #     -- Latest version
        hash = hashlib.md5()
        file_stream = minio_file_manager.download_file(project_id, file_key)
        for chunk in file_stream:
            hash.update(chunk)
        assert version_2.md5_hash == hash.hexdigest()

        #     -- Specific version
        hash = hashlib.md5()
        file_stream = minio_file_manager.download_file(
            project_id, file_key, version_1.version
        )
        for chunk in file_stream:
            hash.update(chunk)
        assert version_1.md5_hash == hash.hexdigest()

        # Test - Bucket does not exist
        # TODO
        pass

    def test_delete_file(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:

        # Test - File does not exist
        minio_file_manager.delete_file(project_id, "invalid-key")

        # File exists
        file = seeder.create_file(project_id)
        minio_file_manager.delete_file(project_id, file.key)
        self._validate_file_not_found(minio_file_manager, project_id, file.key)

        # Test - Multiple versions and no version specified
        file_key = "delete-1.bin"
        version_1 = seeder.create_file(project_id, file_key)
        version_2 = seeder.create_file(project_id, file_key)
        minio_file_manager.delete_file(project_id, file_key)
        self._validate_file_not_found(minio_file_manager, project_id, file_key)

        # Test - Multiple versions and version specified
        file_key = "delete-2.bin"
        version_1 = seeder.create_file(project_id, file_key)
        version_2 = seeder.create_file(project_id, file_key)
        version_3 = seeder.create_file(project_id, file_key)

        #      -- Delete latest
        minio_file_manager.delete_file(project_id, file_key, version_3.version)
        self._validate_file_not_found(
            minio_file_manager, project_id, file_key, version_3.version
        )
        file = minio_file_manager.get_file_metadata(project_id, file_key)
        assert file.version == version_2.version

        #      -- Delete oldest
        minio_file_manager.delete_file(project_id, file_key, version_1.version)
        self._validate_file_not_found(
            minio_file_manager, project_id, file_key, version_1.version
        )
        file = minio_file_manager.get_file_metadata(project_id, file_key)
        assert file.version == version_2.version

        # Test - Keep latest version
        file_key = "delete-3.bin"
        version_1 = seeder.create_file(project_id, file_key)
        version_2 = seeder.create_file(project_id, file_key)
        version_3 = seeder.create_file(project_id, file_key)
        minio_file_manager.delete_file(project_id, file_key, keep_latest_version=True)
        self._validate_file_not_found(
            minio_file_manager, project_id, file_key, version_1.version
        )
        self._validate_file_not_found(
            minio_file_manager, project_id, file_key, version_2.version
        )
        file = minio_file_manager.get_file_metadata(project_id, file_key)
        assert file.version == version_3.version

    def _validate_file_not_found(
        self,
        minio_file_manager: MinioFileManager,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> None:
        try:
            minio_file_manager.get_file_metadata(project_id, file_key, version)
            assert False
        except ResourceNotFoundError:
            pass
