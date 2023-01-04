import json
import logging
import os
from datetime import datetime
from typing import IO, Dict, Iterator, List, Optional, Tuple

from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.exceptions import ResourceNotFoundError as AzureResourceNotFoundError
from azure.storage.blob import (
    BlobClient,
    BlobProperties,
    BlobServiceClient,
    ContentSettings,
)
from loguru import logger
from starlette.responses import Response

from contaxy.config import Settings
from contaxy.operations import FileOperations
from contaxy.operations.components import ComponentOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema import File, FileInput, ResourceAction
from contaxy.schema.exceptions import ResourceNotFoundError, ServerBaseError
from contaxy.schema.json_db import JsonDocument
from contaxy.utils.file_utils import generate_file_id


def get_container_name(project_id: str, prefix: str) -> str:
    return project_id if not prefix else f"{prefix}-{project_id}"


def create_azure_blob_client(settings: Settings) -> BlobServiceClient:
    try:
        # Disable detailed http request logging of azure storage client
        azure_logger = logging.getLogger(
            "azure.core.pipeline.policies.http_logging_policy"
        )
        azure_logger.setLevel(logging.WARNING)
        assert (
            settings.AZURE_BLOB_CONNECTION_STRING
        ), "AZURE_BLOB_CONNECTION_STRING must be set to create an azure blob client!"
        client: BlobServiceClient = BlobServiceClient.from_connection_string(
            settings.AZURE_BLOB_CONNECTION_STRING,
            settings.AZURE_BLOB_TOKEN,
        )
        client.get_account_information()
    except AzureError:
        logger.critical(
            f"Could not connect to Azure object storage ({settings.AZURE_BLOB_CONNECTION_STRING})."
        )
        raise ServerBaseError(
            "Could not connect to object storage. Check Azure object storage endpoint configuration."
        )
    return client


