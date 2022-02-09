from typing import Dict, List, Optional

import requests
from pydantic import parse_raw_as
from requests.models import Response

from contaxy.clients.shared import handle_errors
from contaxy.operations.auth import AuthOperations
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
from contaxy.schema.auth import ApiToken, OAuth2Error, TokenPurpose


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
        token_purpose: Optional[TokenPurpose] = None,
        token_subject: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> str:
        # TODO: Implement token_purpose and token_subject
        params = {"token_type": token_type.value, "scopes": scopes}
        if description:
            params["description"] = description
        response = self._client.post("/auth/tokens", params=params, **request_kwargs)
        handle_errors(response)
        return response.json()

    def list_api_tokens(self, request_kwargs: Dict = {}) -> List[ApiToken]:
        response = self._client.get("/auth/tokens")
        handle_errors(response)
        return parse_raw_as(List[ApiToken], response.text, **request_kwargs)

    def verify_access(
        self,
        token: str,
        permission: Optional[str] = None,
        disable_cache: bool = False,
        request_kwargs: Dict = {},
    ) -> AuthorizedAccess:
        # TODO: Implement
        pass

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
        # TODO: Implement
        pass

    def remove_permission(
        self,
        resource_name: str,
        permission: str,
        remove_sub_permissions: bool = False,
        request_kwargs: Dict = {},
    ) -> None:
        # TODO: Implement
        pass

    def list_permissions(
        self,
        resource_name: str,
        resolve_roles: bool = True,
        use_cache: bool = False,
        request_kwargs: Dict = {},
    ) -> List[str]:
        # TODO: Implement
        pass

    def list_resources_with_permission(
        self,
        permission: str,
        resource_name_prefix: Optional[str] = None,
        request_kwargs: Dict = {},
    ) -> List[str]:
        # TODO: Implement
        pass

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

    def list_users(self, request_kwargs: Dict = {}) -> List[User]:
        response = self._client.get("/users", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[User], response.text)

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

    def update_user(
        self, user_id: str, user_input: UserInput, request_kwargs: Dict = {}
    ) -> User:
        response = self._client.get(
            f"/users/{user_id}",
            data=user_input.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(User, response.text)

    def delete_user(self, user_id: str, request_kwargs: Dict = {}) -> None:
        response = self._client.delete(f"/users/{user_id}", **request_kwargs)
        handle_errors(response)
