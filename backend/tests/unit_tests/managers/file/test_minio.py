import hashlib
from random import randint
from typing import Generator

import pytest
from minio import Minio
from sqlalchemy.future import create_engine
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.file.minio import MinioFileManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.seed import SeedManager
from contaxy.schema import FileInput
from contaxy.schema.exceptions import ResourceNotFoundError
from contaxy.utils.file_utils import FormMultipartStream
from contaxy.utils.minio_utils import (  # delete_bucket,
    create_bucket,
    create_minio_client,
    get_bucket_name,
)
from contaxy.utils.postgres_utils import create_jsonb_merge_patch_func
from contaxy.utils.state_utils import GlobalState, RequestState
from tests.unit_tests.conftest import test_settings

from .data.metadata import file_data


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
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
    else:
        # TODO: Put in conftest
        assert settings.POSTGRES_CONNECTION_URI
        engine = create_engine(
            settings.POSTGRES_CONNECTION_URI,
            future=True,
        )
        create_jsonb_merge_patch_func(engine)
        json_db = PostgresJsonDocumentManager(global_state, request_state)
    return MinioFileManager(global_state, request_state, json_db)


@pytest.fixture()
def seeder(minio_file_manager: MinioFileManager) -> SeedManager:
    return SeedManager(file_manager=minio_file_manager)


@pytest.fixture(scope="session")
def minio_client() -> Minio:
    return create_minio_client(settings)


@pytest.fixture(scope="function")
def project_id(minio_client: Minio) -> Generator[str, None, None]:
    # Creates one project + bucket per test function
    project_id = f"{randint(1, 100000)}-file-manager-test"
    bucket_name = get_bucket_name(project_id, settings.SYSTEM_NAMESPACE)
    create_bucket(minio_client, bucket_name)
    yield project_id
    # TODO: Fix bucket deletion
    # delete_bucket(
    #     minio_client,
    #     get_bucket_name(project_id, settings.SYSTEM_NAMESPACE),
    #     force=True,
    # )


@pytest.mark.skipif(
    test_settings.MINIO_INTEGRATION_TESTS is None,
    reason="Minio Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestMinioFileManager:
    @pytest.mark.parametrize("metadata", file_data)
    def test_upload_and_list_files(
        self,
        minio_file_manager: MinioFileManager,
        project_id: str,
        metadata: dict,
    ) -> None:

        filename = metadata.get("filename")
        assert filename
        file_path = metadata.get("multipart_file_path")
        assert file_path

        with open(file_path, "rb") as file_stream:
            # TODO: Replace use seeder
            multipart_stream = FormMultipartStream(
                file_stream, metadata.get("headers"), form_field="file", hash_algo="md5"
            )

            uploaded_file = minio_file_manager.upload_file(
                project_id,
                filename,
                multipart_stream,
                multipart_stream.content_type,
            )

            # TODO: Enhance
            assert uploaded_file.key == metadata.get("filename")
            assert uploaded_file.key == uploaded_file.display_name
            assert uploaded_file.content_type == multipart_stream.content_type
            assert uploaded_file.md5_hash == multipart_stream.hash
            assert uploaded_file.version in uploaded_file.available_versions

            listed_file = minio_file_manager.list_files(project_id, prefix=filename)[0]
            assert listed_file
            assert uploaded_file == listed_file

            read_file = minio_file_manager.get_file_metadata(project_id, filename)
            assert listed_file == read_file

            # Update metadata
            exp_description = "Updated description"
            exp_metadata = {"source": "http://fc.de"}
            updates = FileInput(
                key=filename, description=exp_description, metadata=exp_metadata
            )
            updated_file = minio_file_manager.update_file_metadata(
                updates, project_id, filename
            )
            assert updated_file != uploaded_file
            assert updated_file.description == exp_description
            # TODO: Fix
            # assert updated_file.metadata == exp_metadata

            # Download
            file_stream = minio_file_manager.download_file(project_id, filename)
            actual_hash = hashlib.md5()
            for chunk in file_stream:
                actual_hash.update(chunk)

            assert actual_hash.hexdigest() == multipart_stream.hash

            try:
                minio_file_manager.download_file("invalid-project", filename)
                assert False
            except ResourceNotFoundError:
                pass

            try:
                minio_file_manager.download_file(project_id, "invalid-file")
                assert False
            except ResourceNotFoundError:
                pass

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
        assert len(file_versions[0].available_versions) == 2
        assert (
            file_versions[0].available_versions == file_versions[1].available_versions
        )

        # Test - Recursive
        # TODO

    def test_get_file_metadata(
        self, minio_file_manager: MinioFileManager, project_id: str, seeder: SeedManager
    ) -> None:

        version_1 = seeder.create_file(project_id)
        version_2 = seeder.create_file(project_id)

        # Test - File does not exsists
        try:
            minio_file_manager.get_file_metadata(project_id, "invalid-file")
            assert False
        except ResourceNotFoundError:
            pass

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
        self, minio_file_manager: MinioFileManager, project_id: str
    ) -> None:
        # Test - File does not exsists
        # try:
        #     minio_file_manager.update_file_metadata(
        #         FileInput(key="invalid-file"), project_id, "invalid-file"
        #     )
        #     assert False
        # except ResourceNotFoundError:
        #     pass

        # Test - File exists

        #    -- Update latest version

        #    -- Update specific

        pass

    def test_upload_file(self, minio_file_manager: MinioFileManager) -> None:
        # File exists

        # File does not exist

        # Bucket does not exist
        pass

    def test_download_file(self, minio_file_manager: MinioFileManager) -> None:
        # File exists

        # File does not exist

        # Bucket does not exist
        pass

    def test_delete_file(self, minio_file_manager: MinioFileManager) -> None:
        # File does not exist

        # File exists

        # - Multiple versions and no version specified

        # - Multiple versions and version specified

        pass
