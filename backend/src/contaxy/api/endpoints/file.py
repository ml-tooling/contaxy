import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, Response, status
from fastapi.responses import StreamingResponse

from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.managers.extension import parse_composite_id
from contaxy.schema import ExtensibleOperations, File, FileInput, ResourceAction
from contaxy.schema.auth import AccessLevel
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    CREATE_RESOURCE_RESPONSES,
    GET_RESOURCE_RESPONSES,
    UPDATE_RESOURCE_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
    ClientValueError,
)
from contaxy.schema.extension import EXTENSION_ID_PARAM
from contaxy.schema.file import FILE_KEY_PARAM
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.schema.shared import (
    MAX_DISPLAY_NAME_LENGTH,
    OPEN_URL_REDIRECT,
    RESOURCE_ID_REGEX,
)
from contaxy.utils.auth_utils import get_api_token
from contaxy.utils.file_utils import FormMultipartStream, SyncFromAsyncGenerator

_FILE_METADATA_PREFIX = "x-amz-meta-"

router = APIRouter(
    tags=["files"],
    responses={**AUTH_ERROR_RESPONSES, **VALIDATION_ERROR_RESPONSE},
)


@router.get(
    "/projects/{project_id}/files",
    operation_id=ExtensibleOperations.LIST_FILES.value,
    response_model=List[File],
    summary="List project files.",
    status_code=status.HTTP_200_OK,
)
def list_files(
    project_id: str = PROJECT_ID_PARAM,
    recursive: bool = Query(True, description="Include all content of subfolders."),
    include_versions: bool = Query(
        False,
        description="Include all versions of all files.",
    ),
    prefix: Optional[str] = Query(
        None,
        description="Filter results to include only files whose names begin with this prefix.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all available files for the project.

    The files can be filtered by using a `prefix`. The prefix is applied on the full path (directory path + filename).

    All versions of the files can be included by setting `versions` to `true` (default is `false`).

    Set `recursive` to `false` to only show files and folders (prefixes) of the current folder.
    The current folder is either the root folder (`/`) or the folder selected by the `prefix` parameter (has to end with `/`).
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/files", AccessLevel.READ
    )

    return component_manager.get_file_manager(extension_id).list_files(
        project_id, recursive, include_versions, prefix
    )


@router.post(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=ExtensibleOperations.UPLOAD_FILE.value,
    response_model=File,
    summary="Upload a file.",
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def upload_file(
    request: Request,
    project_id: str = PROJECT_ID_PARAM,
    file_key: Optional[str] = FILE_KEY_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Uploads a file to a file storage.

    The file will be streamed to the selected file storage (core platform or extension).

    This upload operation allows to attach file metadata by passing headers with the prefix 'x-amz-meta-'
    Once the upload is finished, you can use the [update_file_metadata operation](#files/update_file_metadata)
    to add or update the metadata of the file.

    The `file_key` allows to categorize the uploaded file under a virtual file structure managed by the core platform.
    This allows to create a directory-like structure for files from different extensions and file-storage types.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/files", AccessLevel.WRITE
    )

    file_stream = SyncFromAsyncGenerator(
        request.stream(), component_manager.global_state.shared_namespace.async_loop
    )

    multipart_stream = FormMultipartStream(
        file_stream, request.headers, form_field="file", hash_algo="md5"
    )
    content_type = (
        multipart_stream.content_type
        if multipart_stream.content_type
        else "application/octet-stream"
    )

    if not file_key:
        if not multipart_stream.filename:
            raise ClientValueError(
                "The multipart stream does not contain a file name. Use the endpoint `/projects/{project_id}/files/{file_key:path/}` to explicitly provide a file key."
            )
        file_key = multipart_stream.filename

    file_name = os.path.basename(file_key)
    if len(file_name) > MAX_DISPLAY_NAME_LENGTH:
        raise ClientValueError(
            "Error in uploading file "
            + file_name
            + ". File name is more than "
            + str(MAX_DISPLAY_NAME_LENGTH)
            + " characters."
        )

    metadata = {}
    for key, value in request.headers.items():
        if key.startswith(_FILE_METADATA_PREFIX):
            metadata[key[len(_FILE_METADATA_PREFIX) :]] = value

    return component_manager.get_file_manager().upload_file(
        project_id=project_id,
        file_key=file_key,
        file_stream=multipart_stream,  # type: ignore[arg-type]
        metadata=metadata,
        content_type=content_type,
    )


@router.post(
    "/projects/{project_id}/multipart-upload",
    operation_id=ExtensibleOperations.UPLOAD_FILE_NO_KEY.value,
    response_model=File,
    summary="Upload a file via multipart stream with filename as file key.",
    status_code=status.HTTP_200_OK,
    # TODO: Decide if to include
    include_in_schema=False,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def upload_file_without_key(
    request: Request,
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Uploads a file to a file storage.

    The file will be streamed to the selected file storage (core platform or extension).

    The file key will be derived based on the filename in the multipart stream.

    This upload operation allows to attach file metadata by passing headers with the prefix 'x-amz-meta-'
    Once the upload is finished, you can use the [update_file_metadata operation](#files/update_file_metadata)
    to add or update the metadata of the file.
    """
    return upload_file(request, project_id, None, component_manager, token)


@router.get(
    "/projects/{project_id}/files/{file_key:path}:metadata",
    operation_id=ExtensibleOperations.GET_FILE_METADATA.value,
    response_model=File,
    summary="Get file metadata.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_file_metadata(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns metadata about the specified file."""
    component_manager.verify_access(
        token,
        f"/projects/{project_id}/files/{file_key}:metadata",
        AccessLevel.READ,
    )

    file_key, extension_id = parse_composite_id(file_key)
    return component_manager.get_file_manager(extension_id).get_file_metadata(
        project_id, file_key, version
    )


@router.patch(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=ExtensibleOperations.UPDATE_FILE_METADATA.value,
    response_model=File,
    summary="Update file metadata.",
    status_code=status.HTTP_200_OK,
    responses={**UPDATE_RESOURCE_RESPONSES},
)
def update_file_metadata(
    file: FileInput,
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates the file metadata.

    This will not change the actual content or the key of the file.

    The update is applied on the existing metadata based on the JSON Merge Patch Standard ([RFC7396](https://tools.ietf.org/html/rfc7396)).
    Thereby, only the specified properties will be updated.
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/files/{file_key}",
        AccessLevel.WRITE,
    )

    file_key, extension_id = parse_composite_id(file_key)
    return component_manager.get_file_manager(extension_id).update_file_metadata(
        file, project_id, file_key, version
    )


@router.get(
    "/projects/{project_id}/files/{file_key:path}:download",
    operation_id=ExtensibleOperations.DOWNLOAD_FILE.value,
    # TODO: response_model?
    summary="Download a file.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def download_file(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Downloads the selected file.

    If the file storage supports versioning and no `version` is specified, the latest version will be downloaded.
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/files/{file_key}:download",
        AccessLevel.READ,
    )
    file_manager = component_manager.get_file_manager()
    metadata = file_manager.get_file_metadata(project_id, file_key, version)
    file_stream, file_len = file_manager.download_file(project_id, file_key, version)

    return StreamingResponse(
        file_stream,
        media_type=metadata.content_type,
        headers={
            "Content-Disposition": f"attachment;filename={metadata.display_name}",
            "Content-Length": f"{file_len}",
        },
    )


@router.get(
    "/projects/{project_id}/files/{file_key:path}/actions",
    operation_id=ExtensibleOperations.LIST_FILE_ACTIONS.value,
    response_model=List[ResourceAction],
    summary="List file actions.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def list_file_actions(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all actions available for the specified file.

    The returned action IDs should be used when calling the [execute_file_action](#files/execute_file_action) operation.

    The action mechanism allows extensions to provide additional functionality on files. It works the following way:

    1. The user requests all available actions via the [list_file_actions](#files/list_file_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_file_actions](#files/list_file_actions) operation.
    3. Extensions can run arbitrary code - e.g., request and check the file metadata for compatibility - and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [execute_file_action](#files/execute_file_action) operation by providing the selected action- and extension-ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action.
    6. The return value of the operation can be either a simple message  (shown to the user) or a redirect to another URL (e.g., to show a web UI).

    The same action mechanism is also used for other resources (e.g., services, jobs).
    It can support a very broad set of use-cases, for example: CSV Viewer, Tensorflow Model Deployment, ZIP Archive Explorer ...
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/files/{file_key}/actions",
        AccessLevel.WRITE,
    )

    return component_manager.get_file_manager(extension_id).list_file_actions(
        project_id, file_key, version
    )


@router.get(
    "/projects/{project_id}/files/{file_key:path}/actions/{action_id}",
    operation_id=ExtensibleOperations.EXECUTE_FILE_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a file action.",
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT, **GET_RESOURCE_RESPONSES},
)
def execute_file_action(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    action_id: str = Path(
        ...,
        description="The action ID from the file actions operation.",
        regex=RESOURCE_ID_REGEX,
    ),
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Executes the selected action.

    The actions need to be first requested from the [list_file_actions](#files/list_file_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_file_actions](#files/list_file_actions).
    """
    # TODO: write permission?
    component_manager.verify_access(
        token,
        f"projects/{project_id}/files/{file_key}/actions/{action_id}",
        AccessLevel.WRITE,
    )

    # TODO: only extract extension ID from action?
    action_id, extension_id = parse_composite_id(action_id)

    return component_manager.get_file_manager(extension_id).execute_file_action(
        project_id, file_key, action_id, version
    )


@router.delete(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=ExtensibleOperations.DELETE_FILE.value,
    summary="Delete a file.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_file(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, all versions of the file will be deleted.",
    ),
    keep_latest_version: Optional[bool] = Query(
        False, description="Keep the latest version of the file."
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes the specified file.

    If the file storage supports versioning and no `version` is specified, all versions of the file will be deleted.

    The parameter `keep_latest_version` is useful if you want to delete all older versions of a file.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/files/{file_key}", AccessLevel.WRITE
    )
    if keep_latest_version is None:
        keep_latest_version = False

    file_key, extension_id = parse_composite_id(file_key)
    component_manager.get_file_manager(extension_id).delete_file(
        project_id, file_key, version, keep_latest_version
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/projects/{project_id}/files",
    operation_id=ExtensibleOperations.DELETE_FILES.value,
    summary="Delete all files.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_files(
    project_id: str = PROJECT_ID_PARAM,
    date_from: Optional[datetime] = Query(
        None,
        description="The start date to delete the files. If not specified, all files will be deleted.",
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="The end date to delete the files. If not specified, all files will be deleted.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes all files associated with a project."""
    component_manager.verify_access(
        token, f"projects/{project_id}/files", AccessLevel.ADMIN
    )

    component_manager.get_file_manager(extension_id).delete_files(
        project_id, date_from, date_to
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def modify_openapi_schema(openapi_schema: dict) -> Dict[str, Any]:
    request_body = {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "$ref": "#/components/schemas/Body_upload_file_projects__project_id__files__file_key___post"
                }
            }
        },
    }

    openapi_schema["paths"]["/projects/{project_id}/files/{file_key}"]["post"][
        "requestBody"
    ] = request_body

    component_schema = {
        "title": "Body_upload_file_projects__project_id__files__file_key___post",
        "required": ["file"],
        "type": "object",
        "properties": {
            "file": {"title": "File", "type": "string", "format": "binary"},
            # "file_name": {"title": "File Name", "type": "string"},
        },
    }

    if (
        "components" not in openapi_schema
        or "schemas" not in openapi_schema["components"]
    ):
        openapi_schema["components"] = {"schemas": {}}

    openapi_schema["components"]["schemas"][
        "Body_upload_file_projects__project_id__files__file_key___post"
    ] = component_schema

    return openapi_schema
