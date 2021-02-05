from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from fastapi import Body, FastAPI, Path, Query, status
from starlette.responses import RedirectResponse, Response

from contaxy import __version__, data_model
from contaxy.utils.api_utils import patch_fastapi

app = FastAPI()

# Initialize API
app = FastAPI(
    title="Contaxy API",
    description="Functionality to create and manage projects, services, jobs, and files.",
    version=__version__,
)

# TODO: use custom type instead?
PROJECT_ID_PARAM = Path(
    ...,
    title="Project ID",
    description="A valid project ID.",
    min_length=data_model.MIN_PROJECT_ID_LENGTH,
    max_length=data_model.MAX_PROJECT_ID_LENGTH,
)

USER_ID_PARAM = Path(
    ...,
    title="USER ID",
    description="A valid user ID.",
    # TODO: add length restriction
)

SERVICE_ID_PARAM = Path(
    ...,
    title="Service ID",
    description="A valid service ID.",
    # TODO: add length restriction
)

JOB_ID_PARAM = Path(
    ...,
    title="Job ID",
    description="A valid job ID.",
    # TODO: add length restriction
)

FILE_KEY_PARAM = Query(
    ...,
    title="File Key",
    description="A valid file key.",
    # TODO: add restriction
)

EXTENSION_ID_PARAM = Query(
    None,
    title="Extension ID",
    description="A valid extension ID.",
    # TODO: add length restriction
)

# TODO: evaluate status codes: 302,303,...
OPEN_URL_REDIRECT: Mapping[Union[int, str], Dict[str, Any]] = {
    status.HTTP_307_TEMPORARY_REDIRECT: {"description": "Redirecting to another URL"}
}

# TODO: https://fastapi.tiangolo.com/advanced/additional-responses/#combine-predefined-responses-and-custom-ones
# DEFAULT_RESPONSES = {
#    404: {"description": "Item not found"},
#    307: {"description": "Redirecting to another URL"},
#    403: {"description": "Not enough privileges"},
# }

# TODO: just for debugging purpose
@app.get("/welcome", include_in_schema=False)
def welcome() -> Any:
    return {"Hello": "World"}


# Redirect to docs
@app.get("/", include_in_schema=False)
def root() -> Any:
    return RedirectResponse("./docs")


# System Endpoints


@app.get(
    "/system/info",
    operation_id=data_model.CoreOperations.GET_SYSTEM_INFO.value,
    response_model=data_model.SystemInfo,
    summary="Get system info.",
    tags=["system"],
    status_code=status.HTTP_200_OK,
)
def get_system_info() -> Any:
    """Returns information about this instance."""
    # TODO: this call can also be made without authentication
    raise NotImplementedError


@app.get(
    "/system/healthz",
    status_code=status.HTTP_200_OK,
    summary="Check server health status.",
    tags=["system"],
)
def check_health() -> Any:
    # TODO: this call can also be made without authentication
    raise NotImplementedError


@app.get(
    "/system/statistics",
    operation_id=data_model.CoreOperations.GET_SYSTEM_STATISTICS.value,
    response_model=data_model.SystemStatistics,
    summary="Get system statistics.",
    tags=["system"],
    status_code=status.HTTP_200_OK,
)
def get_system_statistics() -> Any:
    raise NotImplementedError


# User Endpoints