class AzureBlobFileManager(FileOperations):
    DOC_COLLECTION_NAME = "azure_blob_files"
    METADATA_FIELD_SET = {
        "key",
        "external_id",
        "md5_hash",
        "description",
        "metadata",
        "disabled",
        "icon",
        "display_name",
        "tags",
    }

    def __init__(
        self,
        component_manager: ComponentOperations,
    ):
        """Initializes the Azure Blob File Manager.

        Args:
            component_manager: Instance of the component manager that grants access to the other managers.
        """
        self._global_state = component_manager.global_state
        self._request_state = component_manager.request_state
        self._component_manager = component_manager
        self.client = self._create_client()
        self.sys_namespace = self._global_state.settings.SYSTEM_NAMESPACE

    @property
    def json_db_manager(self) -> JsonDocumentOperations:
        return self._component_manager.get_json_db_manager()

    def list_files(
        self,
        project_id: str,
        recursive: bool = True,
        include_versions: bool = False,
        prefix: Optional[str] = None,
    ) -> List[File]:
        """List files.

        Args:
            project_id (str): Project ID associated with the file.
            recursive (bool, optional): List recursively as directory structure emulation. Defaults to True.
            include_versions (bool, optional): Flag to control whether include object versions. Defaults to False.
            prefix (Optional[str], optional): File key starts with prefix. Defaults to None.

        Returns:
            List[File]: List of file metadata objects.
        """

        # TODO: Test case when object is folder
        logger.debug(
            f"list_files (`project_id`: {project_id}, `recursive`: {recursive}, `include_versions`: {include_versions}, `prefix`: {prefix})."
        )

        if not recursive:
            logger.warning(
                "The parameter 'recursive' of function 'list_files' is set to False, "
                "but the AzureBlobFileManager always lists all files in all sub-folders."
            )

        container_name = get_container_name(project_id, self.sys_namespace)

        file_data, document_keys = self._load_file_data_from_azure(
            container_name, prefix, include_versions
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
        logger.debug(
            f"get_file_metadata (`project_id`: {project_id}, `file_key`: {file_key}, `version`: {version})"
        )

        files_to_prefix = self.list_files(
            project_id, prefix=file_key, include_versions=True if version else False
        )

        file_versions = filter(lambda file: file.key == file_key, files_to_prefix)

        for file in file_versions:
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
        logger.debug(
            f"update_file_metadata (`project_id`: {project_id}, `file_key`: {file_key}, `version`: {version})"
        )

        azure_blob_client: BlobClient = self.client.get_blob_client(
            get_container_name(
                project_id, self._global_state.settings.SYSTEM_NAMESPACE
            ),
            file_key,
        )
        try:
            azure_blob = azure_blob_client.get_blob_properties(version_id=version)
        except AzureResourceNotFoundError as e:
            raise ResourceNotFoundError(
                f"Invalid file {file_key} (version: {version}."
            ) from e

        data = file.dict(
            include=self.METADATA_FIELD_SET, exclude_none=True, exclude_unset=True
        )
        # TODO: Fix metadata creation
        json_value = json.dumps(data)

        doc_key = generate_file_id(file_key, azure_blob.version_id)

        try:
            self.json_db_manager.update_json_document(
                project_id, self.DOC_COLLECTION_NAME, doc_key, json_value
            )
        except ResourceNotFoundError:
            # Lazily create and update a metadata entry in the DB, since the resource might be uploaded externally
            self._create_file_metadata_json_document(
                project_id, azure_blob, metadata=None
            )
            self.json_db_manager.update_json_document(
                project_id, self.DOC_COLLECTION_NAME, doc_key, json_value
            )

        return self.get_file_metadata(project_id, file_key, azure_blob.version_id)

    def upload_file(
        self,
        project_id: str,
        file_key: str,
        file_stream: IO[bytes],
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ) -> File:
        """Upload a file.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            file_stream (IO[bytes]): The actual file stream object.
            metadata (Dict, optional): Additional key-value pairs of file meta data
            content_type (str, optional): The mime-type of the file. Defaults to "application/octet-stream".

        Raises:
            ServerBaseError: If the upload failed.

        Returns:
            File: The file metadata object of the uploaded file.
        """

        logger.debug(
            f"upload_file (`project_id`: {project_id}, `file_key`: {file_key})"
        )

        # Todo: Handle further metadata: creation, disabled, tags, icon, userdata, extension_id
        container_name = get_container_name(project_id, self.sys_namespace)

        container_client = self.client.get_container_client(container_name)

        if not container_client.exists():
            # This can not be done lazily because put_object still consumes the stream although the bucket does not exists yet
            logger.debug(f"No bucket existing for project {project_id}.")
            container_client.create_container()

        try:
            blob_client = container_client.upload_blob(
                file_key,
                # Filestream class has read method which is the only requirement for upload blob
                # Therefore the type mismatch can be ignored
                file_stream,  # type: ignore
                content_settings=ContentSettings(
                    content_type=content_type
                    if content_type is not None
                    else "application/octet-stream",
                ),
                overwrite=True,
            )
        except AzureError as err:
            raise ServerBaseError(
                f"The file {file_key} could not be uploaded ({err.message})."
            )

        file_hash: Optional[str] = None
        if hasattr(file_stream, "hash"):
            file_hash = file_stream.hash  # type: ignore[attr-defined]
        else:
            logger.warning(
                "The provided stream object does not provide a hash property. No hash will be available."
            )

        self._create_file_metadata_json_document(
            project_id, blob_client.get_blob_properties(), metadata, file_hash
        )

        # This is necessary in order to have the available versions metadata set
        files_to_prefix = self.list_files(
            project_id, include_versions=False, prefix=file_key
        )
        file_versions = filter(lambda file: file.key == file_key, files_to_prefix)
        return file_versions.__next__()

    def download_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> Tuple[Iterator[bytes], int]:
        """Download a file.

        Either the latest version will be returned or the specified one.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.

        Raises:
            ResourceNotFoundError: If file does not exist.

        Yields:
            Iterator[bytes]: [description]
        """
        logger.debug(
            f"download_file (`project_id`: {project_id}, `file_key`: {file_key}, `version`: {version})"
        )
        container_name = get_container_name(project_id, self.sys_namespace)
        try:
            blob_client = self.client.get_blob_client(container_name, file_key)
            response = blob_client.download_blob(version_id=version)
        except AzureResourceNotFoundError as err:
            raise ResourceNotFoundError(
                f"Could not find file {file_key} (version: {version}) in project {project_id}."
            ) from err
        return response.chunks(), len(response)

    def delete_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        keep_latest_version: bool = False,
    ) -> None:
        """Delete a file.

        If a specific file `version` is provided, only this one will be deleted. If no `version` is provided and `keep_latest_version` is True, all but the latest version will be deleted. Otherwise, all existing versions will be removed.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.
            keep_latest_version (bool, optional): [description]. Defaults to False.
        """

        logger.debug(
            f"delete_file (`project_id`: {project_id}, `file_key`: {file_key}, `version`: {version}, `keep_latest_version`: {keep_latest_version})"
        )

        if keep_latest_version or version is None:
            self._delete_file_versions(project_id, file_key, keep_latest_version)
            return

        container_name = get_container_name(project_id, self.sys_namespace)

        blob_client = self.client.get_blob_client(container_name, file_key)
        try:
            blob_client.delete_blob(version_id=version)
        except AzureResourceNotFoundError as err:
            raise ResourceNotFoundError(
                f"Could not find file {file_key} (version: {version}) in project {project_id}."
            ) from err
        except HttpResponseError as e:
            if e.status_code == 403:
                raise ValueError("Latest file version can not be deleted!")
            else:
                raise e

        try:
            self.json_db_manager.delete_json_document(
                project_id,
                self.DOC_COLLECTION_NAME,
                generate_file_id(file_key, version),
            )
        except ResourceNotFoundError:
            logger.warning(
                f"No file metadata Json doc found for file_key: {file_key}, version: {version}, project: {project_id}"
            )

    def delete_files(
        self,
        project_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> None:
        """Delete all files and storage resources related to a project.

        Args:
            project_id (str): Project ID associated with the files.
            date_from (Optional[datetime], optional): The start date to delete the files. If not specified, all files will be deleted.
            date_to (Optional[datetime], optional): The end date to delete the files. If not specified, all files will be deleted.

        Raises:
            ServerBaseError: Exception
        """
        if date_from and date_to:
            files_to_delete = self.list_files(project_id)

            for file in files_to_delete:
                if file.updated_at and (
                    (date_to.date() >= file.updated_at.date() >= date_from.date())
                ):
                    self.delete_file(project_id, file.key)
        else:
            container_name = get_container_name(
                project_id, self._global_state.settings.SYSTEM_NAMESPACE
            )
            try:
                container_client = self.client.get_container_client(container_name)
                container_client.delete_container()
            except AzureResourceNotFoundError:
                logger.info(
                    f"Project container {container_name} to deleted as it does not exist."
                )
                return
            except AzureError as e:
                raise ServerBaseError(
                    f"Project container {container_name} could not be deleted."
                ) from e

            self.json_db_manager.delete_json_collection(
                project_id, self.DOC_COLLECTION_NAME
            )

    def list_file_actions(
        self, project_id: str, file_key: str, version: Optional[str] = None
    ) -> List[ResourceAction]:
        return []

    def execute_file_action(
        self,
        project_id: str,
        file_key: str,
        action_id: str,
        version: Optional[str] = None,
    ) -> Optional[Response]:
        # TODO
        return None

    def _create_client(self) -> BlobServiceClient:
        settings = self._global_state.settings
        state_namespace = self._global_state[AzureBlobFileManager]
        if not state_namespace.client:
            state_namespace.client = create_azure_blob_client(
                self._global_state.settings
            )
            logger.info(
                f"Azure Blob client created (connection string: {settings.AZURE_BLOB_CONNECTION_STRING})"
            )
        return state_namespace.client

    def _create_file_metadata_json_document(
        self,
        project_id: str,
        azure_blob: BlobProperties,
        metadata: Optional[Dict[str, str]],
        md5_hash: Optional[str] = None,
    ) -> JsonDocument:
        meta_file = self._map_azure_blob_to_file_model(azure_blob)
        if metadata is not None:
            meta_file.metadata = metadata
        if md5_hash:
            meta_file.md5_hash = md5_hash
        metadata_json = self._map_file_obj_to_json_document(meta_file)
        return self.json_db_manager.create_json_document(
            project_id,
            self.DOC_COLLECTION_NAME,
            meta_file.id,  # type: ignore
            metadata_json,
        )

    def _map_azure_blob_to_file_model(self, blob: BlobProperties) -> File:
        # Todo: Check if directory can be given and what the implications are. Do we want to list such? (see object.is_dir param)
        file_extension = os.path.splitext(blob.name)[1]
        display_name = os.path.basename(blob.name)
        data = {
            "id": generate_file_id(blob.name, blob.version_id),
            "external_id": blob.name,
            "key": blob.name,
            "display_name": display_name,
            "updated_at": blob.last_modified,
            "file_extension": file_extension,
            "file_size": blob.size,
            "etag": blob.etag,
            "latest_version": blob.is_current_version or False,
            "version": blob.version_id,
            "content_type": blob.content_settings.content_type,
        }

        return File(**data)

    def _map_file_obj_to_json_document(self, file: File) -> str:
        # Todo: Handle creation metadata. Problem: Each version is actually a new object and gets a dedicated db entry. Use list_objects or direct lookup in the DB?
        json_data = json.dumps(
            file.dict(include=self.METADATA_FIELD_SET, exclude_none=True),
            default=str,
        )
        return json_data

    def _load_file_data_from_azure(
        self,
        container_name: str,
        prefix: Optional[str] = None,
        include_version: Optional[bool] = None,
    ) -> Tuple[List[File], List[str]]:

        file_data: List[File] = []
        db_keys: List[str] = []
        file_versions: Dict[str, List[str]] = {}

        container_client = self.client.get_container_client(container_name)
        if not container_client.exists():
            logger.debug(
                f"No files to list - Container {container_name} does not exist."
            )
            return [], []
        blobs = container_client.list_blobs(
            name_starts_with=prefix,
            include=["versions"],
        )
        for blob in blobs:
            file = self._map_azure_blob_to_file_model(blob)
            if include_version or file.latest_version:
                file_data.append(file)
                # ? The DB Keys might be added always in order to improve syncing between S3 and DB. But this would imply to read all versions from the DB everytime, even when versions arent requested by the user.
                db_keys.append(str(file.id))

            versions = file_versions.get(file.key, [])
            file_versions.update({file.key: versions + [str(file.version)]})

        for file in file_data:
            file.available_versions = file_versions.get(file.key, [])

        return file_data, db_keys

    def _enrich_data_from_db(
        self, project_id: str, file_data: List[File], document_keys: List[str]
    ) -> Tuple[List[File], List[Tuple[str, str]]]:

        json_docs = self.json_db_manager.list_json_documents(
            project_id, self.DOC_COLLECTION_NAME, keys=document_keys
        )

        # Create dict for efficient lookups
        doc_dict: Dict[str, JsonDocument] = {}
        for doc in json_docs:
            doc_dict.update({doc.key: doc})

        docs_not_in_db: List[Tuple[str, str]] = []
        for file in file_data:
            doc_of_file = doc_dict.get(str(file.id))
            if doc_of_file:
                file = self._add_data_from_doc_to_file(file, doc_of_file)
            else:
                json_doc = self._map_file_obj_to_json_document(file)
                docs_not_in_db.append((str(file.id), json_doc))

        return file_data, docs_not_in_db

    def _add_data_from_doc_to_file(self, file: File, doc: JsonDocument) -> File:
        json_dict = json.loads(doc.json_value)
        for metadata_field in self.METADATA_FIELD_SET:
            value = json_dict.get(metadata_field)
            if not value:
                logger.trace(
                    f"The file metadata field {metadata_field} is not in the respective json document."
                )
                continue
            file.__setattr__(metadata_field, value)
        return file

    def _delete_file_versions(
        self, project_id: str, file_key: str, keep_latest_version: bool
    ) -> None:
        container_name = get_container_name(project_id, self.sys_namespace)
        files_to_prefix = self.list_files(
            project_id, include_versions=True, prefix=file_key
        )
        latest_version_db_key = ""
        deleted_values = 0
        blob_client = self.client.get_blob_client(container_name, file_key)
        for file in files_to_prefix:
            if file.key != file_key:
                # This might happen, since list_files takes only a prefix
                continue
            if keep_latest_version and file.latest_version:
                latest_version_db_key = generate_file_id(file_key, str(file.version))
                continue
            # If we keep the latest version we have to delete all old versions manually
            # Otherwise we delete the entire blob after the loop
            if keep_latest_version:
                blob_client.delete_blob(version_id=file.version)
            deleted_values += 1
        if not keep_latest_version and len(files_to_prefix) > 0:
            blob_client.delete_blob()
        elif deleted_values == 0:
            logger.debug(f"No versions for deletion (file_key: {file_key}).")
            return

        # Check related versions against the DB so that everything gets cleaned up
        json_path_filter = f'$ ? (@.key == "{file_key}")'
        db_keys = [
            doc.key
            for doc in self.json_db_manager.list_json_documents(
                project_id, self.DOC_COLLECTION_NAME, json_path_filter
            )
        ]
        if keep_latest_version:
            db_keys.remove(latest_version_db_key)

        for db_key in db_keys:
            self.json_db_manager.delete_json_document(
                project_id, self.DOC_COLLECTION_NAME, db_key
            )
