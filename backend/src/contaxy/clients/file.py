from datetime import datetime
from typing import IO, Callable, Dict, Iterator, List, Optional, Tuple

import requests
from pydantic import parse_obj_as
from requests_toolbelt import MultipartEncoderMonitor

from contaxy.clients.shared import handle_errors
from contaxy.operations.file import FileOperations
from contaxy.schema import File, FileInput, ResourceAction


class FileClient(FileOperations):
    _FILE_METADATA_PREFIX = "x-amz-meta-"

    def __init__(self, client: requests.Session):
        self._client = client

    def list_files(
        self,
        project_id: str,
        recursive: bool = True,
        include_versions: bool = False,
        prefix: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> List[File]:

        query_params: Dict = {
            "recursive": recursive,
            "include_versions": include_versions,
        }
        if prefix:
            query_params.update({"prefix": prefix})

        response = self._client.get(
            f"/projects/{project_id}/files",
            params=query_params,
            **request_kwargs,
        )
        handle_errors(response)
        return parse_obj_as(List[File], response.json())

    def get_file_metadata(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> File:

        query_params: Dict = {}
        if version:
            query_params.update({"version": version})

        response = self._client.get(
            f"/projects/{project_id}/files/{file_key}:metadata",
            params=query_params,
            **request_kwargs,
        )
        handle_errors(response)
        return parse_obj_as(File, response.json())

    def update_file_metadata(
        self,
        file: FileInput,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> File:
        query_params: Dict = {}
        if version:
            query_params.update({"version": version})

        response = self._client.patch(
            f"/projects/{project_id}/files/{file_key}",
            params=query_params,
            data=file.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(response)
        return parse_obj_as(File, response.json())

    def upload_file(
        self,
        project_id: str,
        file_key: str,
        file_stream: IO[bytes],
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        callback: Optional[Callable[[int, int], None]] = None,
        request_kwargs: Dict = {},
    ) -> File:
        """Upload a file.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            file_stream (IO[bytes]): The actual file stream object.
            metadata (Dict, optional): Additional key-value pairs of file meta data
            content_type (str, optional): The mime-type of the file. Defaults to "application/octet-stream".
            callback: Callback function for updating a progress bar. Callback function takes 2 parameters: bytes_read and total_bytes
            request_kwargs: Additional arguments to pass to the request function
        Raises:
            ServerBaseError: If the upload failed.

        Returns:
            File: The file metadata object of the uploaded file.
        """
        # ! It is strongly recommended that you open files in binary mode. This is because Requests may attempt to provide the Content-Length header for you, and if it does this value will be set to the number of bytes in the file. Errors may occur if you open the file in text mode.

        metadata_headers = {}
        if metadata:
            # Add metadata as headers. Use prefix x-amz-meta prefix for header names (S3 conform)
            metadata_headers = {
                self._FILE_METADATA_PREFIX + key: value
                for key, value in metadata.items()
            }
        multipart_data = MultipartEncoderMonitor.from_fields(
            fields={"file": (file_key, file_stream, content_type)},
            callback=lambda m: callback(m.bytes_read, m.len) if callback else None,
        )
        response = self._client.post(
            f"/projects/{project_id}/files/{file_key}",
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type, **metadata_headers},
            **request_kwargs,
        )
        handle_errors(response)
        return parse_obj_as(File, response.json())

    def download_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> Tuple[Iterator[bytes], int]:
        query_params: Dict = {}
        if version:
            query_params.update({"version": version})

        response = self._client.get(
            f"/projects/{project_id}/files/{file_key}:download",
            params=query_params,
            stream=True,
            **request_kwargs,
        )
        handle_errors(response)
        return response.iter_content(chunk_size=10 * 1024 * 1024), int(
            response.headers.get("Content-Length", 0)
        )

    def delete_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        keep_latest_version: bool = False,
        request_kwargs: Dict = {},
    ) -> None:
        query_params: Dict = {"keep_latest_version": keep_latest_version}
        if version:
            query_params.update({"version": version})

        response = self._client.delete(
            f"/projects/{project_id}/files/{file_key}",
            params=query_params,
            **request_kwargs,
        )
        handle_errors(response)

    def delete_files(
        self,
        project_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        request_kwargs: Dict = {},
    ) -> None:
        query_params: Dict = {"date_from": date_from, "date_to": date_to}
        response = self._client.delete(
            f"/projects/{project_id}/files",
            params=query_params,
            **request_kwargs,
        )
        handle_errors(response)

    def list_file_actions(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> List[ResourceAction]:
        # TODO
        return []

    def execute_file_action(
        self,
        project_id: str,
        file_key: str,
        action_id: str,
        version: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> None:
        # TODO
        pass
