from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from fastapi import Body, Cookie, Depends, FastAPI, Form, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
    description="A valid Service ID.",
    # TODO: add length restriction
)

JOB_ID_PARAM = Path(
    ...,
    title="Job ID",
    description="A valid job ID.",
    # TODO: add length restriction
)

FILE_KEY_PARAM = Path(
    ...,
    title="File Key",
    example="datasets/customer-table.csv",
    description="A valid file key.",
    regex=data_model.FILE_KEY_REGEX,
    min_length=1,
    max_length=1024,
)

EXTENSION_ID_PARAM = Query(
    None,
    title="Extension ID",
    description="Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.",
    regex=data_model.QUALIFIED_RESOURCE_ID_REGEX,
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

# TEMP: for debugging purpose
@app.get("/welcome", include_in_schema=False)
def welcome() -> Any:
    return {"Hello": "World"}


# Redirect to docs
@app.get("/", include_in_schema=False)
def root() -> Any:
    return RedirectResponse("./docs")


# TEMP: Graphql test

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


@app.get(
    "/search",
    operation_id="search_resources",
    # response_model=data_model.Resource,
    summary="Search resources.",
    # tags=,
    status_code=status.HTTP_200_OK,
)
def search_resources(
    q: str = Query(..., description="Search query."),
    type: Optional[str] = Query(
        None, description="Resource type to use for filtering search results."
    ),
) -> Any:
    raise NotImplementedError


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
    """Returns a successful return code if the instance is healthy."""
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
    """Returns statistics about this instance."""
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
    "/users/me",
    operation_id=data_model.CoreOperations.GET_MY_USER.value,
    response_model=data_model.User,
    summary="Get my user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def get_my_user() -> Any:
    """Returns the user metadata from the authenticated user."""
    # TODO: not a manager operation -> just forward to the get_user operation
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
    """Returns the user metadata for a single user."""
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


# Auth Endpoints


@app.get(
    "/auth/login",
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


@app.get(
    "/auth/logout",
    operation_id=data_model.CoreOperations.LOGOUT_SESSION.value,
    summary="Logout a user session.",
    tags=["auth"],
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
def logout_session() -> Any:
    """Removes all session token cookies and redirects to the login page.

    When making requests to the this endpoint, the browser should be redirected to this endpoint.
    """
    return RedirectResponse("./login", status_code=307)


@app.get(
    "/auth/tokens",
    operation_id=data_model.CoreOperations.LIST_API_TOKENS.value,
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
) -> Any:
    """Returns list of created API tokens for the specified user or project.

    If a user ID and a project ID is provided, a combined list will be returned.
    """
    raise NotImplementedError


@app.post(
    "/auth/tokens",
    operation_id=data_model.CoreOperations.CREATE_TOKEN.value,
    response_model=str,
    summary="Create API or session token.",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def create_token(
    permission: Optional[List[str]] = Query(
        None,
        title="Permissions",
        description="Permissions granted to the token. If none specified, the token will be generated with the same permissions as the one used to call this method.",
    ),
    token_type: data_model.TokenType = Query(
        data_model.TokenType.SESSION_TOKEN,
        description="Type of the token.",
        type="string",
    ),
    description: Optional[str] = Query(
        None, description="Attach a short description to the generated token."
    ),
) -> Any:
    """Returns a session or API token with access on the specified resource.

    A permission is a single string that combines a global ID of a resource with a permission level:

    `{global_id}.{permission_level}`

    Permission levels are a hierarchical system that determines the kind of access that is granted on the resource.
    Permission levels are interpreted and applied inside resource operations. There are three permission levels:

    1. `admin` permission level allows read, write, and administrative access to the resource.
    2. `write` permission level allows read and write (edit) access to the resource.
    3. `read` permission level allows read-only (view) access to the resource.

    The permission level can also be suffixed with an optional restriction defined by the resource:
    `{global_id}.{permission_level}.{custom_restriction}`

    If no permissions are specified, the token will be generated with the same permissions as the authorized token.

    The API token can be deleted (revoked) at any time.
    In comparison, the session token cannot be revoked but expires after a short time (a few minutes).

    This operation can only be called with API tokens (or refresh tokens) due to security aspects.
    Session tokens are not allowed to create other tokens.
    Furthermore, tokens can only be created if the API token used for authorization is granted at least
    the same permission level on the given resource. For example, a token with `write` permission level on a given resource
    allows to create new tokens with `write` or `read` permission on that resource.
    If a restriction is attached to the permission, created tokens on the same permission level require the same restriction.
    """
    raise NotImplementedError


@app.post(
    "/auth/tokens/verify",
    operation_id=data_model.CoreOperations.VERIFY_TOKEN.value,
    # response_model=List[str],
    summary="Verify a Session or API Token.",
    tags=["auth"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def verify_token(
    token: Optional[str] = Body(
        None,
        title="Token",
        description="Token to verify.",
    ),
    permission: Optional[str] = Query(
        None,
        title="Resource Type ",
        description="The token is checked if is granted this permission. If none specified, only the existence or validity of the token itself is checked.",
    ),
) -> Any:
    """Verifies a session or API token for its validity and - if provided - if it has the specified permission.

    Returns an successful HTTP Status code if verification was successful, otherwise an error is returned.
    """
    raise NotImplementedError


class AuthorizeResponseType(str, Enum):
    TOKEN = "token"
    CODE = "code"


class OAuth2AuthorizeRequestForm:
    """OAuth2 Authorize Endpoint Request Form."""

    def __init__(
        self,
        response_type: AuthorizeResponseType = Form(
            ...,
            description="Either code for requesting an authorization code or token for requesting an access token (implicit grant).",
        ),
        client_id: Optional[str] = Form(
            None, description="The public identifier of the client."
        ),
        redirect_uri: Optional[str] = Form(None, description="Redirection URL."),
        scope: Optional[str] = Form(
            None, description="The scope of the access request."
        ),
        state: Optional[str] = Form(
            None,
            description="An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery",
        ),
        nonce: Optional[str] = Form(None),
    ):
        self.response_type = response_type
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state
        self.nonce = nonce


class OAuth2TokenGrantTypes(str, Enum):
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"


class OAuth2TokenRequestForm:
    """OAuth2 Token Endpoint Request Form."""

    def __init__(
        self,
        grant_type: OAuth2TokenGrantTypes = Form(
            ...,
            description="Grant type. Determines the mechanism used to authorize the creation of the tokens.",
        ),
        username: Optional[str] = Form(
            None, description="Required for `password` grant type. The user’s username."
        ),
        password: Optional[str] = Form(
            None, description="Required for `password` grant type. The user’s password."
        ),
        scope: Optional[str] = Form(
            None,
            description="Scopes that the client wants to be included in the access token. List of space-delimited, case-sensitive strings",
        ),
        client_id: Optional[str] = Form(
            None,
            description="The client identifier issued to the client during the registration process",
        ),
        client_secret: Optional[str] = Form(
            None,
            description=" The client secret. The client MAY omit the parameter if the client secret is an empty string.",
        ),
        code: Optional[str] = Form(
            None,
            description="Required for `authorization_code` grant type. The value is what was returned from the authorization endpoint.",
        ),
        redirect_uri: Optional[str] = Form(
            None,
            description="Required for `authorization_code` grant type. Specifies the callback location where the authorization was sent. This value must match the `redirect_uri` used to generate the original authorization_code.",
        ),
        refresh_token: Optional[str] = Form(
            None,
            description="Required for `refresh_token` grant type. The refresh token previously issued to the client.",
        ),
        state: Optional[str] = Form(
            None,
            description="An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery.",
        ),
        set_as_cookie: Optional[bool] = Form(
            False,
            description="If `true`, the access (and refresh) token will be set as cookie instead of the response body.",
        ),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = []
        if scope:
            self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
        self.code = code
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.state = state
        self.set_as_cookie = set_as_cookie


@app.post(
    "/auth/oauth/authorize",
    operation_id=data_model.CoreOperations.AUTHORIZE_CLIENT.value,
    summary="Authorize a client (OAuth2 Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_302_FOUND,
)
def authorize_client(form_data: OAuth2AuthorizeRequestForm = Depends()) -> Any:
    """Authorizes a client.

    The authorization endpoint is used by the client to obtain authorization from the resource owner via user-agent redirection.

    The authorization server redirects the user-agent to the client's redirection endpoint previously established with the
    authorization server during the client registration process or when making the authorization request.

    This endpoint implements the [OAuth2 Authorization Endpoint](https://tools.ietf.org/html/rfc6749#section-3.1).
    """
    pass


@app.post(
    "/auth/oauth/token",
    operation_id=data_model.CoreOperations.REQUEST_TOKEN.value,
    response_model=data_model.OauthToken,
    summary="Request a token (OAuth2 Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def request_token(form_data: OAuth2TokenRequestForm = Depends()) -> Any:
    """Returns an access tokens, ID tokens, or refresh tokens depending on the request parameters.

     The token endpoint is used by the client to obtain an access token by
     presenting its authorization grant or refresh token.

     The token endpoint supports the following grant types:
     - [Password Grant](https://tools.ietf.org/html/rfc6749#section-4.3.2): Used when the application exchanges the user’s username and password for an access token.
         - `grant_type` must be set to `password`
         - `username` (required): The user’s username.
         - `password` (required): The user’s password.
         - `scope` (optional): Optional requested scope values for the access token.
     - [Refresh Token Grant](https://tools.ietf.org/html/rfc6749#section-6): Allows to use refresh tokens to obtain new access tokens.
         - `grant_type` must be set to `refresh_token`
         - `refresh_token` (required): The refresh token previously issued to the client.
         - `scope` (optional): Requested scope values for the new access token. Must not include any scope values not originally granted by the resource owner, and if omitted is treated as equal to the originally granted scope.
     - [Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4.2): Request an access token using only its client
    credentials.
         - `grant_type` must be set to `client_credentials`
         - `scope` (optional): Optional requested scope values for the access token.
         - Client Authentication required (e.g. via client_id and client_secret or auth header)
     - [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1): Used to obtain both access tokens and refresh tokens based on an authorization code from the `/authorize` endpoint.
         - `grant_type` must be set to `authorization_code`
         - `code` (required): The authorization code that the client previously received from the authorization server.
         - `redirect_uri` (required): The redirect_uri parameter included in the original authorization request.
         - Client Authentication required (e.g. via client_id and client_secret or auth header)

    For password, client credentials, and refresh token flows, calling this endpoint is the only step of the flow.
    For the authorization code flow, calling this endpoint is the second step of the flow.

    This endpoint implements the [OAuth2 Token Endpoint](https://tools.ietf.org/html/rfc6749#section-3.2).
    """
    raise NotImplementedError


@app.post(
    "/auth/oauth/revoke",
    operation_id=data_model.CoreOperations.REVOKE_TOKEN.value,
    response_model=List[str],
    summary="Revoke a token (OAuth2 Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def revoke_token(
    token: str = Form(..., description="The token that should be revoked."),
    token_type_hint: Optional[str] = Form(
        None,
        description="A hint about the type of the token submitted for revokation.",
    ),
) -> Any:
    """Revokes a given token.

    This will delete the API token, preventing further requests with the given token.
    Because of caching, the API token might still be usable under certain conditions
    for some operations for a maximum of 15 minutes after deletion.

    This endpoint implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)).
    """
    raise NotImplementedError


@app.post(
    "/auth/oauth/introspect",
    operation_id=data_model.CoreOperations.INTROSPECT_TOKEN.value,
    response_model=data_model.TokenIntrospection,
    summary="Introspect a token (OAuth2 Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def introspect_token(
    token: str = Form(
        ..., description="The token that should be instrospected revoked."
    ),
    token_type_hint: Optional[str] = Form(
        None,
        description="A hint about the type of the token submitted for introspection (e.g. `access_token`, `id_token` and `refresh_token`).",
    ),
) -> Any:
    """Introspects a given token.

    Returns a boolean that indicates whether it is active or not.
    If the token is active, additional data about the token is also returned.
    If the token is invalid, expired, or revoked, it is considered inactive.

    This endpoint implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)).
    """
    raise NotImplementedError


@app.get(
    "/auth/oauth/userinfo",
    operation_id=data_model.CoreOperations.GET_USERINFO.value,
    response_model=data_model.OpenIDUserInfo,
    summary="Get userinfo (OpenID Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def get_userinfo() -> Any:
    """Returns information about the authenticated user.

    The access token obtained must be sent as a bearer token in the `Authorization` header.

    This endpoint implements the [OpenID UserInfo Endpoint](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo).
    """
    return None


@app.get(
    "/auth/oauth/callback",
    operation_id=data_model.CoreOperations.LOGIN_CALLBACK.value,
    summary="Open the login page (OAuth2 Client Endpoint).",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
def login_callback(
    code: str = Query(
        ..., description="The authorization code generated by the authorization server."
    ),
    state: Optional[str] = Query(None),
) -> Any:
    """Callback to finish the login process (OAuth2 Client Endpoint).

    The authorization `code` is exchanged for an access and ID token.
    The ID token contains all relevant user information and is used to login the user.
    If the user does not exist, a new user will be created with the information from the ID token.

    Finally, the user is redirected to the webapp and a session/refresh token is set in the cookies.

    This method implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749.
    """
    rr = RedirectResponse("/webapp", status_code=307)
    rr.set_cookie(key="session_token", value="test-token")
    rr.set_cookie(key="refresh-token", value="test-refresh-token")
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
    test = list_projects
    print("get project")
    return None


@app.get(
    "/projects:suggest-id",
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
    print("Suggest ID")
    return None


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
    "/projects/{project_id}/services:suggest-config",
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
) -> Any:
    """Returns the metadata of a single service.

    The returned metadata might be filtered based on the permission level of the authenticated user.
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/services:deploy-actions",
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
    """Lists all available service deployment options (actions).

    The returned action IDs should be used when calling the [deploy_service](#services/deploy_service) operation.

    The action mechanism allows extensions to provide additional deployment options for a service based on the provided configuration. It works the following way:

    1. The user requests all available deployment options via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
    3. Extensions can run arbitrary code based on the provided service configuration and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [deploy_service](#services/deploy_service) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to deploy the service based on the provided configuration.
    6. The return value of the operation should be a `Service` object.

    The same action mechanism is also used for other type of actions on resources.
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
        None,
        description="The action ID from the service deploy options.",
        regex=data_model.RESOURCE_ID_REGEX,
    ),
) -> Any:
    """Deploy a service for the specified project.

    If no `action_id` is provided, the system will automatically select the best deployment option.

    Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions).
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
    lines: Optional[int] = Query(None, description="Only show the last n lines."),
    since: Optional[datetime] = Query(
        None, description="Only show the logs generated after a given date."
    ),
) -> Any:
    """Returns the stdout/stderr logs of the service."""
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
    """Lists all actions available for the specified service.

    The returned action IDs should be used when calling the [execute_service_action](#services/execute_service_action) operation.

    The action mechanism allows extensions to provide additional functionality on services. It works the following way:

    1. The user requests all available actions via the [list_service_actions](#services/list_service_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_service_actions](#services/list_service_actions) operation.
    3. Extensions can run arbitrary code - e.g., request and check the service metadata for compatibility - and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [execute_service_action](#services/execute_service_action) operation by providing the selected action ID.  The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action.
    6. The return value of the operation can be either a simple message (shown to the user) or a redirect to another URL (e.g., to show a web UI).

    The same action mechanism is also used for other resources (e.g., files, jobs).
    It can support a very broad set of use-cases, for example: Access to service endpoints, dashboards for monitoring, adminsitration tools, and more...
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/actions/{action_id}",
    operation_id=data_model.ExtensibleOperations.EXECUTE_SERVICE_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a service action.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def execute_service_action(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    action_id: str = Path(
        ...,
        description="The action ID from the list_service_actions operation.",
        regex=data_model.RESOURCE_ID_REGEX,
    ),
) -> Any:
    """Executes the selected service action.

    The actions need to be first requested from the [list_service_actions](#services/list_service_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_service_actions](#services/list_service_actions).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/services/{service_id}/access/{endpoint:path}",
    operation_id=data_model.ExtensibleOperations.ACCESS_SERVICE.value,
    # TODO: what is the response model? add additional status codes?
    summary="Access a service endpoint.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def access_service(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    endpoint: str = Path(
        ..., description="The port and base path of the service endpoint."
    ),
) -> Any:
    """Accesses the specified HTTP endpoint of the given service.

    The endpoint should be based on the endpoint information from the service metadata.
    This is usually a combination of port and URL path information.

    The user is expected to be redirected to the specified endpoint.
    If required, cookies can be attached to the response with session tokens to authorize access.
    """
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
    """Lists all jobs associated with the given project."""
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
    project_id: str = PROJECT_ID_PARAM, job_id: str = JOB_ID_PARAM
) -> Any:
    """Returns the metadata of a single job.

    The returned metadata might be filtered based on the permission level of the authenticated user.
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs:suggest-config",
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
    "/projects/{project_id}/jobs:deploy-actions",
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
    """Lists all available job deployment options (actions).

    The returned action IDs should be used when calling the [deploy_job](#job/deploy_job) operation.

    The action mechanism allows extensions to provide additional deployment options for a job based on the provided configuration. It works the following way:

    1. The user requests all available deployment options via the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation.
    3. Extensions can run arbitrary code based on the provided job configuration and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [deploy_job](#jobs/deploy_job) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to deploy the job based on the provided configuration.
    6. The return value of the operation should be a `Job` object.

    The same action mechanism is also used for other type of actions on resources.
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/jobs",
    operation_id=data_model.ExtensibleOperations.DEPLOY_JOB.value,
    response_model=data_model.JobInput,
    summary="Deploy a job.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def deploy_job(
    job: data_model.Job,
    project_id: str = PROJECT_ID_PARAM,
    action_id: Optional[str] = Query(
        None,
        description="The action ID from the job deploy options.",
        regex=data_model.RESOURCE_ID_REGEX,
    ),
) -> Any:
    """Deploy a job for the specified project.

    If no `action_id` is provided, the system will automatically select the best deployment option.

    Available actions can be requested via the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_deploy_job_actions](#jobs/list_deploy_job_actions).
    """
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/jobs/{job_id}",
    operation_id=data_model.ExtensibleOperations.DELETE_JOB.value,
    summary="Delete a job.",
    tags=["jobs"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job(project_id: str = PROJECT_ID_PARAM, job_id: str = JOB_ID_PARAM) -> Any:
    """Deletes a job.

    This will kill and remove the container and all associated deployment artifacts.
    """
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
    job_id: str = JOB_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all actions available for the specified job.

    The returned action IDs should be used when calling the [execute_job_action](#jobs/execute_job_action) operation.

    The action mechanism allows extensions to provide additional functionality on jobs. It works the following way:

    1. The user requests all available actions via the [list_job_actions](#jobs/list_job_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_job_actions](#jobs/list_job_actions) operation.
    3. Extensions can run arbitrary code - e.g., request and check the job metadata for compatibility - and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [execute_job_action](#jobs/execute_job_action) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action.
    6. The return value of the operation can be either a simple message (shown to the user) or a redirect to another URL (e.g., to show a web UI).

    The same action mechanism is also used for other resources (e.g., files, services).
    It can support a very broad set of use-cases, for example: Access to dashboards for monitoring, adminsitration tools, and more...
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/jobs/{job_id}/actions/{action_id}",
    operation_id=data_model.ExtensibleOperations.EXECUTE_JOB_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a job action.",
    tags=["jobs"],
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT},
)
def execute_job_action(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    action_id: str = Path(
        ...,
        description="The action ID from the list_job_actions operation.",
        regex=data_model.RESOURCE_ID_REGEX,
    ),
) -> Any:
    """Executes the selected job action.

    The actions need to be first requested from the [list_job_actions](#jobs/list_job_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_job_actions](#jobs/list_job_actions).
    """
    raise NotImplementedError


# Extension Endpoints


@app.get(
    "/projects/{project_id}/extensions",
    operation_id=data_model.CoreOperations.LIST_EXTENSIONS.value,
    response_model=List[data_model.Extension],
    summary="List extensions.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def list_extensions(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Returns all installed extensions accesible by the specified project.

    This also includes all extensions which are installed globally as well as
    extensions installed by the authorized user.
    """
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/extensions/{extension_id}",
    operation_id=data_model.CoreOperations.DELETE_EXTENSION.value,
    summary="Delete extension.",
    tags=["extensions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_extension(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = Path(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    ),
) -> Any:
    """Deletes an extension.

    This will delete the installation metadata as well as the service container.
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/extensions/{extension_id}",
    operation_id=data_model.CoreOperations.GET_EXTENSION_METADATA.value,
    response_model=data_model.Extension,
    summary="Get extension metadata.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def get_extension_metadata(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: str = Path(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    ),
) -> Any:
    """Returns the metadata of the given extension."""
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/extensions",
    operation_id=data_model.CoreOperations.INSTALL_EXTENSION.value,
    response_model=data_model.Extension,
    summary="Install extension.",
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def install_extension(
    extension: data_model.ExtensionInput, project_id: str = PROJECT_ID_PARAM
) -> Any:
    """Installs an extension for the given project.

    This will deploy the extension container for the selected project and
    registers the extension for all the specified capabilities.
    """
    # TODO: add additonal configuration
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/extensions:suggest-config",
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
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
    raise NotImplementedError


@app.put(
    "/projects/{project_id}/extensions:defaults",
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
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Configures the extension to be used as default for a set of operation IDs.

    This operation can only be executed by project administrators (for setting project defaults) or system administrators.
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/extensions:defaults",
    operation_id=data_model.CoreOperations.GET_EXTENSION_DEFAULTS.value,
    summary="Get extensions defaults.",
    response_model=List[Dict[data_model.TechnicalProject, str]],
    tags=["extensions"],
    status_code=status.HTTP_200_OK,
)
def get_extension_defaults(
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Returns the list of extensible operation IDs with the configured default extension.

    This operation can only be called by project administrators (to get project defaults) or system administrators.
    """
    raise NotImplementedError


# File Endpoints


@app.get(
    "/projects/{project_id}/files",
    operation_id=data_model.ExtensibleOperations.LIST_FILES.value,
    response_model=List[data_model.File],
    summary="List project files.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def list_files(
    project_id: str = PROJECT_ID_PARAM,
    prefix: Optional[str] = Query(
        None,
        description="Filter results to include only files whose names begin with this prefix.",
    ),
    recursive: Optional[bool] = Query(
        True, description="Include all content of subfolders."
    ),
    include_versions: Optional[bool] = Query(
        False,
        description="Include all versions of all files.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
) -> Any:
    """Lists all available files for the project.

    The files can be filtered by using a `prefix`. The prefix is applied on the full path (directory path + filename).

    All versions of the files can be included by setting `versions` to `true` (default is `false`).

    Set `recursive` to `false` to only show files and folders (prefixes) of the current folder.
    The current folder is either the root folder (`/`) or the folder selected by the `prefix` parameter (has to end with `/`).
    """
    raise NotImplementedError


@app.post(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=data_model.ExtensibleOperations.UPLOAD_FILE.value,
    response_model=data_model.File,
    summary="Upload a file.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def upload_file(
    body: str = Body(...),
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
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


@app.get(
    "/projects/{project_id}/files/{file_key:path}:metadata",
    operation_id=data_model.ExtensibleOperations.GET_FILE_METADATA.value,
    response_model=data_model.File,
    summary="Get file metadata.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def get_file_metadata(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
) -> Any:
    """Returns metadata about the specified file."""
    print("file metadata")
    print(file_key)
    return None
    # raise NotImplementedError


@app.patch(
    "/projects/{project_id}/files/{file_key:path}",
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
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
) -> Any:
    """Updates the file metadata.

    This will not change the actual content or the key of the file.

    The update is applied on the existing metadata based on the JSON Merge Patch Standard ([RFC7396](https://tools.ietf.org/html/rfc7396)).
    Thereby, only the specified properties will be updated.
    """
    print("Update file metadata.")
    return None


@app.get(
    "/projects/{project_id}/files/{file_key:path}:download",
    operation_id=data_model.ExtensibleOperations.DOWNLOAD_FILE.value,
    response_model=data_model.File,
    summary="Download a file.",
    tags=["files"],
    status_code=status.HTTP_200_OK,
)
def download_file(
    project_id: str = PROJECT_ID_PARAM,
    file_key: str = FILE_KEY_PARAM,
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
) -> Any:
    """Downloads the selected file.

    If the file storage supports versioning and no `version` is specified, the latest version will be downloaded.
    """
    # TODO adapt download implementation
    print("download")
    print(file_key)
    return None


@app.get(
    "/projects/{project_id}/files/{file_key:path}/actions",
    operation_id=data_model.ExtensibleOperations.LIST_FILE_ACTIONS.value,
    response_model=List[data_model.ResourceAction],
    summary="List file actions.",
    tags=["files"],
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


@app.get(
    "/projects/{project_id}/files/{file_key:path}/actions/{action_id}",
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
        ...,
        description="The action ID from the file actions operation.",
        regex=data_model.RESOURCE_ID_REGEX,
    ),
    version: Optional[str] = Query(
        None,
        description="File version tag. If not specified, the latest version will be used.",
    ),
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


@app.delete(
    "/projects/{project_id}/files/{file_key:path}",
    operation_id=data_model.ExtensibleOperations.DELETE_FILE.value,
    summary="Delete a file.",
    tags=["files"],
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
) -> Any:
    """Deletes the specified file.

    If the file storage supports versioning and no `version` is specified, all versions of the file will be deleted.

    The parameter `keep_latest_version` is useful if you want to delete all older versions of a file.
    """
    print("delete file")
    print(file_key)
    return None


# Secrets Endpoints


@app.get(
    "/projects/{project_id}/secrets",
    operation_id=data_model.CoreOperations.LIST_SECRETS.value,
    response_model=List[data_model.Secret],
    summary="List project secrets.",
    tags=["secrets"],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_secrets(project_id: str = PROJECT_ID_PARAM) -> Any:
    """Lists all the secrets associated with the project."""
    raise NotImplementedError


@app.put(
    "/projects/{project_id}/secrets/{secret_name}",
    operation_id=data_model.CoreOperations.CREATE_SECRET.value,
    summary="Create or updated a sercret.",
    tags=["secrets"],
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
def create_secret(
    secret: data_model.SecretInput,
    secret_name: str = Path(
        ..., description="Name of the secret."
    ),  # TODO add regex pattern
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Creates or updates (overwrites) a secret.

    The secret value will be stored in an encrypted format
    and hidden or removed in certain parts of the application (such as job or service logs).

    However, all project members with atleast `read` permission on the project will be able to access and read the secret value.
    Therefore, we cannot prevent any misuse with the secret caused by mishandling from a project member.
    """
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/secrets/{secret_name}",
    operation_id=data_model.CoreOperations.DELETE_SECRET.value,
    summary="Delete a sercret.",
    tags=["secrets"],
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
def delete_secret(
    secret_name: str = Path(
        ..., description="Name of the secret."
    ),  # TODO add regex pattern
    project_id: str = PROJECT_ID_PARAM,
) -> Any:
    """Deletes a secret."""
    raise NotImplementedError


# Configuration Endpoints


@app.put(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.CREATE_CONFIGURATION.value,
    summary="Create a configuration.",
    tags=["configurations"],
    response_model=data_model.Configuration,
    status_code=status.HTTP_200_OK,
)
def create_configuration(
    configuration: data_model.ConfigurationInput,
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Creates a configuration.

    If a configuration already exists for the given id, the configuration will be overwritten.
    """
    raise NotImplementedError


@app.patch(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.UPDATE_CONFIGURATION.value,
    summary="Update a configuration.",
    tags=["configurations"],
    response_model=data_model.Configuration,
    status_code=status.HTTP_200_OK,
)
def update_configuration(
    configuration: data_model.ConfigurationInput,
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Updates a configuration.

    The update is applied on the existing configuration based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.LIST_CONFIGURATIONS.value,
    response_model=List[data_model.Configuration],
    summary="List configuration.",
    tags=["configurations"],
    status_code=status.HTTP_200_OK,
)
def list_configurations(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Lists all configuration associated with the project.

    If extensions are registered for this operation and no extension is selected via the `extension_id`
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.GET_CONFIGURATION.value,
    response_model=data_model.Configuration,
    summary="Get a configuration.",
    tags=["configurations"],
    status_code=status.HTTP_200_OK,
)
def get_configuration(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Returns a single configuration."""
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/configurations/{configuration_id}/{parameter_key}",
    operation_id=data_model.CoreOperations.GET_CONFIGURATION_PARAMETER.value,
    response_model=str,
    summary="Get a configuration parameter.",
    tags=["configurations"],
    status_code=status.HTTP_200_OK,
)
def get_configuration_parameter(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
    paramter_key: str = Path(..., description="Key of the paramter."),
) -> Any:
    """Returns a the value of a single parameter from a configuration."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/configurations/{configuration_id}",
    operation_id=data_model.CoreOperations.DELETE_CONFIGURATION.value,
    summary="Delete a configuration.",
    tags=["configurations"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_configuration(
    project_id: str = PROJECT_ID_PARAM,
    configuration_id: str = Path(..., description="ID of the configuration."),
) -> Any:
    """Deletes a single configuration."""
    raise NotImplementedError


# Json Document Endpoints


@app.put(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=data_model.CoreOperations.CREATE_JSON_DOCUMENT.value,
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
) -> Any:
    """Creates a JSON document. If a document already exists for the given key, the document will be overwritten.

    If no collection exists in the project with the provided `collection_id`, a new collection will be created.
    """
    raise NotImplementedError


@app.patch(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=data_model.CoreOperations.UPDATE_JSON_DOCUMENT.value,
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
) -> Any:
    """Updates a JSON document.

    The update is applied on the existing document based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/json/{collection_id}",
    operation_id=data_model.CoreOperations.LIST_JSON_DOCUMENTS.value,
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
) -> Any:
    """Lists all JSON documents for the given project collection.

    If extensions are registered for this operation and no extension is selected via the `extension_id` parameter, the results from all extensions will be included in the returned list.

    The `filter` parameter allows to filter the result documents based on a JSONPath expression ([JSON Path Specification](https://goessner.net/articles/JsonPath/)). The filter is only applied to filter documents in the list. It is not usable to extract specific properties.

    # TODO: Add filter examples
    """
    raise NotImplementedError


@app.get(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=data_model.CoreOperations.GET_JSON_DOCUMENT.value,
    response_model=data_model.JsonDocument,
    summary="Get JSON document.",
    tags=["json"],
    status_code=status.HTTP_200_OK,
)
def get_json_document(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
) -> Any:
    """Returns a single JSON document."""
    raise NotImplementedError


@app.delete(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=data_model.CoreOperations.DELETE_JSON_DOCUMENT.value,
    summary="Delete JSON document.",
    tags=["json"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_json_document(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
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

    # TODO: Run with: Run with: PYTHONASYNCIODEBUG=1
    uvicorn.run(
        "contaxy.base_api:app", host="0.0.0.0", port=8082, log_level="info", reload=True
    )
