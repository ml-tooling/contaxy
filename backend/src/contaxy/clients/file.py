from typing import Dict, Iterator, List, Optional

import requests
from pydantic import parse_obj_as

from contaxy.clients.shared import handle_errors
from contaxy.operations.file import FileOperations
from contaxy.schema import File, FileInput, FileStream, ResourceAction


class FileClient(FileOperations):
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
        file_stream: FileStream,
        content_type: str = "application/octet-stream",
        request_kwargs: Dict = {},
    ) -> File:
        # ! It is strongly recommended that you open files in binary mode. This is because Requests may attempt to provide the Content-Length header for you, and if it does this value will be set to the number of bytes in the file. Errors may occur if you open the file in text mode.

        # TODO Check if it actually gets streamed or not
        # ! In the event you are posting a very large file as a multipart/form-data request, you may want to stream the request. By default, requests does not support this, but there is a separate package which does - requests-toolbelt. You should read the toolbelt’s documentation for more details about how to use it.

        response = self._client.post(
            f"/projects/{project_id}/files/{file_key}",
            files={"file": (f"{file_key}", file_stream, content_type)},
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
    ) -> Iterator[bytes]:
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
        return response.iter_content(chunk_size=10 * 1024 * 1024)

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
        request_kwargs: Dict = {},
    ) -> None:
        response = self._client.delete(
            f"/projects/{project_id}/files",
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
        pass

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
