import json
import os
from typing import Dict, Iterator, List, Optional, Tuple

from loguru import logger
from minio import Minio
from minio.datatypes import Object as MinioObject
from minio.error import S3Error
from starlette.responses import Response

from contaxy.operations import FileOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema import File, FileInput, ResourceAction
from contaxy.schema.exceptions import (
    ClientValueError,
    ResourceNotFoundError,
    ServerBaseError,
)
from contaxy.schema.json_db import JsonDocument
from contaxy.utils.file_utils import FileStream, generate_file_id
from contaxy.utils.minio_utils import (
    create_bucket,
    create_minio_client,
    get_bucket_name,
)
from contaxy.utils.state_utils import GlobalState, RequestState


class MinioFileManager(FileOperations):

    DOC_COLLECTION_NAME = "s3_files"
    METADATA_FIELD_SET = {
        "key",
        "external_id",
        "md5_hash",
        "description",
        "content_type",
        "metadata",
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
        self.sys_namespace = self.global_state.settings.SYSTEM_NAMESPACE

    def list_files(
        self,
        project_id: str,
        recursive: bool = True,
        include_versions: bool = False,
        prefix: Optional[str] = None,
    ) -> List[File]:
        # TODO: Test case when object is folder

        bucket_name = get_bucket_name(project_id, self.sys_namespace)

        file_data, document_keys = self._load_file_data_from_s3(
            bucket_name, prefix, recursive, include_versions
        )

        file_data, docs_not_in_db = self._enrich_data_from_db(
            project_id, file_data, document_keys
        )

        # Usually each file should have a corresponding db entry with some meta data.
        # This might not be the case, if someone manually added a file to S3.
        # TODO: Consider conflict handling
        for key, json_doc in docs_not_in_db:
            self.json_db_manager.create_json_document(
                project_id, self.DOC_COLLECTION_NAME, key, json_doc
            )

        return file_data

    def get_file_metadata(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        """Get file metadata of a single file.

        If no version is provided then the latest version will be returned.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.

        Raises:
            ResourceNotFoundError: If no file is found.

        Returns:
            File: The file metadata object.
        """

        file_data = self.list_files(
            project_id, prefix=file_key, include_versions=True if version else False
        )

        for file in file_data:
            if not version or (file.version == version):
                return file

        msg = f"File not found (key: {file_key}"
        msg = f"{msg}, version {version})." if version else f"{msg})."
        raise ResourceNotFoundError(msg)

    def update_file_metadata(
        self,
        file: FileInput,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        """Update the file metadata.

        If no version is provided then the latest version will be returned. Moreover, additional custom metadata provied via `file.metadata` will executed with json merge patch strategy in case a specific version is updated. But if a new version was created it is treated as a new file and hence the metadata from older versions will not be considered. If a version should inherit the metadata from a previous version, then this data needs to be set explictly.

        Args:
            file (FileInput): The file metadata object. All unset attributes or None values will be ignored.
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.

        Raises:
            ClientValueError: If the provided keys do not match.

        Returns:
            File: The updated file metadata object.
        """

        if file.key != file_key:
            raise ClientValueError(
                f"File keys do not match (file_key: {file_key}, file.key {file.key})"
            )

        s3_object = self.client.stat_object(
            get_bucket_name(project_id, self.global_state.settings.SYSTEM_NAMESPACE),
            file_key,
            version,
        )

        data = file.dict(
            include=self.METADATA_FIELD_SET, exclude_none=True, exclude_unset=True
        )
        json_value = json.dumps(data)

        doc_key = generate_file_id(file_key, s3_object.version_id)

        try:
            self.json_db_manager.update_json_document(
                project_id, self.DOC_COLLECTION_NAME, doc_key, json_value
            )
        except ResourceNotFoundError:
            # Lazily create and update a metadata entry in the DB, since the resource mmight be uploaded externally
            self._create_file_metadata_json_document(
                project_id, file_key, s3_object.version_id
            )
            self.json_db_manager.update_json_document(
                project_id, self.DOC_COLLECTION_NAME, doc_key, json_value
            )

        return self.get_file_metadata(project_id, file_key, s3_object.version_id)

    def upload_file(
        self,
        project_id: str,
        file_key: str,
        file_stream: FileStream,
        content_type: str = "application/octet-stream",
    ) -> File:

        logger.debug(
            f"Upload file (`project_id`: {project_id}, `file_key`: {file_key})"
        )

        # Todo: Handle further metadata: creation, disabled, tags, icon, userdata, extension_id
        bucket_name = get_bucket_name(project_id, self.sys_namespace)

        if not self.client.bucket_exists(bucket_name):
            # This can not be done lazily because put_object still consumes the stream although the bucket does not exists yet
            logger.debug(f"No bucket existing for project {project_id}.")
            create_bucket(self.client, bucket_name)

        try:
            result = self.client.put_object(
                bucket_name,
                file_key,
                file_stream,
                -1,
                content_type,
                part_size=10 * 1024 * 1024,
            )
        except S3Error as err:
            raise ServerBaseError(
                f"The file {file_key} could not be uploaded ({err.code})."
            )

        # ? Get the data from the last version if existing?
        self._create_file_metadata_json_document(
            project_id, file_key, result.version_id, file_stream.hash
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

    def _create_client(self) -> Minio:
        settings = self.global_state.settings
        state_namespace = self.request_state[MinioFileManager]
        if not state_namespace.client:
            state_namespace.client = create_minio_client(self.global_state.settings)
            logger.info(
                f"Minio client created (endpoint: {settings.S3_ENDPOINT}, region: {settings.S3_REGION}, secure: {settings.S3_SECURE})"
            )
        return state_namespace.client

    def _create_file_metadata_json_document(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        md5_hash: Optional[str] = None,
    ) -> JsonDocument:
        s3_object = self.client.stat_object(
            get_bucket_name(project_id, self.global_state.settings.SYSTEM_NAMESPACE),
            file_key,
            version_id=version,
        )
        meta_file = self._map_s3_object_to_file_model(s3_object)
        if md5_hash:
            meta_file.md5_hash = md5_hash
        metadata_json = self._map_file_obj_to_json_document(meta_file)
        return self.json_db_manager.create_json_document(
            project_id,
            self.DOC_COLLECTION_NAME,
            meta_file.id,  # type: ignore
            metadata_json,
        )

    def _map_s3_object_to_file_model(self, object: MinioObject) -> File:
        # Todo: Check if directory can be given and what the implications are. Do we want to list such? (see object.is_dir param)
        file_extension = os.path.splitext(object.object_name)[1]
        display_name = os.path.basename(object.object_name)
        data = {
            "id": generate_file_id(object.object_name, object.version_id),
            "external_id": object.object_name,
            "key": object.object_name,
            "display_name": display_name,
            "updated_at": object.last_modified,
            "file_extension": file_extension,
            "file_size": object.size,
            "etag": object.etag,
            "latest_version": object.is_latest,
            "version": object.version_id,
        }

        # ! Minio seems to not set the content type, only when reading single object via stat_object, hence we persist it in the db
        if object.content_type:
            data.update({"content_type": object.content_type})
        return File(**data)

    def _map_file_obj_to_json_document(self, file: File) -> str:
        # Todo: Handle creation metadata. Problem: Each version is actually a new object and gets a dedicated db entry. Use list_objects or direct lookup in the DB?
        json_data = json.dumps(
            file.dict(include=self.METADATA_FIELD_SET, exclude_none=True),
            default=str,
        )
        return json_data

    def _load_file_data_from_s3(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        recursive: Optional[bool] = None,
        include_version: Optional[bool] = None,
    ) -> Tuple[List[File], List[str]]:
        # TODO: Currently the available version field is always set and thus all versions are internally read everytime. Decide what is the desired behavior here.

        file_data: List[File] = []
        db_keys: List[str] = []
        file_versions: Dict[str, List[str]] = {}

        try:
            objects: List[MinioObject] = self.client.list_objects(
                bucket_name,
                prefix,
                recursive,
                include_version=True,
                include_user_meta=True,
            )

            for obj in objects:
                file = self._map_s3_object_to_file_model(obj)
                if include_version or file.latest_version:
                    file_data.append(file)
                    # ? The DB Keys might be added always in order to improve syncing between S3 and DB. But this would imply to read all versions from the DB everytime, even when versions arent requested by the user.
                    db_keys.append(str(file.id))

                versions = file_versions.get(file.key, [])
                file_versions.update({file.key: versions + [str(file.version)]})

            if not file_data:
                return [], []

        except S3Error as err:
            if err.code == "NoSuchBucket":
                create_bucket(self.client, bucket_name)
                return [], []

        for file in file_data:
            file.available_versions = file_versions.get(file.key)

        return file_data, db_keys

    def _enrich_data_from_db(
        self, project_id: str, file_data: List[File], document_keys: List[str]
    ) -> Tuple[List[File], List[Dict[str, str]]]:

        json_docs = self.json_db_manager.list_json_documents(
            project_id, self.DOC_COLLECTION_NAME, keys=document_keys
        )

        # Create dict for efficient lookups
        doc_dict: Dict[str, JsonDocument] = {}
        for doc in json_docs:
            doc_dict.update({doc.key: doc})

        docs_not_in_db: List[Dict[str, str]] = []
        for file in file_data:
            doc_of_file = doc_dict.get(str(file.id))
            if doc_of_file:
                file = self._add_data_from_doc_to_file(file, doc_of_file)
            else:
                json_doc = self._map_file_obj_to_json_document(file)
                docs_not_in_db.append({str(file.id): json_doc})

        return file_data, docs_not_in_db

    def _add_data_from_doc_to_file(self, file: File, doc: JsonDocument) -> File:
        json_dict = json.loads(doc.json_value)
        for metadata_field in self.METADATA_FIELD_SET:
            value = json_dict.get(metadata_field)
            if not value:
                logger.debug(
                    f"The file metadata field {metadata_field} is not in the respective json document."
                )
                continue
            file.__setattr__(metadata_field, value)
        return file
