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
        pass

    @abstractmethod
    def verify_token(
        self,
        token: str,
        permission: Optional[str] = None,
    ) -> GrantedPermission:
        pass

    @abstractmethod
    def change_password(
        self,
        user_id: str,
        password: str,
    ) -> None:
        pass

    @abstractmethod
    def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool:
        pass

    # Permission Operations

    @abstractmethod
    def add_permission(
        self,
        resource_name: str,
        permission: str,
    ) -> None:
        pass

    @abstractmethod
    def remove_permission(
        self, resource_name: str, permission: str, apply_as_prefix: bool = False
    ) -> None:
        pass

    @abstractmethod
    def list_permissions(
        self, resource_name: str, resolve_groups: bool = True
    ) -> List[str]:
        pass

    @abstractmethod
    def list_resources_with_permissions(
        self, permission: str, resource_name_prefix: Optional[str] = None
    ) -> List[str]:
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
