import json
from typing import Dict, List, Optional, Union

import requests
from pydantic import parse_raw_as
from requests.models import Response

from contaxy.clients.shared import handle_errors
from contaxy.operations.auth import AuthOperations
from contaxy.schema import (
    AccessLevel,
    AuthorizedAccess,
    OAuth2TokenRequestFormNew,
    OAuthToken,
    OAuthTokenIntrospection,
    TokenType,
    User,
    UserInput,
    UserRegistration,
)
from contaxy.schema.auth import ApiToken, OAuth2Error, UserPermission, UserRead


def handle_oauth_error(response: Response) -> None:
    if response.status_code != 400:
        return

    response_data = response.json()
    if "error" in response_data:
        raise OAuth2Error(response_data["error"])


class AuthClient(AuthOperations):
    def __init__(self, client: requests.Session):
        self._client = client

    def create_token(
        self,
        scopes: List[str],
        token_type: TokenType,
        description: Optional[str] = None,
        token_purpose: Optional[str] = None,
        token_subject: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> str:
        # TODO: Implement token_purpose and token_subject
        params = {
            "token_type": token_type.value,
            "scope": scopes,
            "token_purpose": token_purpose,
        }
        if description:
            params["description"] = description
        response = self._client.post("/auth/tokens", params=params, **request_kwargs)
        handle_errors(response)
        return response.json()

    def list_api_tokens(
        self, token_subject: Optional[str] = None, request_kwargs: Dict = {}
    ) -> List[ApiToken]:
        params = {}
        if token_subject is not None:
            params["token_subject"] = token_subject
        response = self._client.get("/auth/tokens", params=params, **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[ApiToken], response.text)

    def verify_access(
        self,
        token: str,
        permission: Optional[str] = None,
        use_cache: bool = True,
        request_kwargs: Dict = {},
    ) -> AuthorizedAccess:
        params: Dict = {"use_cache": use_cache}
        if permission is not None:
            params["permission"] = permission
        response = self._client.post(
            "/auth/tokens/verify",
            params=params,
            data=json.dumps(token),
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(AuthorizedAccess, response.text)

    def change_password(
        self, user_id: str, password: str, request_kwargs: Dict = {}
    ) -> None:
        response = self._client.put(
            f"/users/{user_id}:change-password", data=password, **request_kwargs
        )
        handle_errors(response)

    def add_permission(
        self, resource_name: str, permission: str, request_kwargs: Dict = {}
    ) -> None:
        params = {
            "resource_name": resource_name,
            "permission": permission,
        }
        response = self._client.post(
            "/auth/permissions", params=params, **request_kwargs
        )
        handle_errors(response)

    def remove_permission(
        self,
        resource_name: str,
        permission: str,
        remove_sub_permissions: bool = False,
        request_kwargs: Dict = {},
    ) -> None:
        params: Dict = {
            "resource_name": resource_name,
            "permission": permission,
            "remove_sub_permissions": remove_sub_permissions,
        }
        response = self._client.delete(
            "/auth/permissions", params=params, **request_kwargs
        )
        handle_errors(response)

    def list_permissions(
        self,
        resource_name: str,
        resolve_roles: bool = True,
        use_cache: bool = False,
        request_kwargs: Dict = {},
    ) -> List[str]:
        params: Dict = {
            "resource_name": resource_name,
            "resolve_roles": resolve_roles,
            "use_cache": use_cache,
        }
        response = self._client.get(
            "/auth/permissions", params=params, **request_kwargs
        )
        handle_errors(response)
        return parse_raw_as(List[str], response.text)

    def list_resources_with_permission(
        self,
        permission: str,
        resource_name_prefix: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> List[str]:
        params = {
            "permission": permission,
            "resource_name_prefix": resource_name_prefix,
        }
        response = self._client.get("/auth/resources", params=params, **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[str], response.text)

    # OAuth Operations

    def request_token(
        self, token_request_form: OAuth2TokenRequestFormNew, request_kwargs: Dict = {}
    ) -> OAuthToken:
        response = self._client.post(
            "/auth/oauth/token",
            data=token_request_form.dict(exclude_unset=True),
            **request_kwargs,
        )
        handle_oauth_error(response)
        handle_errors(response)

        if token_request_form.set_as_cookie is True:
            # No return value since it is set as cookie
            return None  # type: ignore
        return parse_raw_as(OAuthToken, response.text)

    def revoke_token(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> None:
        response = self._client.post(
            "/auth/oauth/revoke", data={"token": token}, **request_kwargs
        )
        handle_oauth_error(response)
        handle_errors(response)

    def introspect_token(
        self,
        token: str,
        # token_type_hint: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> OAuthTokenIntrospection:
        response = self._client.post(
            "/auth/oauth/introspect", data={"token": token}, **request_kwargs
        )
        handle_errors(response)
        return parse_raw_as(OAuthTokenIntrospection, response.text)

    # User Operations

    def list_users(self, request_kwargs: Dict = {}) -> List[Union[User, UserRead]]:
        response = self._client.get("/users", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[Union[User, UserRead]], response.text)

    def create_user(
        self,
        user_input: UserRegistration,
        technical_user: bool = False,
        request_kwargs: Dict = {},
    ) -> User:
        response = self._client.post(
            "/users",
            data=user_input.json(exclude_unset=True),
            params={"technical_user": technical_user},
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(User, response.text)

    def get_user(self, user_id: str, request_kwargs: Dict = {}) -> User:
        response = self._client.get(f"/users/{user_id}", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(User, response.text)

    def get_user_with_permission(
        self, user_id: str, request_kwargs: Dict = {}
    ) -> UserPermission:
        response = self._client.get(f"/users/{user_id}", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(UserPermission, response.text)

    def update_user(
        self, user_id: str, user_input: UserInput, request_kwargs: Dict = {}
    ) -> User:
        response = self._client.patch(
            f"/users/{user_id}",
            data=user_input.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(User, response.text)

    def delete_user(self, user_id: str, request_kwargs: Dict = {}) -> None:
        response = self._client.delete(f"/users/{user_id}", **request_kwargs)
        handle_errors(response)

    def get_user_token(
        self,
        user_id: str,
        access_level: AccessLevel = AccessLevel.WRITE,
        request_kwargs: Dict = {},
    ) -> str:
        response = self._client.get(
            f"/users/{user_id}/token",
            params={"access_level": access_level.value},
            **request_kwargs,
        )
        handle_errors(response)
        return response.json()
