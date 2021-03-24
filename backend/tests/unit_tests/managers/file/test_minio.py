import hashlib
from random import randint
from typing import Generator

import pytest
from minio import Minio
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.file.minio import MinioFileManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.schema import File, FileInput
from contaxy.schema.exceptions import ResourceNotFoundError
from contaxy.utils.file_utils import FormMultipartStream
from contaxy.utils.minio_utils import (
    create_minio_client,
    delete_bucket,
    get_bucket_name,
)
from contaxy.utils.state_utils import GlobalState, RequestState

from .data.metadata import file_data


# TODO: Put in global conftest
@pytest.fixture(scope="session")
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
    json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
    return MinioFileManager(global_state, request_state, json_db)


@pytest.fixture(scope="session")
def minio_client() -> Minio:
    return create_minio_client(settings)


@pytest.fixture(scope="session")
def project_id(minio_client: Minio) -> Generator[str, None, None]:
    project_id = f"{randint(1, 10000)}-file-manager-test"
    yield project_id
    delete_bucket(
        minio_client,
        get_bucket_name(project_id, settings.SYSTEM_NAMESPACE),
        force=True,
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
            assert updated_file.metadata == exp_metadata

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

    def test_update_file_metadata(self, minio_file_manager: MinioFileManager) -> None:
        # File does not exsists

        # File exists

        # - Update latest version

        # - Update specific

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
