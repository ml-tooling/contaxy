import os
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, Form, Query, Request, status
from requests_oauthlib import OAuth2Session
from starlette.responses import RedirectResponse, Response

from contaxy import config
from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.managers.auth import AuthManager
from contaxy.schema import (
    ApiToken,
    CoreOperations,
    ExtensibleOperations,
    OAuth2TokenRequestFormNew,
    OAuthToken,
    OAuthTokenIntrospection,
    TokenType,
)
from contaxy.schema.auth import (
    AccessLevel,
    AuthorizedAccess,
    OAuth2ErrorDetails,
    OAuth2TokenGrantTypes,
    contaxy_token_purposes,
)
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
    ClientBaseError,
    ClientValueError,
    ServerBaseError,
)
from contaxy.schema.system import SystemState
from contaxy.utils import auth_utils, id_utils
from contaxy.utils.auth_utils import get_api_token

OAUTH_CALLBACK_ROUTE = "auth/oauth/callback"

router = APIRouter(tags=["auth"], responses={**VALIDATION_ERROR_RESPONSE})


@router.get(
    "/auth/login-page",
    operation_id=ExtensibleOperations.OPEN_LOGIN_PAGE.value,
    summary="Open the login page.",
    status_code=status.HTTP_303_SEE_OTHER,
)
def open_login_page(
    request: Request,
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Returns or redirect to the login-page."""
    if not config.settings.OIDC_AUTH_URL or not config.settings.OIDC_CLIENT_ID:
        raise ServerBaseError(
            "External OIDC Provider is not configured. Please set OIDC_AUTH_URL and further relevant OIDC config params."
        )

    # Needed for test setups
    schema = "http://" if os.getenv("OAUTHLIB_INSECURE_TRANSPORT") else "https://"
    callback_uri = os.path.join(
        schema,
        config.settings.get_redirect_uri(),
        config.settings.CONTAXY_API_PATH,
        OAUTH_CALLBACK_ROUTE,
    )
    session = OAuth2Session(
        config.settings.OIDC_CLIENT_ID,
        scope=["openid", "email"],
        redirect_uri=callback_uri,
    )
    url, state = session.authorization_url(config.settings.OIDC_AUTH_URL)
    # TODO: Check if connector id is required here
    redirect_response = RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="oauth_state", value=state, httponly=True)
    return redirect_response


@router.get(
    "/auth/login",
    operation_id=CoreOperations.LOGIN_USER_SESSION.value,
    summary="Login a user session.",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
def login_user_session(
    username: str = Form(
        ..., description="The user’s username or email used for login."
    ),
    password: str = Form(..., description="The user’s password."),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Signs in the user based on username and password credentials.

    This will set http-only cookies containg tokens with full user access.
    """
    system_info = component_manager.get_system_manager().get_system_info()
    if system_info.system_state != SystemState.RUNNING:
        raise ClientBaseError(
            status.HTTP_400_BAD_REQUEST,
            "Login is not possible before system has been initialized!",
        )

    oauth_token = component_manager.get_auth_manager().request_token(
        OAuth2TokenRequestFormNew(
            grant_type=OAuth2TokenGrantTypes.PASSWORD,
            username=username,
            password=password,
            scope=auth_utils.construct_permission(
                "*", AccessLevel.ADMIN
            ),  # Get full scope
        )
    )

    # TODO: set the right start page of webapp
    response = RedirectResponse(
        url="/app", status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
    # TODO: Set cookie and path or other configurations
    token_info = component_manager.get_auth_manager().introspect_token(
        oauth_token.access_token
    )
    response.set_cookie(
        key=config.API_TOKEN_NAME, value=oauth_token.access_token, httponly=True
    )
    if token_info.sub:
        # Set user ID as cookie as well
        response.set_cookie(
            key=config.AUTHORIZED_USER_COOKIE,
            value=id_utils.extract_user_id_from_resource_name(token_info.sub),
        )

    return response


@router.get(
    "/auth/logout",
    operation_id=CoreOperations.LOGOUT_USER_SESSION.value,
    summary="Logout a user session.",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
def logout_user_session(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Removes all session token cookies and redirects to the login page.

    When making requests to the this endpoint, the browser should be redirected to this endpoint.
    """
    component_manager.verify_access(token)
    return component_manager.get_auth_manager().logout_session()


@router.get(
    "/auth/tokens",
    operation_id=CoreOperations.LIST_API_TOKENS.value,
    response_model=List[ApiToken],
    response_model_exclude_unset=True,
    summary="List API tokens.",
    status_code=status.HTTP_200_OK,
    responses={**AUTH_ERROR_RESPONSES},
)
def list_api_tokens(
    token_subject: Optional[str] = Query(
        None,
        title="Token Subject",
        description="Subject for which the tokens should be listed."
        "If it is not provided, the tokens of the authorized user are returned.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns list of created API tokens associated with the authenticated user."""
    if token_subject is None:
        authorized_access = component_manager.verify_access(token)
        token_subject = authorized_access.authorized_subject

    # Check if the caller has admin access on the user resource
    component_manager.verify_access(
        token,
        token_subject,
        AccessLevel.ADMIN,
    )

    return component_manager.get_auth_manager().list_api_tokens(token_subject)


@router.get(
    "/auth/permissions",
    summary="Lists permissions for given resource.",
    operation_id=CoreOperations.LIST_RESOURCE_PERMISSIONS.value,
    status_code=status.HTTP_200_OK,
    response_model=List[str],
)
def list_resource_permissions(
    resource_name: str,
    resolve_roles: bool = True,
    use_cache: bool = True,
    token: str = Depends(get_api_token),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Lists the permissions for a given resource, admin access for that resource is required."""
    component_manager.verify_access(token, resource_name, AccessLevel.ADMIN)

    return component_manager.get_auth_manager().list_permissions(
        resource_name, resolve_roles, use_cache
    )


@router.post(
    "/auth/permissions",
    summary="Add permission to specified resource.",
    operation_id=CoreOperations.SET_RESOURCE_PERMISSIONS.value,
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_resource_permission(
    resource_name: str,
    permission: str,
    token: str = Depends(get_api_token),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Adds permission to specified resource, admin access to the /auth/permissions resource is required."""
    component_manager.verify_access(token, "/auth/permissions", AccessLevel.ADMIN)

    component_manager.get_auth_manager().add_permission(resource_name, permission)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/auth/permissions",
    summary="Deletes permission of specified resource.",
    operation_id=CoreOperations.DELETE_RESOURCE_PERMISSIONS.value,
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource_permissions(
    resource_name: str,
    permission: str,
    remove_sub_permissions: bool = False,
    token: str = Depends(get_api_token),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Deletes permission of specified resource, admin access to the /auth/permissions resource is required."""
    component_manager.verify_access(token, "/auth/permissions", AccessLevel.ADMIN)

    component_manager.get_auth_manager().remove_permission(
        resource_name, permission, remove_sub_permissions
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/auth/resources",
    summary="List all resources that have a certain permission.",
    operation_id=CoreOperations.GET_RESOURCES_WITH_PERMISSION.value,
    status_code=status.HTTP_200_OK,
    response_model=List[str],
)
def list_resources_with_permission(
    permission: str,
    resource_name_prefix: Optional[str] = None,
    token: str = Depends(get_api_token),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """List all resources that have a certain permission, admin access to the /auth/resources resource is required."""
    component_manager.verify_access(token, "/auth/resources", AccessLevel.ADMIN)

    return component_manager.get_auth_manager().list_resources_with_permission(
        permission, resource_name_prefix
    )


@router.post(
    "/auth/tokens",
    operation_id=CoreOperations.CREATE_TOKEN.value,
    response_model=str,
    summary="Create API or session token.",
    status_code=status.HTTP_200_OK,
    responses={**AUTH_ERROR_RESPONSES},
)
def create_token(
    scopes: Optional[List[str]] = Query(
        None,
        title="Scopes",
        alias="scope",
        description="Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token.",
    ),
    token_type: TokenType = Query(
        TokenType.SESSION_TOKEN,
        description="Type of the token.",
        type="string",
    ),
    description: Optional[str] = Query(
        None, description="Attach a short description to the generated token."
    ),
    token_purpose: Optional[str] = Query(
        "custom-token-purpose",
        description="Purpose of this token.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns a session or API token with the specified scopes.

    If no scopes are specified, the token will be generated with the same scopes as the authorized token.

    The API token can be deleted (revoked) at any time.
    In comparison, the session token cannot be revoked but expires after a short time (a few minutes).

    This operation can only be called with API tokens (or refresh tokens) due to security aspects.
    Session tokens are not allowed to create other tokens.
    Furthermore, tokens can only be created if the API token used for authorization is granted at least
    the same access level on the given resource. For example, a token with `write` access level on a given resource
    allows to create new tokens with `write` or `read` granted level on that resource.
    """
    authorized_access = component_manager.verify_access(token)

    if token_purpose is not None:
        if token_purpose in contaxy_token_purposes:
            raise ClientValueError(
                f"Cannot generate token with purpose {token_purpose} as it is a reserved token purpose."
            )

    if not scopes:
        # Get scopes from token
        scopes = []
        token_introspection = component_manager.get_auth_manager().introspect_token(
            token
        )
        if token_introspection.scope:
            scopes = token_introspection.scope.split()

    # Check that caller has requested scopes/permissions
    for scope in scopes:
        resource_name, access_level = auth_utils.parse_permission(scope)
        component_manager.verify_access(token, resource_name, access_level)

    # Update user last activity time when new token is requested. This updates the time on logon and also on session token refresh.
    user_id = id_utils.extract_user_id_from_resource_name(
        authorized_access.authorized_subject
    )
    component_manager.get_auth_manager().update_user_last_activity_time(user_id=user_id)

    return component_manager.get_auth_manager().create_token(
        token_subject=authorized_access.authorized_subject,
        scopes=scopes,
        token_type=token_type,
        description=description,
        token_purpose=token_purpose,
    )


@router.post(
    "/auth/tokens/verify",
    operation_id=CoreOperations.VERIFY_ACCESS.value,
    response_model=AuthorizedAccess,
    summary="Verify a Session or API Token.",
    status_code=status.HTTP_200_OK,
    responses={**AUTH_ERROR_RESPONSES},
)
def verify_access(
    token_in_body: Optional[str] = Body(
        None,
        title="Token",
        description="Token to verify.",
    ),
    permission: Optional[str] = Query(
        None,
        title="Resource Type ",
        description="The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked.",
    ),
    use_cache: bool = Query(
        True,
        title="Use Cache",
        description="If false, no cache will be used for verifying the token.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Verifies a session or API token for its validity and - if provided - if it has the specified permission.

    Returns an successful HTTP Status code if verification was successful, otherwise an error is returned.
    """
    if token_in_body:
        # Prefer token from request body
        token = token_in_body
    return component_manager.get_auth_manager().verify_access(
        token, permission, use_cache
    )


# OAuth Endpoints
def _add_cookies_to_response(
    auth_manager: AuthManager, response: Response, token: OAuthToken
) -> Response:
    # TODO: Set cookie and path or other configurations
    token_info = auth_manager.introspect_token(token.access_token)
    response.set_cookie(
        key=config.API_TOKEN_NAME, value=token.access_token, httponly=True
    )
    if token_info.sub:
        # Set user ID as cookie as well
        response.set_cookie(
            key=config.AUTHORIZED_USER_COOKIE,
            value=id_utils.extract_user_id_from_resource_name(token_info.sub),
        )

    return response


@router.post(
    "/auth/oauth/token",
    operation_id=CoreOperations.REQUEST_TOKEN.value,
    response_model=OAuthToken,
    summary="Request a token (OAuth2 Endpoint).",
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": OAuth2ErrorDetails},
    },
)
def request_token(
    token_request_form: OAuth2TokenRequestFormNew = Depends(
        OAuth2TokenRequestFormNew.as_form  # type: ignore
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
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
    system_info = component_manager.get_system_manager().get_system_info()
    if system_info.system_state != SystemState.RUNNING:
        raise ClientBaseError(
            status.HTTP_400_BAD_REQUEST,
            "Login is not possible before system has been initialized!",
        )

    oauth_token = component_manager.get_auth_manager().request_token(token_request_form)
    if token_request_form.set_as_cookie:
        response = Response(status_code=status.HTTP_200_OK)
        return _add_cookies_to_response(
            component_manager.get_auth_manager(), response, oauth_token
        )
    return oauth_token


@router.post(
    "/auth/oauth/revoke",
    operation_id=CoreOperations.REVOKE_TOKEN.value,
    summary="Revoke a token (OAuth2 Endpoint).",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": OAuth2ErrorDetails},
    },
)
def revoke_token(
    token: str = Form(..., description="The token that should be revoked."),
    token_type_hint: Optional[str] = Form(
        None,
        description="A hint about the type of the token submitted for revokation.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Revokes a given token.

    This will delete the API token, preventing further requests with the given token.
    Because of caching, the API token might still be usable under certain conditions
    for some operations for a maximum of 15 minutes after deletion.

    This endpoint implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)).
    """
    # TODO: Implement authentication required by spec
    component_manager.get_auth_manager().revoke_token(token)


@router.post(
    "/auth/oauth/introspect",
    operation_id=CoreOperations.INTROSPECT_TOKEN.value,
    response_model=OAuthTokenIntrospection,
    summary="Introspect a token (OAuth2 Endpoint).",
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    responses={**AUTH_ERROR_RESPONSES},
)
def introspect_token(
    token: str = Form(..., description="The token that should be instrospected."),
    token_type_hint: Optional[str] = Form(
        None,
        description="A hint about the type of the token submitted for introspection (e.g. `access_token`, `id_token` and `refresh_token`).",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Introspects a given token.

    Returns a boolean that indicates whether it is active or not.
    If the token is active, additional data about the token is also returned.
    If the token is invalid, expired, or revoked, it is considered inactive.

    This endpoint implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)).
    """
    # TODO: Implement authentication required by spec
    return component_manager.get_auth_manager().introspect_token(token)


@router.get(
    "/auth/oauth/callback",
    operation_id=CoreOperations.LOGIN_CALLBACK.value,
    summary="Open the login page (OAuth2 Client Endpoint).",
    status_code=status.HTTP_200_OK,
)
def login_callback(
    code: str = Query(
        ..., description="The authorization code generated by the authorization server."
    ),
    state: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Callback to finish the login process (OAuth2 Client Endpoint).

    The authorization `code` is exchanged for an access and ID token.
    The ID token contains all relevant user information and is used to login the user.
    If the user does not exist, a new user will be created with the information from the ID token.

    Finally, the user is redirected to the webapp and a session/refresh token is set in the cookies.

    This endpoint implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749.
    """
    system_info = component_manager.get_system_manager().get_system_info()
    if system_info.system_state != SystemState.RUNNING:
        raise ClientBaseError(
            status.HTTP_400_BAD_REQUEST,
            "Login is not possible before system has been initialized!",
        )

    auth_manager = component_manager.get_auth_manager()
    # Needed for test setups
    schema = "http://" if os.getenv("OAUTHLIB_INSECURE_TRANSPORT") else "https://"
    oauth_token = auth_manager.login_callback(
        code,
        os.path.join(
            schema,
            config.settings.get_redirect_uri(),
            config.settings.CONTAXY_API_PATH,
            OAUTH_CALLBACK_ROUTE,
        ),
        component_manager.get_project_manager(),
        state,
    )

    # ! Currently, the webapp needs to be accessible via the same host/port
    response = RedirectResponse(
        os.path.join(
            schema,
            config.settings.get_redirect_uri(),
            f"{config.settings.CONTAXY_WEBAPP_PATH}/",
            # TODO remove when nginx routing is possible without trailing slash
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )

    return _add_cookies_to_response(auth_manager, response, oauth_token)


@router.get(
    "/auth/oauth/enabled",
    operation_id=CoreOperations.OAUTH_ENABLED.value,
    summary="Check if external OAuth2 (OIDC) IDP is enabled.",
    status_code=status.HTTP_200_OK,
    response_model=str,
)
def is_external_idp_enabled() -> Any:
    """Returns the value of `OIDC_AUTH_ENABLED`.

    Returns "0" if it is not set, "1" if it is set.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        content=str(int(config.settings.OIDC_AUTH_ENABLED)),
    )
