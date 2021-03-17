from abc import ABC, abstractmethod
from typing import List, Optional

from starlette.responses import RedirectResponse

from contaxy.schema import (
    GrantedPermission,
    OAuth2TokenRequestForm,
    OAuthToken,
    OAuthTokenIntrospection,
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
            PermissionDeniedError:
            UnauthenticatedError: If the token is invalid or expired.

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
    def list_resources_with_permissions(
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
    def request_token(self, form_data: OAuth2TokenRequestForm) -> OAuthToken:
        pass

    @abstractmethod
    def revoke_token(
        self,
        token: str,
        token_type_hint: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def introspect_token(
        self,
        token: str,
        token_type_hint: Optional[str] = None,
    ) -> OAuthTokenIntrospection:
        pass

    @abstractmethod
    def get_userinfo(
        self,
        token: str,
        token_type_hint: Optional[str] = None,
    ) -> OAuthTokenIntrospection:
        pass

    @abstractmethod
    def login_callback(
        self,
        code: str,
        state: Optional[str] = None,
    ) -> RedirectResponse:
        pass
