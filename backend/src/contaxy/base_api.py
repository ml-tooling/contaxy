from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from fastapi import Body, FastAPI, Path, Query, status
from starlette.responses import HTMLResponse, RedirectResponse, Response

from contaxy import __version__, data_model
from contaxy.utils.api_utils import patch_fastapi

app = FastAPI()

# Initialize API
app = FastAPI(
    title="Contaxy API",
    description="Functionality to create and manage projects, services, jobs, and files.",
    version=__version__,
)

# TODO: add prefix: /api/v1/

# TODO: rename open?
# /actions
# /actions/{action_id}

# TODO: use custom type instead?
PROJECT_ID_PARAM = Path(
    ...,
    title="Project ID",
    example="image-search-engine",
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
    example="datasets/customer-table.csv",
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
    status.HTTP_307_TEMPORARY_REDIRECT: {"message": "Redirecting to another URL"}
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


# TODO define token names

# Graphql test

import graphene
from starlette.graphql import GraphQLApp

graphql_voyager = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        height: 100%;
        margin: 0;
        width: 100%;
        overflow: hidden;
      }
      #voyager {
        height: 100vh;
      }
    </style>

    <!--
      This GraphQL Voyager example depends on Promise and fetch, which are available in
      modern browsers, but can be "polyfilled" for older browsers.
      GraphQL Voyager itself depends on React DOM.
      If you do not want to rely on a CDN, you can host these files locally or
      include them directly in your favored resource bunder.
    -->
    <script src="https://cdn.jsdelivr.net/es6-promise/4.0.5/es6-promise.auto.min.js"></script>
    <script src="https://cdn.jsdelivr.net/fetch/0.9.0/fetch.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react@16/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@16/umd/react-dom.production.min.js"></script>

    <!--
      These two files are served from jsDelivr CDN, however you may wish to
      copy them directly into your environment, or perhaps include them in your
      favored resource bundler.
     -->
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/graphql-voyager/dist/voyager.css"
    />
    <script src="https://cdn.jsdelivr.net/npm/graphql-voyager/dist/voyager.min.js"></script>
  </head>
  <body>
    <div id="voyager">Loading...</div>
    <script>
      // Defines a GraphQL introspection fetcher using the fetch API. You're not required to
      // use fetch, and could instead implement introspectionProvider however you like,
      // as long as it returns a Promise
      // Voyager passes introspectionQuery as an argument for this function
      function introspectionProvider(introspectionQuery) {
        // This example expects a GraphQL server at the path /graphql.
        // Change this to point wherever you host your GraphQL server.
        return fetch('./test-graphql', {
          method: 'post',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: introspectionQuery }),
          credentials: 'include',
        })
          .then(function (response) {
            return response.text();
          })
          .then(function (responseBody) {
            try {
              return JSON.parse(responseBody);
            } catch (error) {
              return responseBody;
            }
          });
      }

      // Render <Voyager /> into the body.
      GraphQLVoyager.init(document.getElementById('voyager'), {
        introspection: introspectionProvider,
      });
    </script>
  </body>
</html>
"""


class GraphQlQuery(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name) -> str:  # type: ignore
        return "Hello " + name


app.add_route("/test-graphql", GraphQLApp(schema=graphene.Schema(query=GraphQlQuery)))


@app.get(
    "/graphql-voyager",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    include_in_schema=False,
)
def open_graphql_voyager() -> Any:
    return HTMLResponse(
        content=graphql_voyager,
        status_code=status.HTTP_200_OK,
    )


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
    status_code=status.HTTP_204_NO_CONTENT,
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
    """Lists all users that are visible to the authenticated user."""
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
    """Returns the user metadata for a single user.

    User `me` as `user_id` to get the metadata of the authenticated user.
    """
    raise NotImplementedError


@app.patch(
    "/users/{user_id}",
    operation_id=data_model.CoreOperations.UPDATE_USER.value,
    response_model=data_model.User,
    summary="Update user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def update_user(user: data_model.UserInput, user_id: str = USER_ID_PARAM) -> Any:
    """Updates the user metadata.

    This will update only the properties that are explicitly set in the patch request.
    The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    raise NotImplementedError


