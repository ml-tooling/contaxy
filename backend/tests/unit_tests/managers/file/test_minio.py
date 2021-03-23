from random import randint

import pytest
from minio import Minio
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.file.minio import MinioFileManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
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


@pytest.mark.integration
class TestMinioFileManager:
    def test_get_file_metadata(self, minio_file_manager: MinioFileManager) -> None:
        pass

    def test_update_file_metadata(self, minio_file_manager: MinioFileManager) -> None:
        pass

    @pytest.mark.parametrize("metadata", file_data)
    def test_upload_and_list_files(
        self, minio_file_manager: MinioFileManager, minio_client: Minio, metadata: dict
    ) -> None:

        project_id = f"{randint(1, 10000)}-file-manager-test"

        with open(str(metadata.get("multipart_file_path")), "rb") as file_stream:
            multipart_stream = FormMultipartStream(
                file_stream, metadata.get("headers"), form_field="file", hash_algo="md5"
            )

            file = minio_file_manager.upload_file(
                project_id,
                metadata.get("filename"),
                multipart_stream,
                multipart_stream.content_type,
            )

            # TODO: Enhance
            assert file.key == metadata.get("filename")
            assert file.key == file.display_name
            assert file.content_type == multipart_stream.content_type
            assert file.md5_hash == multipart_stream.hash

        delete_bucket(
            minio_client,
            get_bucket_name(project_id, settings.SYSTEM_NAMESPACE),
            force=True,
        )

    def test_download_file(self, minio_file_manager: MinioFileManager) -> None:
        pass

    def test_delete_file(self, minio_file_manager: MinioFileManager) -> None:
        pass
