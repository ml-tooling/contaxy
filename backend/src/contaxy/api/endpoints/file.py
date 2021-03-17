from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.managers.extension import parse_composite_id
from contaxy.schema import ExtensibleOperations, File, FileInput, ResourceAction
from contaxy.schema.exceptions import PermissionDeniedError
from contaxy.schema.extension import EXTENSION_ID_PARAM
from contaxy.schema.file import FILE_KEY_PARAM
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.schema.shared import OPEN_URL_REDIRECT, RESOURCE_ID_REGEX

router = APIRouter(
    tags=["files"],
    responses={
        401: {"detail": "No API token was provided"},
        403: {"detail": "Forbidden - the user is not authorized to use this resource"},
    },
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
    if not component_manager.get_auth_manager().verify_token(
        token, f"projects/{project_id}/files#read"
    ):
        raise PermissionDeniedError()

    return component_manager.get_file_manager(extension_id).list_files(
        project_id, recursive, include_versions, prefix
    )


@router.post(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=ExtensibleOperations.UPLOAD_FILE.value,
    response_model=File,
    summary="Upload a file.",
    status_code=status.HTTP_200_OK,
)
def upload_file(
    body: str = Body(...),
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Uploads a file to a file storage.

    The file will be streamed to the selected file storage (core platform or extension).

    This upload operation only supports to attach a limited set of file metadata.
    Once the upload is finished, you can use the [update_file_metadata operation](#files/update_file_metadata)
    to add or update the metadata of the files.

    The `file_key` allows to categorize the uploaded file under a virtual file structure managed by the core platform.
    This allows to create a directory-like structure for files from different extensions and file-storage types.
    The actual file path on the file storage might not (and doesn't need to) correspond to the provided `file_key`.
    This allows to move files (via [update_file_metadata operation](#files/update_file_metadata)) into differnt paths
    without any changes on the file storage (depending on the implementation).

    Additional file metadata (`additional_metadata`) can be set by using the `x-amz-meta-` prefix for HTTP header keys (e.g. `x-amz-meta-my-metadata`).
    This corresponds to how AWS S3 handles [custom metadata](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html).
    """
    # TODO adapt upload implementation
    print("Upload file")
    return None


@router.get(
    "/projects/{project_id}/files/{file_key:path}:metadata",
    operation_id=ExtensibleOperations.GET_FILE_METADATA.value,
    response_model=File,
    summary="Get file metadata.",
    status_code=status.HTTP_200_OK,
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
    if not component_manager.get_auth_manager().verify_token(
        token, f"/projects/{project_id}/files/{file_key:path}:metadata#read"
    ):
        raise PermissionDeniedError()

    resource_id, extension_id = parse_composite_id(file_key)
    return component_manager.get_file_manager(extension_id).get_file_metadata(
        project_id, resource_id, version
    )


@router.patch(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=ExtensibleOperations.UPDATE_FILE_METADATA.value,
    response_model=File,
    summary="Update file metadata.",
    status_code=status.HTTP_200_OK,
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
    print("Update file metadata.")
    return None


@router.get(
    "/projects/{project_id}/files/{file_key:path}:download",
    operation_id=ExtensibleOperations.DOWNLOAD_FILE.value,
    # TODO: response_model?
    summary="Download a file.",
    status_code=status.HTTP_200_OK,
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
    # TODO adapt download implementation
    print("download")
    print(file_key)
    return None


@router.get(
    "/projects/{project_id}/files/{file_key:path}/actions",
    operation_id=ExtensibleOperations.LIST_FILE_ACTIONS.value,
    response_model=List[ResourceAction],
    summary="List file actions.",
    status_code=status.HTTP_200_OK,
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
    print("get file actions")
    print(file_key)
    return None


@router.get(
    "/projects/{project_id}/files/{file_key:path}/actions/{action_id}",
    operation_id=ExtensibleOperations.EXECUTE_FILE_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a file action.",
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
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
    print("execute file action")
    print(file_key)
    print(action_id)
    return None
    # raise NotImplementedError


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
    print("delete file")
    print(file_key)
    return None