@app.delete(
    "/users/{user_id}",
    operation_id=data_model.CoreOperations.DELETE_USER.value,
    summary="Delete a user.",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: str = USER_ID_PARAM) -> Any:
    """Deletes a user and all resources which are only accesible by this user.

    Shared project resources will not be deleted.
    """
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
        data_model.TokenType.SESSION_TOKEN,
        description="Type of the token.",
        type="string",
    ),
    permission_level: data_model.PermissionLevel = Query(
        data_model.PermissionLevel.WRITE,
        description="Permission level of the token.",
        type="string",
    ),
) -> Any:
    """Returns a session or API token with permission to access all resources accesible by the given user.

    Depending on the provided permission level, this token also allows to create or update resources (`write`)
    or delete projects or the user itself (`admin`).
    """
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
    """Returns list of created API tokens for the specified user or project.

    If a user ID and a project ID is provided, a combined list will be returned.
    """
    raise NotImplementedError


@app.delete(
    "/auth/tokens/{api_token}",
    operation_id=data_model.ExtensibleOperations.DELETE_API_TOKEN.value,
    summary="Delete API token.",
    tags=["auth"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_api_token(
    api_token: str = Path(
        ...,
        title="API Token",
        description="API Token to delete.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Deletes an API token.

    This will revoke the API token, preventing further requests with the given token.
    Because of caching, the API token might still be usable under certain conditions
    for some operations for a maximum of 15 minutes after deletion.
    """
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
    response_model=List[str],
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
    resource_type: Optional[data_model.ResourceType] = Query(
        None,
        title="Resource Type ",
        description="Type of the resource.",
    ),
    resource_id: Optional[str] = Query(
        None,
        title="Resource ID",
        description="ID of the resource.",
    ),
    permission_level: Optional[data_model.PermissionLevel] = Query(
        None,
        title="Permission Level",
        description="Permission level to verify.",
    ),
) -> Any:
    """Verifies a session or API token for its validity and - if provided - if it has the provided permisson.

    If the verification is successful, a list of permssions will be returned associated with the given token.
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
def create_project(project: data_model.ProjectInput) -> Any:
    """Creates a new project.

    We suggest to use the `suggest_project_id` endpoint to get a valid and available ID.
    The project ID might also be set manually, however, an error will be returned if it does not comply with the ID requirements or is already used.
    """
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
    project: data_model.ProjectInput, project_id: str = PROJECT_ID_PARAM
) -> Any:
    """Updates the metadata of the given project.

    This will update only the properties that are explicitly set in the patch request.
    The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    raise NotImplementedError


@app.get(
    "/projects",
    operation_id=data_model.CoreOperations.LIST_PROJECTS.value,
    response_model=List[data_model.Project],
    summary="List all projects.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def list_projects() -> Any:
    """Lists all projects visible to the authenticated user.

    A project is visible to a user, if the user has the atleast a `read` permission for the project.
    System adminstrators will also see technical projects, such as `system-internal` and `system-global`.
    """
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
    """Returns the metadata of a single project."""
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
    """Suggests a valid and unique project ID for the given display name.

    The project ID will be human-readable and resemble the provided display name,
    but might be cut off or have an attached counter prefix.
    """
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}",
    operation_id=data_model.CoreOperations.DELETE_PROJECT.value,
    summary="Delete a project.",
    tags=["projects"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Deletes a project and all its associated resources including deployments and files.

    A project can only be delete by a user with `admin` permission on the project.
    """
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
        data_model.TokenType.SESSION_TOKEN,
        description="Type of the token.",
        type="string",
    ),
    permission_level: data_model.PermissionLevel = Query(
        data_model.PermissionLevel.WRITE,
        description="Permission level of the token.",
        type="string",
    ),
) -> Any:
    """Returns a session or API token with permission (`read`, `write`, or `admin`) to access all project resources.

    The `read` permission level allows read-only access on all resources.
    The `write` permission level allows to create and delete project resources.
    The `admin` permission level allows to delete the project or add/remove other users.
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/users",
    operation_id=data_model.CoreOperations.LIST_PROJECT_MEMBERS.value,
    summary="List project members.",
    tags=["projects"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def list_project_members(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Lists all project members.

    This include all users that have atlease a `read` permission on the given project.
    """
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
    permission_level: Optional[data_model.PermissionLevel] = Query(
        data_model.PermissionLevel.WRITE,
        description="The permission level.",
        type="string",
    ),
) -> Any:
    """Adds a user to the project.

    This will add the permission for this project to the user item.
    The `permission_level` defines what the user can do:

    - The `read` permission level allows read-only access on all resources.
    - The `write` permission level allows to create and delete project resources.
    - The `admin` permission level allows to delete the project or add/remove other users.
    """
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
    """Removes a user from a project.

    This will remove the permission for this project from the user item.
    """
    raise NotImplementedError


