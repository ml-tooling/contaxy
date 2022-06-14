from abc import ABC, abstractmethod
from typing import List, Optional, Union

from contaxy.schema import (
    AuthorizedAccess,
    OAuth2TokenRequestFormNew,
    OAuthToken,
    OAuthTokenIntrospection,
    TokenType,
    User,
    UserInput,
    UserRegistration,
)
from contaxy.schema.auth import AccessLevel, ApiToken, UserPermission, UserRead


class AuthOperations(ABC):
    @abstractmethod
    def create_token(
        self,
        scopes: List[str],
        token_type: TokenType,
        description: Optional[str] = None,
        token_purpose: Optional[str] = None,
        token_subject: Optional[str] = None,
    ) -> str:
        """Returns a session or API token with access to the speicfied scopes.

        The token is created on behalfe of the authorized user.

        Args:
            scopes: Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token.
            token_type: The type of the token.
            description (optional): A short description about the generated token.
            token_purpose: Purpose of the newly created token
            token_subject: Subject that the token belongs to

        Returns:
            str: The created session or API token.
        """
        pass

    @abstractmethod
    def list_api_tokens(self, token_subject: Optional[str] = None) -> List[ApiToken]:
        """Lists all API tokens associated with the given token subject.

        Args:
            token_subject:
                Subject for which the tokens should be listed.
                If it is not provided, the tokens of the authorized user are returned.

        Returns:
            List[ApiToken]: A list of API tokens.
        """
        pass

    @abstractmethod
    def verify_access(
        self, token: str, permission: Optional[str] = None, use_cache: bool = True
    ) -> AuthorizedAccess:
        """Verifies if the authorized token is valid and grants a certain permission.

        The token is verfied for its validity and - if provided - if it has the specified permission.

        Args:
            token: Token (session or API) to verify.
            permission (optional): The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked.
            use_cache (optional): If `False`, no cache will be used for verifying the token. Defaults to `True`.

        Raises:
            PermissionDeniedError: If the requested permission is denied.
            UnauthenticatedError: If the token is invalid or expired.

        Returns:
            AuthorizedAccess: Information about the granted permission and authenticated user.
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
    def add_permission(
        self,
        resource_name: str,
        permission: str,
    ) -> None:
        """Grants a permission to the specified resource.

        Args:
            resource_name: The resource name that the permission is granted to.
            permission: The permission to grant to the specified resource.

        Raises:
            ResourceUpdateFailedError: If the resource update could not be applied successfully.
        """
        pass

    @abstractmethod
    def remove_permission(
        self, resource_name: str, permission: str, remove_sub_permissions: bool = False
    ) -> None:
        """Revokes a permission from the specified resource.

        Args:
            resource_name: The resource name that the permission should be revoked from.
            permission: The permission to revoke from the specified resource.
            remove_sub_permissions: If `True`, the permission is used as prefix, and all permissions that start with this prefix will be revoked. Defaults to `False`.
        """
        pass

    @abstractmethod
    def list_permissions(
        self, resource_name: str, resolve_roles: bool = True, use_cache: bool = False
    ) -> List[str]:
        """Returns all permissions granted to the specified resource.

        Args:
            resource_name: The name of the resource (relative URI).
            resolve_roles: If `True`, all roles of the resource will be resolved to the associated permissions. Defaults to `True`.

        Returns:
            List[str]: List of permissions granted to the given resource.
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

    # TODO: v2
    # @abstractmethod
    # def authorize_client(form_data: OAuth2AuthorizeRequestForm) -> Any:
    #    pass

    @abstractmethod
    def request_token(
        self, token_request_form: OAuth2TokenRequestFormNew
    ) -> OAuthToken:
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

        Raises:
            OAuth2Error: If an error occures. Conforms the RFC6749 spec.

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

        Raises:
            OAuth2Error: If an error occures. Conforms the RFC6749 spec.
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

    # User Operations

    @abstractmethod
    def list_users(self) -> List[Union[User, UserRead]]:
        """Lists all users.

        TODO: Filter based on authenticated user?

        Returns:
            List[User]: List of users.
        """
        pass

    @abstractmethod
    def create_user(
        self, user_input: UserRegistration, technical_user: bool = False
    ) -> User:
        """Creates a user.

        Args:
            user_input: The user data to create the new user.
            technical_user: If `True`, the created user will be marked as technical user. Defaults to `False`.

        Raises:
            ResourceAlreadyExistsError: If a user with the same username or email already exists.

        Returns:
            User: The created user information.
        """
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Union[User, UserRead]:
        """Returns the user metadata for a single user.

        Args:
            user_id: The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The user information.
        """
        pass

    @abstractmethod
    def get_user_with_permission(self, user_id: str) -> UserPermission:
        """Returns the user metadata for a single user.

        Args:
            user_id: The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The user information with permssion to resource.
        """
        pass

    @abstractmethod
    def update_user(self, user_id: str, user_input: UserInput) -> User:
        """Updates the user metadata.

        This will update only the properties that are explicitly set in the `user_input`.
        The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).

        Args:
            user_id (str): The ID of the user.
            user_input (UserInput): The user data used to update the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The updated user information.
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        """Deletes a user.

        Args:
            user_id (str): The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.
        """
        pass

    @abstractmethod
    def get_user_token(
        self, user_id: str, access_level: AccessLevel = AccessLevel.WRITE
    ) -> str:
        """Create user token with permission to access all resources accessible by the user.

        If a token for the specified user and access level already exists in the DB, it is returned instead of creating
        a new user token.

        Args:
            user_id: Id of the user for which the token should be created
            access_level: The access level of the user token (defaults to "write")

        Returns:
            User token for specified user id and access level.
        """
        pass
