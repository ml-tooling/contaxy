from abc import ABC, abstractmethod
from typing import List, Optional

from starlette.responses import RedirectResponse

from contaxy.schema import (
    GrantedPermission,
    OAuth2TokenRequestForm,
    OAuthToken,
    OAuthTokenIntrospection,
    OpenIDUserInfo,
    TokenType,
)


class AuthOperations(ABC):
    @abstractmethod
    def login_page(self) -> RedirectResponse:
        pass

    @abstractmethod
    def logout_session(self) -> RedirectResponse:
        pass

    @abstractmethod
    def create_token(
        self,
        authorized_token: str,
        scopes: Optional[List[str]] = None,
        token_type: TokenType = TokenType.SESSION_TOKEN,
        description: Optional[str] = None,
    ) -> str:
        """Returns a session or API token with access to the speicfied scopes.

        Args:
            authorized_token: The authorized token used to create the new token.
            scopes (optional): Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token.
            token_type (optional): The type of the token. Defaults to `TokenType.SESSION_TOKEN`.
            description (optional): A short description about the generated token.

        Raises:
            PermissionDeniedError: The the `authorized_token` is not granted the permissions for the requested scopes
            UnauthenticatedError: If the `authorized_token` is invalid or expired.

        Returns:
            str: The created session or API token.
        """
        pass

    @abstractmethod
    def verify_token(
        self,
        token: str,
        permission: Optional[str] = None,
    ) -> GrantedPermission:
        """Verifies a session or API token.

        The token is verfied for its validity and - if provided - if it has the specified permission.

        Args:
            token: Token to verify.
            permission (optional): The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked.

        Raises:
            PermissionDeniedError: If the requested permission is denied.
            UnauthenticatedError: If the token is invalid or expired.

        Returns:
            GrantedPermission: Information about the granted permission and authenticated user.
        """
        pass

    @abstractmethod
    def change_password(
        self,
        user_id: str,
        password: str,
    ) -> None:
        """Changes the password of a given user.

        The password is stored as a hash.

        Args:
            user_id: The ID of the user.
            password: The new password to apply for the user.
        """
        pass

    @abstractmethod
    def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool:
        """Verifies a password of a specified user.

        The password is stored as a hash

        Args:
            user_id: The ID of the user.
            password: The password to check. This can also be specified as a hash.

        Returns:
            bool: `True` if the password matches the stored password.
        """
        pass

    # Permission Operations

    @abstractmethod
    def add_permission(
        self,
        resource_name: str,
        permission: str,
    ) -> None:
        """Grants a permission to the specified resource.

        Args:
            resource_name: The resource name that the permission is granted to.
            permission: The permission to grant to the specified resource.
        """
        pass

    @abstractmethod
    def remove_permission(
        self, resource_name: str, permission: str, apply_as_prefix: bool = False
    ) -> None:
        """Revokes a permission from the specified resource.

        Args:
            resource_name: The resource name that the permission should be revoked from.
            permission: The permission to revoke from the specified resource.
            apply_as_prefix: If `True`, the permission is used as prefix, and all permissions that start with this prefix will be revoked. Defaults to `False`.
        """
        pass

    @abstractmethod
    def list_permissions(
        self, resource_name: str, resolve_groups: bool = True
    ) -> List[str]:
        """Returns all permissions associated with the specified resource.

        Args:
            resource_name: The name of the resource (relative URI).
            resolve_groups: If `True`, all permission will be resolved to basic permissions. Defaults to `True`.

        Returns:
            List[str]: List of permissions associated with the given resource.
        """
        pass

    @abstractmethod
    def list_resources_with_permission(
        self, permission: str, resource_name_prefix: Optional[str] = None
    ) -> List[str]:
        """Returns all resources that are granted for the specified permission.

        Args:
            permission: The permission to use. If the permission is specified without the access level, it will filter for all access levels.
            resource_name_prefix: Only return resources that match with this prefix.

        Returns:
            List[str]: List of resources names (relative URIs).
        """
        pass


class OAuthOperations(ABC):

    # TODO: v2
    # @abstractmethod
    # def authorize_client(form_data: OAuth2AuthorizeRequestForm) -> Any:
    #    pass

    @abstractmethod
    def request_token(self, token_request_form: OAuth2TokenRequestForm) -> OAuthToken:
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

        Args:
            token_request_form: The request instructions.

        Returns:
            OAuthToken: The access token and additonal metadata (depending on the grant type).
        """
        pass

    @abstractmethod
    def revoke_token(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
    ) -> None:
        """Revokes a given token.

        This will delete the API token, preventing further requests with the given token.
        Because of caching, the API token might still be usable under certain conditions
        for some operations for a maximum of 15 minutes after deletion.

        This operation implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)).

        Args:
            token: The token that should be revoked.
        """
        pass

    @abstractmethod
    def introspect_token(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
    ) -> OAuthTokenIntrospection:
        """Introspects a given token.

        Returns a status (`active`) that indicates whether it is active or not.
        If the token is active, additional data about the token is also returned.
        If the token is invalid, expired, or revoked, it is considered inactive.

        This operation implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)).

        Args:
            token: The token that should be instrospected.

        Returns:
            OAuthTokenIntrospection: The token state and additional metadata.
        """
        pass

    @abstractmethod
    def get_userinfo(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
    ) -> OpenIDUserInfo:
        """Returns info about the user associated with the token.

        This operation implements the [OpenID UserInfo Endpoint](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo).

        Args:
            token: The token of the authorized user.

        Returns:
            OpenIDUserInfo: Information about the authorized user.
        """
        pass

    @abstractmethod
    def login_callback(
        self,
        code: str,
        state: Optional[str] = None,
    ) -> RedirectResponse:
        """Callback to finish the login process.

        The authorization `code` is exchanged for an access and ID token.
        The ID token contains all relevant user information and is used to login the user.
        If the user does not exist, a new user will be created with the information from the ID token.

        Finally, the user is redirected to the webapp and a session/refresh token is set in the cookies.

        This operation implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749.

        Args:
            code: The authorization code generated by the authorization server.
            state (optional): An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery.

        Raises:
            UnauthenticatedError: If the `code` could not be used to get an ID token.

        Returns:
            RedirectResponse: A redirect to the webapp that has valid access tokens attached.
        """
        pass
