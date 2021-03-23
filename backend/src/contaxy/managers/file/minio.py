import json
import os
from typing import Iterator, List, Optional

from loguru import logger
from minio import Minio
from minio.datatypes import Object as MinioObject
from starlette.responses import Response
from urllib3.exceptions import MaxRetryError

from contaxy.operations import FileOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema import File, FileInput, ResourceAction
from contaxy.schema.exceptions import ServerBaseError
from contaxy.utils.file_utils import FileStream, generate_file_id
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

        logger.debug(
            f"Upload file (`project_id`: {project_id}, `file_key`: {file_key} )"
        )

        # Todo: Handle further metadata: creation, disabled, tags, icon, userdata, extension_id
        bucket_name = self.get_bucket_name(project_id)
        result = self.client.put_object(
            bucket_name,
            file_key,
            file_stream,
            -1,
            content_type,
            part_size=10 * 1024 * 1024,
        )

        object_stats = self.client.stat_object(
            bucket_name, file_key, version_id=result.version_id
        )

        file = self._map_s3_object_to_file_model(object_stats)
        file.md5_hash = file_stream.hash

        # ? Get the data from the last version if existing?
        json_doc = self._create_metadata_json_docuemnt(file)
        self.json_db_manager.create_json_document(
            project_id, self.DOC_COLLECTION_NAME, str(file.id), json_doc
        )

        # This is necessary in order to have the available versions metadata set
        file = self.list_files(project_id, False, False, file_key)[0]
        return file

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

    def get_bucket_name(self, project_id: str) -> str:
        # Todo: Replace depending on actual prefix handling
        bucket_prefix = self.global_state.settings.SYSTEM_NAMESPACE
        return project_id if not bucket_prefix else f"{bucket_prefix}.{project_id}"

    def _create_client(self) -> Minio:
        settings = self.global_state.settings
        state_namespace = self.request_state[MinioFileManager]
        if not state_namespace.client:
            client = Minio(
                endpoint=settings.S3_ENDPOINT,
                access_key=settings.S3_ACCESS_KEY,
                secret_key=settings.S3_SECRET_KEY,
                region=settings.S3_REGION,
                secure=settings.S3_SECURE,
            )

            try:
                if not client.bucket_exists("nonexistingbucket"):
                    logger.debug("Object storage connected")
            except MaxRetryError:
                logger.critical(
                    "Could not connect to object storage (endpoint: {settings.S3_ENDPOINT}, region: {settings.S3_REGION}, secure: {settings.S3_SECURE})"
                )
                raise ServerBaseError("Could not connect to object storage")

            state_namespace.client = client
            logger.info(
                f"Minio client created (endpoint: {settings.S3_ENDPOINT}, region: {settings.S3_REGION}, secure: {settings.S3_SECURE})"
            )
        return state_namespace.client

    def _map_s3_object_to_file_model(self, object: MinioObject) -> File:
        # Todo: Check if directory can be given and what the implications are. Do we want to list such? (see object.is_dir param)
        file_extension = os.path.splitext(object.object_name)[1]
        display_name = os.path.basename(object.object_name)
        data = {
            "id": generate_file_id(object.object_name, object.version_id),
            "external_id": object.object_name,
            "key": object.object_name,
            "display_name": display_name,
            # ! Minio seems to not set the content type, only when reading single object via stat_object, hence we persist it in the db
            # "content_type": object.content_type,
            "updated_at": object.last_modified,
            "file_extension": file_extension,
            "file_size": object.size,
            "etag": object.etag,
            "latest_version": object.is_latest,
            "version": object.version_id,
        }
        return File(**data)

    def _create_metadata_json_docuemnt(self, file: File) -> str:
        # Todo: Handle creation metadata. Problem: Each version is actually a new object and gets a dedicated db entry. Use list_objects or direct lookup in the DB?
        json_data = json.dumps(
            file.dict(include=self.METADATA_FIELD_SET, exclude_none=True),
            default=str,
        )
        return json_data
