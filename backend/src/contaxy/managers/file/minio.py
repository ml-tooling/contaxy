from typing import Iterator, List, Optional

from loguru import logger
from minio import Minio
from starlette.responses import Response
from urllib3.exceptions import MaxRetryError

from contaxy.operations import FileOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema import File, FileInput, ResourceAction
from contaxy.schema.exceptions import ServerBaseError
from contaxy.utils.file_utils import FileStream
from contaxy.utils.state_utils import GlobalState, RequestState


class MinioFileManager(FileOperations):

    DOC_COLLECTION_NAME = "s3_files"
    METADATA_FIELD_SET = {
        "key",
        "external_id",
        "md5_hash",
        "description",
        "content_type",
        "additional_metadata",
        "disabled",
        "icon",
        "display_name",
        "tags",
    }

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
    ):
        """Initializes the Minio File Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
        """
        self.global_state = global_state
        self.request_state = request_state
        self.json_db_manager = json_db_manager
        self.client = self._create_client()

    def list_files(
        self,
        project_id: str,
        recursive: bool = True,
        include_versions: bool = False,
        prefix: Optional[str] = None,
    ) -> List[File]:
        pass

    def get_file_metadata(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        pass

    def update_file_metadata(
        self,
        file: FileInput,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        pass

    def upload_file(
        self,
        project_id: str,
        file_key: str,
        file_stream: FileStream,
        content_type: str = "application/octet-stream",
    ) -> File:
        pass

    def download_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> Iterator[bytes]:
        pass

    def list_file_actions(
        self, project_id: str, file_key: str, version: Optional[str] = None
    ) -> ResourceAction:
        pass

    def execute_file_action(
        self,
        project_id: str,
        file_key: str,
        action_id: str,
        version: Optional[str] = None,
    ) -> Response:
        pass

    def delete_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        keep_latest_version: bool = False,
    ) -> None:
        pass