@app.get(
    "/users",
    operation_id=data_model.CoreOperations.LIST_USERS.value,
    response_model=List[data_model.User],
    summary="List all users.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def list_users() -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/users/{user_id}",
    operation_id=data_model.CoreOperations.GET_USER.value,
    response_model=data_model.User,
    summary="Get user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: str = USER_ID_PARAM) -> Any:
    """TODO: add documentation."""
    # TODO: allow me as keyword to access own user info
    raise NotImplementedError


@app.patch(
    "/users/{user_id}",
    operation_id=data_model.CoreOperations.UPDATE_USER.value,
    response_model=data_model.User,
    summary="Update user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def update_user(user: data_model.UserIn, user_id: str = USER_ID_PARAM) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.delete(
    "/users/{user_id}",
    operation_id=data_model.CoreOperations.DELETE_USER.value,
    summary="Delete a user.",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: str = USER_ID_PARAM) -> Any:
    """Deletes a user and all resources which are only accesible by this user. Shared project resources will not be deleted."""
    raise NotImplementedError


@app.get(
    "/users/{user_id}/token",
    operation_id=data_model.CoreOperations.GET_USER_TOKEN.value,
    response_model=str,
    summary="Get a user token.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def get_user_token(
    user_id: str = USER_ID_PARAM,
    token_type: data_model.TokenType = Query(
        data_model.TokenType.SESSION_TOKEN, description="Type of the token."
    ),
) -> Any:
    """Returns a session or API token with permission to access all resources accesible by the given user."""
    raise NotImplementedError


# Auth Endpoints


@app.get(
    "/auth/tokens",
    operation_id=data_model.ExtensibleOperations.LIST_API_TOKENS.value,
    response_model=List[data_model.ApiToken],
    summary="List API tokens.",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def list_api_token(
    user_id: Optional[str] = Query(
        None,
        title="User ID",
        description="Return API tokens associated with this user.",
    ),
    project_id: Optional[str] = Query(
        None,
        title="Project ID",
        description="Return API tokens associated with this project.",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Returns list of created API tokens for the specified user and/or project."""
    raise NotImplementedError


@app.delete(
    "/auth/tokens",
    operation_id=data_model.ExtensibleOperations.DELETE_API_TOKEN.value,
    summary="Delete API token.",
    tags=["auth"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_api_token(
    api_token: str = Query(
        ...,
        title="API Token",
        description="API Token to delete.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    raise NotImplementedError


@app.get(
    "/auth/tokens/refresh",
    operation_id=data_model.CoreOperations.REFRESH_TOKEN.value,
    response_model=str,
    summary="Refresh Session Token.",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    api_token: Optional[str] = Query(
        None,
        title="API Token",
        description="Token to use for refresh.",
    ),
    return_token: bool = Query(
        False,
        title="Return Token",
        description="If true, the session token is returned also in the body.",
    ),
) -> Any:
    """Refreshes the session token.

    This requires an API token sent either as query parameter (not recommended), header, or cookie.
    If successful, the JWT token will be set as session_token cookie and - if requested - returned in the body.
    """
    raise NotImplementedError


@app.post(
    "/auth/tokens/verify",
    operation_id=data_model.CoreOperations.VERIFY_TOKEN.value,
    response_model=str,
    summary="Verify a Token.",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def verify_token(
    token: Optional[str] = Body(
        None,
        title="Token",
        description="Token to verify.",
    ),
    permission: Optional[str] = Query(
        None,
        title="Permission",
        description="Permission to include in the verification.",
    ),
    return_token: bool = Query(
        False,
        title="Return Token",
        description="If true, the session token is returned in the body.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Verifies a session or API token for its validity and - if provided - if it has the provided permisson.

    If the verification is successful and return_token is True, a session token (JWT) will be returned.
    If a permission was provided for verification, only this permission will be included in the session token.
    """
    raise NotImplementedError


@app.get(
    "/auth/login-page",
    operation_id=data_model.ExtensibleOperations.OPEN_LOGIN_PAGE.value,
    summary="Open the login page.",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def open_login_page(
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Returns or redirect to the login-page."""
    rr = RedirectResponse("/welcome", status_code=307)
    rr.set_cookie(key="session_token", value="test-token", path="/welcome")
    rr.set_cookie(key="user_token", value="test-user-token", path="/users/me")
    return rr


# Project Endpoints


@app.post(
    "/projects",
    operation_id=data_model.CoreOperations.CREATE_PROJECT.value,
    response_model=data_model.Project,
    summary="Create a new project.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def create_project(project: data_model.ProjectIn) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.patch(
    "/projects/{project_id}",
    operation_id=data_model.CoreOperations.UPDATE_PROJECT.value,
    response_model=data_model.Project,
    summary="Update project metadata.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def update_project(
    project: data_model.ProjectIn, project_id: str = PROJECT_ID_PARAM
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects",
    operation_id=data_model.CoreOperations.LIST_PROJECTS.value,
    response_model=List[data_model.Project],
    summary="List all available projects.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def list_projects() -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}",
    operation_id=data_model.CoreOperations.GET_PROJECT.value,
    response_model=data_model.Project,
    summary="Get details for a project.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def get_project(project_id: str = PROJECT_ID_PARAM) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/suggest-id",
    operation_id=data_model.CoreOperations.SUGGEST_PROJECT_ID.value,
    response_model=str,
    summary="Suggest project ID.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def suggest_project_id(
    display_name: str = Query(
        ...,
        min_length=data_model.MIN_DISPLAY_NAME_LENGTH,
        max_length=data_model.MAX_DISPLAY_NAME_LENGTH,
    )
) -> Any:
    """Suggests a valid and unique project ID for the given display name."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}",
    operation_id=data_model.CoreOperations.DELETE_PROJECT.value,
    summary="Delete a project.",
    tags=["projects"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Deletes a project and all its associated resources including deployments and files."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/token",
    operation_id=data_model.CoreOperations.GET_PROJECT_TOKEN.value,
    response_model=str,
    summary="Get a project token.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def get_project_token(
    project_id: str = PROJECT_ID_PARAM,
    token_type: data_model.TokenType = Query(
        data_model.TokenType.SESSION_TOKEN, description="Type of the token."
    ),
) -> Any:
    """Returns a session or API token with permission to access all project resources."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/users",
    operation_id=data_model.CoreOperations.LIST_PROJECT_MEMBERS.value,
    summary="List project members.",
    tags=["projects"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def list_project_members(project_id: str = PROJECT_ID_PARAM) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.put(
    "/projects/{project_id}/users/{user_id}",
    operation_id=data_model.CoreOperations.ADD_PROJECT_MEMBER.value,
    summary="Add user to project.",
    tags=["projects"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_project_member(
    project_id: str = PROJECT_ID_PARAM,
    user_id: str = USER_ID_PARAM,
    role: Optional[data_model.ProjectRole] = Query(
        data_model.ProjectRole.MEMBER, description="The permission level."
    ),
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/users/{user_id}",
    operation_id=data_model.CoreOperations.REMOVE_PROJECT_MEMBER.value,
    summary="Remove user from project.",
    tags=["projects"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: str = PROJECT_ID_PARAM, user_id: str = USER_ID_PARAM
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


# Service Endpoints


@app.get(
    "/projects/{project_id}/services",
    operation_id=data_model.ExtensibleOperations.LIST_SERVICES.value,
    response_model=List[data_model.Service],
    summary="List all project services.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def list_services(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/suggest-config",
    operation_id=data_model.ExtensibleOperations.SUGGEST_SERVICE_CONFIG.value,
    response_model=data_model.ServiceIn,
    summary="Suggest service configuration.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def suggest_service_config(
    project_id: str = PROJECT_ID_PARAM,
    container_image: str = Query(
        ..., description="Container image to use for suggestion."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}",
    operation_id=data_model.ExtensibleOperations.GET_SERVICE_METADATA.value,
    response_model=data_model.Service,
    summary="Get service metadata.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def get_service_metadata(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/services/deploy-options",
    operation_id=data_model.ExtensibleOperations.LIST_SERVICE_DEPLOY_OPTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List service deploy options.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def list_service_deploy_options(
    service: data_model.ServiceIn,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all deployment options based on the given service configuration.

    The returned action IDs should be used when calling the deploy service operation.
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/services",
    operation_id=data_model.ExtensibleOperations.DEPLOY_SERVICE.value,
    response_model=data_model.Service,
    summary="Deploy a service.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def deploy_service(
    service: data_model.ServiceIn,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    action_id: Optional[str] = Query(
        None, description="The action ID from the service deploy options."
    ),
) -> Any:
    """Deploy a service for the specified project."""
    # TODO: add auto select provider option
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/services/{service_id}",
    operation_id=data_model.ExtensibleOperations.DELETE_SERVICE.value,
    summary="Delete a service.",
    tags=["services"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/logs",
    operation_id=data_model.ExtensibleOperations.GET_SERVICE_LOGS.value,
    response_model=str,
    summary="Get service logs.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def get_service_logs(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    lines: Optional[int] = Query(None, description="Only show the last n lines."),
) -> Any:
    """Returns the stdout/stderr logs of the service."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/token",
    operation_id=data_model.ExtensibleOperations.GET_SERVICE_ACCESS_TOKEN.value,
    response_model=str,
    summary="Get service access token.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def get_service_access_token(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    token_type: data_model.TokenType = Query(
        data_model.TokenType.SESSION_TOKEN, description="Type of the token."
    ),
) -> Any:
    """Returns a session or API token with permission to access the service endpoints.

    This token is read-only and does not allow any other permission such as deleting or updating the service.
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/open/options",
    operation_id=data_model.ExtensibleOperations.LIST_OPEN_SERVICE_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List open service actions.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def list_open_service_actions(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all actions available for the given service.

    This might include actions to access the service endpoints, dashboards for monitoring, adminsitration tools, and more...
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/open",
    operation_id=data_model.ExtensibleOperations.OPEN_SERVICE.value,
    # TODO: what is the response model? add additional status codes?
    summary="Open the service.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def open_service(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    action_id: str = Query(
        ..., description="The action ID from the open service options operation."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Opens the service with the specified action."""
    raise NotImplementedError


# Job Endpoints


@app.get(
    "/projects/{project_id}/jobs",
    operation_id=data_model.ExtensibleOperations.LIST_JOBS.value,
    response_model=List[data_model.Job],
    summary="List all project jobs.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def list_jobs(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs/{job_id}",
    operation_id=data_model.ExtensibleOperations.GET_JOB_METADATA.value,
    response_model=data_model.Job,
    summary="Get job metadata.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def get_job_metadata(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs/suggest-config",
    operation_id=data_model.ExtensibleOperations.SUGGEST_JOB_CONFIG.value,
    response_model=data_model.JobIn,
    summary="Suggest job configuration.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def suggest_job_config(
    project_id: str = PROJECT_ID_PARAM,
    container_image: str = Query(
        ..., description="Container image to use for suggestion."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/jobs/deploy-options",
    operation_id=data_model.ExtensibleOperations.LIST_JOB_DEPLOY_OPTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List job deploy options.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def list_job_deploy_options(
    service: data_model.JobIn,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all deployment options based on the given job configuration.

    The returned action IDs should be used when calling the deploy job operation.
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/jobs",
    operation_id=data_model.ExtensibleOperations.DEPLOY_JOB.value,
    response_model=data_model.Job,
    summary="Deploy a job.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def deploy_job(
    job: data_model.Job,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    action_id: Optional[str] = Query(
        None, description="The action ID from the job deploy options."
    ),
) -> Any:
    """Deploy a job for the specified project."""
    # TODO: add auto select provider option
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/jobs/{job_id}",
    operation_id=data_model.ExtensibleOperations.DELETE_JOB.value,
    summary="Delete a job.",
    tags=["jobs"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs/{job_id}/logs",
    operation_id=data_model.ExtensibleOperations.GET_JOB_LOGS.value,
    response_model=str,
    summary="Get job logs.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def get_job_logs(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    lines: Optional[int] = Query(None, description="Only show the last n lines."),
) -> Any:
    """Returns the stdout/stderr logs of the job."""
    raise NotImplementedError


# File Endpoints


@app.get(
    "/projects/{project_id}/files",
    operation_id=data_model.ExtensibleOperations.LIST_FILES.value,
    response_model=List[data_model.File],
    summary="List all project files.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def list_files(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    filter: Optional[str] = Query(None),  # TODO: better definition
    data_type: Optional[data_model.DataType] = Query(None),  # TODO: better definition
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/files/metadata",
    operation_id=data_model.ExtensibleOperations.GET_FILE_METADATA.value,
    response_model=data_model.File,
    summary="Get file metadata.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def get_file_metadata(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.patch(
    "/projects/{project_id}/files/metadata",
    operation_id=data_model.ExtensibleOperations.UPDATE_FILE_METADATA.value,
    response_model=data_model.File,
    summary="Update file metadata.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def update_file_metadata(
    file: data_model.FileIn,
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Updates the file metadata. This will not change the actual content or the key of the file."""
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/files/upload",
    operation_id=data_model.ExtensibleOperations.UPLOAD_FILE.value,
    response_model=data_model.File,
    summary="Upload a file.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def upload_file(
    project_id: str = PROJECT_ID_PARAM,
    data_type: Optional[data_model.DataType] = Query(
        data_model.DataType.OTHER, description="The categorization of the file."
    ),
    file_name: Optional[str] = Query(None),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    # TODO adapt upload implementation
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/files/download",
    operation_id=data_model.ExtensibleOperations.DOWNLOAD_FILE.value,
    response_model=data_model.File,
    summary="Download a file.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def download_file(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    # TODO adapt download implementation
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/files/open/options",
    operation_id=data_model.ExtensibleOperations.LIST_OPEN_FILE_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List open file actions.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def list_open_file_actions(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all open file options for the given file.

    The returned action IDs should be used when calling the open file operation.
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/files/open",
    operation_id=data_model.ExtensibleOperations.OPEN_FILE.value,
    # TODO: what is the response model? add additional status codes?
    summary="Open the file.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def open_file(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    action_id: str = Query(
        ..., description="The action ID from the open file options operation."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Opens the file with the specified action."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/files",
    operation_id=data_model.ExtensibleOperations.DELETE_FILE.value,
    summary="Delete a file.",
    tags=["files"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_file(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/files/token",
    operation_id=data_model.ExtensibleOperations.GET_FILE_ACCESS_TOKEN.value,
    response_model=str,
    summary="Get file access token.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def get_file_access_token(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    token_type: data_model.TokenType = Query(
        data_model.TokenType.SESSION_TOKEN, description="Type of the token."
    ),
) -> Any:
    """Returns a session or API token with permission to access given file.

    This token is read-only and does not allow any action which would modify the given file.
    """
    raise NotImplementedError


# Extension Endpoints


@app.get(
    "/extensions",
    operation_id=data_model.CoreOperations.LIST_EXTENSIONS.value,
    response_model=List[data_model.Extension],
    summary="List extensions.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def list_extensions(
    user_id: Optional[str] = Query(
        None,
        title="User ID",
        description="Return extensions associated with this user.",
    ),
    project_id: Optional[str] = Query(
        None,
        title="Project ID",
        description="Return extensions associated with this project.",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
) -> Any:
    """Returns all registered extensions accesible by the given user and/or project.

    If this method is called without authentication, only extensions that do not require authentication are returned.
    """
    raise NotImplementedError


@app.delete(
    "/extensions/{extension_id}",
    operation_id=data_model.CoreOperations.DELETE_EXTENSION.value,
    summary="Delete extension.",
    tags=["extensions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_extension(
    extension_id: Optional[str] = Path(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    )
) -> Any:
    """TODO: add documentation"""
    raise NotImplementedError


@app.get(
    "/extensions/{extension_id}",
    operation_id=data_model.CoreOperations.GET_EXTENSION_METADATA.value,
    response_model=data_model.Extension,
    summary="Get extension metadata.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def get_extension_metadata(
    extension_id: str = Path(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    )
) -> Any:
    """TODO: add documentation"""
    # TODO: only return selected properties (e.g. no parameters)
    raise NotImplementedError


@app.post(
    "/extensions",
    operation_id=data_model.CoreOperations.INSTALL_EXTENSION.value,
    response_model=data_model.Extension,
    summary="Install extension.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def install_extension(
    extension: data_model.ExtensionIn,
    project_id: Union[data_model.TechnicalProject, str] = Query(
        ...,
        title="Project ID",
        description="Project to which install the extension.",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
) -> Any:
    """TODO: detailed description"""
    # TODO: add additonal configuration
    raise NotImplementedError


@app.get(
    "/extensions/suggest-config",
    operation_id=data_model.CoreOperations.SUGGEST_EXTENSION_CONFIG.value,
    response_model=data_model.ExtensionIn,
    summary="Suggest extension configuration.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def suggest_extension_config(
    container_image: str = Query(
        ..., description="Container image to use for suggestion."
    ),
    project_id: Optional[Union[data_model.TechnicalProject, str]] = Query(
        None,
        title="Project ID",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.put(
    "/extensions/defaults",
    operation_id=data_model.CoreOperations.SET_EXTENSION_DEFAULTS.value,
    summary="Set extension defaults.",
    tags=["extensions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def set_extension_defaults(
    extension_id: str = Query(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    ),
    operation_id: List[data_model.ExtensibleOperations] = Query(
        ...,
        title="Operation IDs",
        description="Set extension as default for those operation IDs.",
    ),
    project_id: Union[data_model.TechnicalProject, str] = Query(
        None,
        title="Project ID",
        description="Set defaults for the given project.",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
) -> Any:
    """Configured a set of operation IDs to use the given extension as default."""
    # TODO: only project admins or system admins should be able to call this
    raise NotImplementedError


@app.get(
    "/extensions/defaults",
    operation_id=data_model.CoreOperations.GET_EXTENSION_DEFAULTS.value,
    summary="Get extensions defaults.",
    response_model=List[Dict[data_model.TechnicalProject, str]],
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def get_extension_defaults(
    project_id: Union[data_model.TechnicalProject, str] = Query(
        None,
        title="Project ID",
        description="Filter defaults by project.",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
) -> Any:
    """Returns the list of extensible operation IDs and the configured default extension."""
    # TODO: only project admins or system admins should be able to call this
    raise NotImplementedError


#############


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "contaxy.base_api:app", host="0.0.0.0", port=8081, log_level="info", reload=True
    )
