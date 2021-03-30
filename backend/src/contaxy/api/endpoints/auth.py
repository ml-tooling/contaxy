from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, Form, Query, status
from starlette.responses import RedirectResponse, Response

from contaxy import config
from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.schema import (
    ApiToken,
    CoreOperations,
    ExtensibleOperations,
    OAuth2TokenRequestFormNew,
    OAuthToken,
    OAuthTokenIntrospection,
    TokenType,
)
from contaxy.schema.auth import AccessLevel, OAuth2ErrorDetails, OAuth2TokenGrantTypes
from contaxy.schema.exceptions import AUTH_ERROR_RESPONSES, VALIDATION_ERROR_RESPONSE
from contaxy.utils import auth_utils, id_utils

router = APIRouter(tags=["auth"], responses={**VALIDATION_ERROR_RESPONSE})


@router.get(
    "/auth/login-page",
    operation_id=ExtensibleOperations.OPEN_LOGIN_PAGE.value,
    summary="Open the login page.",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
def open_login_page(
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Returns or redirect to the login-page."""
    # rr = RedirectResponse("/welcome", status_code=307)
    # rr.set_cookie(key="session_token", value="test-token", path="/welcome")
    # rr.set_cookie(key="user_token", value="test-user-token", path="/users/me")
    # return rr
    return component_manager.get_auth_manager().login_page()


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
) -> Any:
    """Removes all session token cookies and redirects to the login page.

    When making requests to the this endpoint, the browser should be redirected to this endpoint.
    """
    # RedirectResponse("./login", status_code=307)
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
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns list of created API tokens associated with the authenticated user."""
    authorized_access = component_manager.verify_access(token)
    # Check if the caller has admin access on the user resource
    component_manager.verify_access(
        token,
        authorized_access.authorized_subject,
        AccessLevel.ADMIN,
    )

    return component_manager.get_auth_manager().list_api_tokens(
        authorized_access.authorized_subject
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

    # Check if the caller has admin access on the user resource
    component_manager.verify_access(
        token, authorized_access.authorized_subject, AccessLevel.ADMIN
    )

    if not scopes:
        # Get scopes from token
        scopes = []
        token_introspection = component_manager.get_auth_manager().introspect_token(
            token
        )
        if token_introspection.scope:
            scopes = token_introspection.scope.split()

    return component_manager.get_auth_manager().create_token(
        token_subject=authorized_access.authorized_subject,
        scopes=scopes,
        token_type=token_type,
        description=description,
    )


@router.post(
    "/auth/tokens/verify",
    operation_id=CoreOperations.VERIFY_ACCESS.value,
    summary="Verify a Session or API Token.",
    status_code=status.HTTP_204_NO_CONTENT,
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
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Verifies a session or API token for its validity and - if provided - if it has the specified permission.

    Returns an successful HTTP Status code if verification was successful, otherwise an error is returned.
    """
    if token_in_body:
        # Prefer token from request body
        token = token_in_body
    component_manager.get_auth_manager().verify_access(token, permission)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# OAuth Endpoints


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
    oauth_token = component_manager.get_auth_manager().request_token(token_request_form)
    if token_request_form.set_as_cookie:
        response = Response(status_code=status.HTTP_200_OK)
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
    return component_manager.get_auth_manager().request_token(token_request_form)


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
    return component_manager.get_auth_manager().login_callback(code, state)