# Service Endpoints


@app.get(
    "/projects/{project_id}/services",
    operation_id=data_model.ExtensibleOperations.LIST_SERVICES.value,
    response_model=List[data_model.Service],
    summary="List project services.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def list_services(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all services associated with the given project."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/suggest-config",
    operation_id=data_model.ExtensibleOperations.SUGGEST_SERVICE_CONFIG.value,
    response_model=data_model.ServiceInput,
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
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
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
    """Returns the metadata of a single service.

    The returned metadata might be filtered based on the permission level of the authenticated user.s
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/services/deploy-actions",
    operation_id=data_model.ExtensibleOperations.LIST_DEPLOY_SERVICE_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List deploy service actions.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def list_deploy_service_actions(
    service: data_model.ServiceInput,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all available deployment actions (options) based on the given service configuration.

    The returned action IDs should be used when calling the [deploy service operation](#services/deploy_service).
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
    service: data_model.ServiceInput,
    project_id: str = PROJECT_ID_PARAM,
    action_id: Optional[str] = Query(
        None, description="The action ID from the service deploy options."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Deploy a service for the specified project.

    If `action_id` is not provided, the system will automatically choose how to deploy the service.
    """
    # TODO: add auto select extension option?
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
    delete_volumes: Optional[bool] = Query(
        False, description="Delete all volumes associated with the deployment."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Deletes a service.

    This will kill and remove the container and all associated deployment artifacts.
    """
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
    since: Optional[datetime] = Query(
        None, description="Only show the logs generated after a given date."
    ),
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
def get_service_token(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    token_type: data_model.TokenType = Query(
        data_model.TokenType.SESSION_TOKEN,
        description="Type of the token.",
        type="string",
    ),
) -> Any:
    """Returns a session or API token with permission to access the service endpoints.

    This token is read-only (permission level read) and does not allow any other permission such as deleting or updating the service.

    The API token can be deleted (revoked) at any time. In comparison, the session token cannot be revoked but expires after a short time (a few minutes).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/actions",
    operation_id=data_model.ExtensibleOperations.LIST_SERVICE_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List service actions.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def list_service_actions(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all actions available for the given service.

    This might include actions to access the service endpoints, dashboards for monitoring, adminsitration tools, and more...
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/actions/{action_id}",
    operation_id=data_model.ExtensibleOperations.EXECUTE_SERVICE_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute service action.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def execute_service_action(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    action_id: str = Path(
        ..., description="The action ID from the list_service_actions operation."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Executes the specified service action."""
    raise NotImplementedError


# Job Endpoints


@app.get(
    "/projects/{project_id}/jobs",
    operation_id=data_model.ExtensibleOperations.LIST_JOBS.value,
    response_model=List[data_model.Job],
    summary="List project jobs.",
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
    response_model=data_model.JobInput,
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
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/jobs/deploy-actions",
    operation_id=data_model.ExtensibleOperations.LIST_DEPLOY_JOB_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List deploy job actions.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def list_deploy_job_actions(
    service: data_model.JobInput,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all deployment actions (options) based on the given job configuration.

    The returned action IDs should be used when calling the [deploy job operation](#jobs/deploy_job).
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
    since: Optional[datetime] = Query(
        None, description="Only show the logs generated after a given date."
    ),
) -> Any:
    """Returns the stdout/stderr logs of the job."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs/{job_id}/actions",
    operation_id=data_model.ExtensibleOperations.LIST_JOB_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List job actions.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
)
def list_job_actions(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all actions available for the given job."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs/{job_id}/actions/{action_id}",
    operation_id=data_model.ExtensibleOperations.EXECUTE_JOB_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute job action.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def execute_job_action(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    action_id: str = Path(
        ..., description="The action ID from the list_job_actions operation."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Executes the specified job action."""
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
    """Returns all installed extensions accesible by the given user or project.

    If a user and project ID is provided, all extensions will be returned that are either accesible by the user or project.
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
    """Deletes an extension.

    This will delete the installation metadata as well as the service container.
    """
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
    """Returns the metadata of the given extension."""
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
    extension: data_model.ExtensionInput,
    project_id: Union[data_model.TechnicalProject, str] = Query(
        ...,
        title="Project ID",
        description="Project to which install the extension.",
        min_length=data_model.MIN_PROJECT_ID_LENGTH,
        max_length=data_model.MAX_PROJECT_ID_LENGTH,
    ),
) -> Any:
    """Installs an extension for the given project.

    This will deploy the extension container for the selected project and register the extension for all the specified capabilities.
    """
    # TODO: add additonal configuration
    raise NotImplementedError


@app.get(
    "/extensions/suggest-config",
    operation_id=data_model.CoreOperations.SUGGEST_EXTENSION_CONFIG.value,
    response_model=data_model.ExtensionInput,
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
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
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
    """Configures the extension to be used as default for a set of operation IDs.

    If no `project_id` is provided, the defaults will be set on a system level.

    This operation can only be executed by project administrators (for setting project defaults) or system administrators.
    """
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
    """Returns the list of extensible operation IDs with the configured default extension.

    This operation can only be called by project administrators (to get project defaults) or system administrators.
    """
    raise NotImplementedError


# File Endpoints


@app.get(
    "/projects/{project_id}/data/files",
    operation_id=data_model.ExtensibleOperations.LIST_FILES.value,
    response_model=List[data_model.File],
    summary="List project files.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def list_files(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    filter: Optional[str] = Query(None),  # TODO: better definition
    data_type: Optional[data_model.DataType] = Query(
        None, type="string"
    ),  # TODO: better definition
) -> Any:
    """TODO: add documentation."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/data/files/metadata",
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
    "/projects/{project_id}/data/files/metadata",
    operation_id=data_model.ExtensibleOperations.UPDATE_FILE_METADATA.value,
    response_model=data_model.File,
    summary="Update file metadata.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def update_file_metadata(
    file: data_model.FileInput,
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Updates the file metadata. This will not change the actual content or the key of the file."""
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/data/files/upload",
    operation_id=data_model.ExtensibleOperations.UPLOAD_FILE.value,
    response_model=data_model.File,
    summary="Upload a file.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def upload_file(
    project_id: str = PROJECT_ID_PARAM,
    data_type: Optional[data_model.DataType] = Query(
        data_model.DataType.OTHER,
        description="The categorization of the file.",
        type="string",
    ),
    file_name: Optional[str] = Query(None),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Uploads a file to the file storage."""
    # TODO adapt upload implementation
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/data/files/download",
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
    "/projects/{project_id}/data/files/actions",
    operation_id=data_model.ExtensibleOperations.LIST_FILE_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List file actions.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def list_file_actions(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all available file actions for the given file.

    The returned action IDs should be used when calling the [execute file action operation](#files/execute_file_action).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/data/files/actions/{action_id}",
    operation_id=data_model.ExtensibleOperations.EXECUTE_FILE_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a file action.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def execute_file_action(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    action_id: str = Path(
        ..., description="The action ID from the file actions operation."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Opens the file with the specified action."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/data/files",
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
    "/projects/{project_id}/data/files/token",
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
        data_model.TokenType.SESSION_TOKEN,
        description="Type of the token.",
        type="string",
    ),
) -> Any:
    """Returns a session or API token with permission to access given file.

    This token is read-only and does not allow any action which would modify the given file (`read` permission level).

    The API token can be deleted (revoked) at any time.
    In comparison, the session token cannot be revoked but expires after a short time (a few minutes).
    However, once the file is downloaded there is no way to prevent any further duplication or misuse.
    """
    raise NotImplementedError


# Secrets Endpoints


@app.get(
    "/projects/{project_id}/data/secrets",
    operation_id=data_model.ExtensibleOperations.LIST_SECRETS.value,
    response_model=List[data_model.Secret],
    summary="List project secrets.",
    tags=["secrets"],
    status_code=status.HTTP_200_OK,
)
def list_secrets(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Lists all the secrets associated with the project."""
    raise NotImplementedError


@app.put(
    "/projects/{project_id}/data/secrets/{secret_name}",
    operation_id=data_model.ExtensibleOperations.CREATE_SECRET.value,
    summary="Create or updated a sercret.",
    tags=["secrets"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def create_secret(
    secret: data_model.SecretInput,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Creates or updates (overwrites) a secret.

    The secret value will be stored in an encrypted format
    and hidden or removed in certain parts of the application (such as job or service logs).

    However, all project members with atleast `read` permission on the project will be able to access and read the secret value.
    Therefore, we cannot prevent any misuse with the secret caused by mishandling from a project member.
    """
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/data/secrets/{secret_name}",
    operation_id=data_model.ExtensibleOperations.DELETE_SECRET.value,
    summary="Delete a sercret.",
    tags=["secrets"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_secret(
    secret_name: str = Path(
        ..., description="Name of the secret."
    ),  # TODO add regex pattern
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Deletes a secret."""
    raise NotImplementedError


# Json Document Endpoints


@app.put(
    "/projects/{project_id}/data/json/{collection_id}/{key}",
    operation_id=data_model.ExtensibleOperations.CREATE_JSON_DOCUMENT.value,
    summary="Create JSON document.",
    tags=["json"],
    response_model=data_model.JsonDocument,
    status_code=status.HTTP_200_OK,
)
def create_json_document(
    json_document: Dict,
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Creates a JSON document. If a document already exists for the given key, the document will be overwritten.

    If no collection exists in the project with the provided `collection_id`, a new collection will be created.
    """
    raise NotImplementedError


@app.patch(
    "/projects/{project_id}/data/json/{collection_id}/{key}",
    operation_id=data_model.ExtensibleOperations.UPDATE_JSON_DOCUMENT.value,
    summary="Update a JSON document.",
    tags=["json"],
    response_model=data_model.JsonDocument,
    status_code=status.HTTP_200_OK,
)
def update_json_document(
    json_document: Dict,
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Updates a JSON document.

    The update is applied on the existing document based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/data/json/{collection_id}",
    operation_id=data_model.ExtensibleOperations.LIST_JSON_DOCUMENTS.value,
    response_model=List[data_model.JsonDocument],
    summary="List JSON documents.",
    tags=["json"],
    status_code=status.HTTP_200_OK,
)
def list_json_documents(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    filter: Optional[str] = Query(
        None, description="JSON Path query used to filter the results."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all JSON documents for the given project collection.

    If extensions are registered for this operation and no extension is selected via the `extension_id` parameter, the results from all extensions will be included in the returned list.

    The `filter` parameter allows to filter the result documents based on a JSONPath expression ([JSON Path Specification](https://goessner.net/articles/JsonPath/)). The filter is only applied to filter documents in the list. It is not usable to extract specific properties.

    # TODO: Add filter examples
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/data/json/{collection_id}/{key}",
    operation_id=data_model.ExtensibleOperations.GET_JSON_DOCUMENT.value,
    response_model=data_model.JsonDocument,
    summary="Get JSON document.",
    tags=["json"],
    status_code=status.HTTP_200_OK,
)
def get_json_document(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Returns a single JSON document."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/data/json/{collection_id}/{key}",
    operation_id=data_model.ExtensibleOperations.DELETE_JSON_DOCUMENT.value,
    summary="Delete JSON document.",
    tags=["json"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_json_document(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Deletes a single JSON document.

    If no other document exists in the project collection, the collection will be deleted.
    """
    raise NotImplementedError


#############


# Patch Fastapi to allow relative path resolution.
patch_fastapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "contaxy.base_api:app", host="0.0.0.0", port=8082, log_level="info", reload=True
    )
