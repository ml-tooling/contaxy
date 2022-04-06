from abc import ABC, abstractmethod
from datetime import datetime, timezone
from random import randrange
from typing import Generator, List, Set

import pytest
import requests
from faker import Faker
from jose import jwt

from contaxy import config
from contaxy.clients import AuthClient, JsonDocumentClient
from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.operations import AuthOperations, JsonDocumentOperations
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2Error,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
    TokenType,
    User,
    UserRegistration,
)
from contaxy.schema.exceptions import (
    PermissionDeniedError,
    ResourceNotFoundError,
    UnauthenticatedError,
)
from contaxy.utils import auth_utils, id_utils
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings
from .utils import ComponentManagerMock

DEFAULT_USERS_TO_GENERATE = 3


def _generate_user_data() -> List[UserRegistration]:
    fake = Faker()
    generated_users: List[UserRegistration] = [
        UserRegistration(
            username=fake.user_name() + id_utils.generate_short_uuid(),
            email=fake.email(),
            password=fake.password(length=12),
        ),
        # User without password:
        UserRegistration(
            username=fake.user_name() + id_utils.generate_short_uuid(),
            email=fake.email(),
        )
        # TODO: Also some with missing emails/usernames?
    ]
    return generated_users


@pytest.fixture()
def user_data() -> List[UserRegistration]:
    return _generate_user_data()


class AuthOperationsTests(ABC):
    @property
    @abstractmethod
    def auth_manager(self) -> AuthOperations:
        pass

    @property
    @abstractmethod
    def json_db(self) -> JsonDocumentOperations:
        pass

    def test_permission_handling(self) -> None:
        added_resources = set()
        for _ in range(3):
            resource_name = "users/" + id_utils.generate_short_uuid()
            added_permissions = []
            for _ in range(randrange(3)):
                project = id_utils.generate_short_uuid()
                permission = f"projects/{project}#write"
                self.auth_manager.add_permission(resource_name, permission)
                added_resources.add(resource_name)
                added_permissions.append(permission)
            resource_permissions = self.auth_manager.list_permissions(resource_name)
            assert len(resource_permissions) == len(added_permissions)
            # Check if permissions where added
            for added_permission in added_permissions:
                assert added_permission in resource_permissions
            # Remove permissions
            for added_permission in added_permissions:
                self.auth_manager.remove_permission(resource_name, added_permission)
            assert len(self.auth_manager.list_permissions(resource_name)) == 0

    def test_remove_single_permission(self) -> None:
        resource_name = "users/" + id_utils.generate_short_uuid()
        project = id_utils.generate_short_uuid()
        permission = f"projects/{project}"
        self.auth_manager.add_permission(resource_name, permission)
        self.auth_manager.remove_permission(resource_name, permission)
        assert len(self.auth_manager.list_permissions(resource_name)) == 0

    def test_remove_multiple_permission(self) -> None:
        resource_name = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.add_permission(
            resource_name, f"projects/{id_utils.generate_short_uuid()}#read"
        )
        self.auth_manager.add_permission(
            resource_name, f"projects/{id_utils.generate_short_uuid()}#read"
        )
        self.auth_manager.add_permission(
            resource_name, f"users/{id_utils.generate_short_uuid()}#read"
        )
        self.auth_manager.add_permission(
            resource_name, f"test/{id_utils.generate_short_uuid()}#read"
        )
        assert len(self.auth_manager.list_permissions(resource_name)) == 4
        self.auth_manager.remove_permission(
            resource_name, "projects#read", remove_sub_permissions=True
        )
        assert len(self.auth_manager.list_permissions(resource_name)) == 2
        self.auth_manager.remove_permission(
            resource_name, "*#read", remove_sub_permissions=True
        )
        assert len(self.auth_manager.list_permissions(resource_name)) == 0

    def test_list_permissions(self, user_data: List[UserRegistration]) -> None:
        # create role
        TEST_ROLE = "roles/test"
        TEST_PERMISSION = "test#read"
        self.auth_manager.add_permission(TEST_ROLE, TEST_PERMISSION)

        assert len(self.auth_manager.list_permissions(TEST_ROLE)) == 1

        # create user with role and project permission
        user = self.auth_manager.create_user(user_data[0])
        PROJECT_PERMISSION = f"projects/{id_utils.generate_short_uuid()}#admin"
        USER_RESOURCE = "users/" + user.id
        self.auth_manager.add_permission(USER_RESOURCE, TEST_ROLE)
        self.auth_manager.add_permission(USER_RESOURCE, PROJECT_PERMISSION)

        # If not resolved, it contains the project permission and role
        unresolved_permissions = self.auth_manager.list_permissions(
            USER_RESOURCE, resolve_roles=False
        )
        assert TEST_ROLE in unresolved_permissions
        assert PROJECT_PERMISSION in unresolved_permissions
        assert TEST_PERMISSION not in unresolved_permissions

        # Resolved permissions should contain the permission of the role
        resolved_permissions = self.auth_manager.list_permissions(
            USER_RESOURCE, resolve_roles=True
        )
        assert TEST_PERMISSION in resolved_permissions
        assert PROJECT_PERMISSION in unresolved_permissions
        assert TEST_ROLE not in resolved_permissions

        # Add the role to itself
        self.auth_manager.add_permission(TEST_ROLE, TEST_ROLE)
        resolved_permissions = self.auth_manager.list_permissions(
            TEST_ROLE, resolve_roles=True
        )
        # The role should have 1 permissions, since the added one is not a valid base permission
        assert len(resolved_permissions) == 1

        # Clean up user and role
        self.auth_manager.delete_user(user.id)
        self.auth_manager.remove_permission(
            TEST_ROLE, "*#admin", remove_sub_permissions=True
        )

    def test_list_resources_with_permission(self) -> None:
        PROJECT_PERMISSION_1 = "projects/" + id_utils.generate_short_uuid() + "#admin"
        PROJECT_PERMISSION_2 = "projects/" + id_utils.generate_short_uuid() + "#admin"

        # create users
        self.auth_manager.add_permission(
            "users/" + id_utils.generate_short_uuid(), PROJECT_PERMISSION_1
        )
        self.auth_manager.add_permission(
            "users/" + id_utils.generate_short_uuid(), PROJECT_PERMISSION_1
        )
        self.auth_manager.add_permission(
            "users/" + id_utils.generate_short_uuid(), PROJECT_PERMISSION_2
        )

        assert (
            len(self.auth_manager.list_resources_with_permission(PROJECT_PERMISSION_1))
            == 2
        )
        assert (
            len(
                self.auth_manager.list_resources_with_permission(
                    PROJECT_PERMISSION_1, "users/"
                )
            )
            == 2
        )
        assert (
            len(
                self.auth_manager.list_resources_with_permission(
                    PROJECT_PERMISSION_1, "other-prefix/"
                )
            )
            == 0
        )
        assert (
            len(self.auth_manager.list_resources_with_permission(PROJECT_PERMISSION_2))
            == 1
        )

    def test_verify_access(self) -> None:
        PROJECT = "projects/" + id_utils.generate_short_uuid()
        USER_ROLE = "roles/user"
        self.auth_manager.add_permission(USER_ROLE, "projects/shared#read")
        USER = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.add_permission(USER, PROJECT + "#admin")
        self.auth_manager.add_permission(USER, USER_ROLE)
        token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=[PROJECT + "#write"],
            token_type=TokenType.API_TOKEN,
            description="This is a test token.",
        )

        USE_CACHE = True
        self.auth_manager.verify_access(token, PROJECT + "#write", use_cache=USE_CACHE)

        authorized_access = self.auth_manager.verify_access(
            token, PROJECT + "#read", use_cache=USE_CACHE
        )
        assert authorized_access.access_level is AccessLevel.READ
        assert authorized_access.resource_name == PROJECT
        # TODO: Test token_subject
        # assert authorized_access.authorized_subject == USER

        self.auth_manager.verify_access(
            token, PROJECT + "/services#read", use_cache=USE_CACHE
        )

        with pytest.raises(PermissionDeniedError):
            self.auth_manager.verify_access(
                token, PROJECT + "#admin", use_cache=USE_CACHE
            )

        with pytest.raises(UnauthenticatedError):
            self.auth_manager.verify_access(
                id_utils.generate_short_uuid(), PROJECT + "#write", use_cache=USE_CACHE
            )

        session_token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=[PROJECT + "#write"],
            token_type=TokenType.SESSION_TOKEN,
        )

        assert (
            self.auth_manager.verify_access(
                session_token, PROJECT + "#read", use_cache=USE_CACHE
            ).access_level
            is AccessLevel.READ
        )

    def test_revoke_token(self) -> None:
        PROJECT = "projects/" + id_utils.generate_short_uuid()
        USER = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.add_permission(USER, PROJECT + "#admin")

        token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=[PROJECT + "#write", "projects#read"],
            token_type=TokenType.API_TOKEN,
            description="This is a test token.",
        )

        assert (
            self.auth_manager.verify_access(
                token, PROJECT + "#read", use_cache=False
            ).access_level
            is AccessLevel.READ
        )

        self.auth_manager.revoke_token(token)

        # Token is revoked -> this should result in an Unauthenticated error
        with pytest.raises(UnauthenticatedError):
            self.auth_manager.verify_access(token, PROJECT + "#read", use_cache=False)

        # Nothing should happen
        self.auth_manager.revoke_token("aosdkadpkad")
        self.auth_manager.revoke_token(token)

        session_token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=[PROJECT + "#write", "projects#read"],
            token_type=TokenType.SESSION_TOKEN,
        )

        with pytest.raises(OAuth2Error):
            self.auth_manager.revoke_token(session_token)

    def test_introspect_token(self) -> None:
        PROJECT = "projects/" + id_utils.generate_short_uuid()
        USER = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.add_permission(USER, PROJECT + "#admin")

        token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=[PROJECT + "#write", "projects#read"],
            token_type=TokenType.API_TOKEN,
            description="This is a test token.",
        )

        token_introspection = self.auth_manager.introspect_token(token)
        assert token_introspection.active is True
        # TODO: Test token_subject
        # assert token_introspection.sub == USER
        assert (PROJECT + "#write") in token_introspection.scope
        assert (
            datetime.now(timezone.utc)
            - datetime.fromtimestamp(token_introspection.iat, tz=timezone.utc)
        ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."

        self.auth_manager.revoke_token(token)
        token_introspection = self.auth_manager.introspect_token(token)
        assert token_introspection.active is False

    def test_request_token_password_grant(self) -> None:
        generated_user = _generate_user_data(1)[0]
        password = generated_user.password  # .get_secret_value()
        self.auth_manager.create_user(generated_user)
        USER_SCOPE = "projects/" + id_utils.generate_short_uuid() + "#write"
        oauth_token = self.auth_manager.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=generated_user.username,
                password=password,
                scope=USER_SCOPE + " system#read",
            )
        )

        assert oauth_token.access_token is not None
        assert USER_SCOPE in oauth_token.scope
        assert oauth_token.token_type == "bearer"

        with pytest.raises(OAuth2Error):
            self.auth_manager.request_token(
                OAuth2TokenRequestFormNew(
                    grant_type=OAuth2TokenGrantTypes.PASSWORD,
                    username=generated_user.username,
                    password="blub",
                )
            )

        with pytest.raises(OAuth2Error):
            self.auth_manager.request_token(
                OAuth2TokenRequestFormNew(
                    grant_type=OAuth2TokenGrantTypes.PASSWORD,
                    username="blub",
                    password=password,
                )
            )

        with pytest.raises(OAuth2Error):
            self.auth_manager.request_token(
                OAuth2TokenRequestFormNew(
                    grant_type=OAuth2TokenGrantTypes.CLIENT_CREDENTIALS,
                    username=generated_user.username,
                    password=password,
                )
            )

    def test_create_user(self, user_data: List[UserRegistration]) -> None:
        user_ids: Set[str] = set()
        for user_input in user_data:
            created_user = self.auth_manager.create_user(user_input.copy())

            assert created_user.id not in user_ids, "User IDs MUST be unique."
            user_ids.add(created_user.id)

            assert created_user.username == user_input.username
            assert created_user.email == user_input.email
            assert (
                datetime.now(timezone.utc) - created_user.created_at
            ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."
            assert created_user.has_password == (user_input.password is not None)

    def test_list_users(self, user_data: List[UserRegistration]) -> None:
        created_users = []
        # create all users
        for user_input in user_data:
            created_user = self.auth_manager.create_user(user_input)
            created_users.append(created_user)

        users_in_db = {user.id: user for user in self.auth_manager.list_users()}

        for user in created_users:
            assert user.id in users_in_db
            assert user.username == users_in_db[user.id].username
            assert user.email == users_in_db[user.id].email

    def test_get_user(self, user_data: List[UserRegistration]) -> None:
        # Create and get a single user
        created_user = self.auth_manager.create_user(_generate_user_data(1)[0])
        retrieved_user = self.auth_manager.get_user(created_user.id)
        assert retrieved_user.dict() == created_user.dict()

        # Create and get multiple users
        created_users: List[User] = []
        for user in user_data:
            created_users.append(self.auth_manager.create_user(user))

        for created_user in created_users:
            retrieved_user = self.auth_manager.get_user(created_user.id)
            # compare all properties
            assert retrieved_user.dict() == created_user.dict()

    def test_update_user(self, user_data: List[UserRegistration]) -> None:
        updated_users = _generate_user_data(len(user_data))
        # Create and update a single user
        for user_data, updated_user_data in zip(user_data, updated_users):
            created_user = self.auth_manager.create_user(user_data)
            updated_user = self.auth_manager.update_user(
                created_user.id, updated_user_data
            )
            assert updated_user.id == created_user.id
            assert updated_user.created_at == created_user.created_at
            assert updated_user.username == updated_user_data.username
            assert updated_user.email == updated_user_data.email

    def test_delete_user(self) -> None:
        # Create and delete single user
        created_user = self.auth_manager.create_user(_generate_user_data(1)[0])
        user_resource_name = f"users/{created_user.id}"
        self.auth_manager.add_permission(user_resource_name, "test#read")
        self.auth_manager.delete_user(created_user.id)
        with pytest.raises(ResourceNotFoundError):
            self.auth_manager.get_user(created_user.id)
        # Check that all other resources have been cleaned up
        # assert len(self.auth_manager.list_permissions(user_resource_name)) == 0
        with pytest.raises(ResourceNotFoundError):
            self.json_db.get_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                AuthManager._USER_PASSWORD_COLLECTION,
                key=created_user.id,
            )
        with pytest.raises(ResourceNotFoundError):
            self.json_db.get_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                AuthManager._LOGIN_ID_MAPPING_COLLECTION,
                key=created_user.username,
            )
        with pytest.raises(ResourceNotFoundError):
            self.json_db.get_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                AuthManager._LOGIN_ID_MAPPING_COLLECTION,
                key=created_user.email,
            )


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestAuthManagerWithPostgresDB(AuthOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_auth_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        self._json_db = PostgresJsonDocumentManager(global_state, request_state)
        # Cleanup everything at the startup
        self._json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        self._auth_manager = AuthManager(
            ComponentManagerMock(
                global_state, request_state, json_db_manager=self._json_db
            )
        )
        yield

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager

    @property
    def json_db(self) -> JsonDocumentOperations:
        return self._json_db


@pytest.mark.unit
class TestAuthManagerWithInMemoryDB(AuthOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_auth_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        self._json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        self._json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        self._auth_manager = AuthManager(
            ComponentManagerMock(
                global_state, request_state, json_db_manager=self._json_db
            )
        )
        yield
        self._json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager

    @property
    def json_db(self) -> JsonDocumentOperations:
        return self._json_db

    def test_change_password(self, faker: Faker) -> None:
        user_id = id_utils.generate_short_uuid()
        user_password = faker.password()
        self.auth_manager.change_password(user_id, user_password)
        assert self.auth_manager.verify_password(user_id, user_password) is True

    def test_create_token(self) -> None:
        USER = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.create_token(
            token_subject=USER,
            scopes=["projects#read", "system#read"],
            token_type=TokenType.API_TOKEN,
            description="This is a test token.",
        )
        self.auth_manager.create_token(
            token_subject=USER,
            scopes=["projects#read"],
            token_type=TokenType.API_TOKEN,
            description="This is another token.",
        )

        session_token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=["projects#read"],
            token_type=TokenType.SESSION_TOKEN,
            description="This is another token.",
        )

        payload = jwt.decode(
            session_token,
            settings.JWT_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        assert payload.get("sub") == USER
        assert len(self.auth_manager.list_api_tokens(USER)) == 2


@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_ENDPOINT,
    reason="No remote backend is configured (via REMOTE_BACKEND_ENDPOINT).",
)
@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_TESTS,
    reason="Remote Backend Tests are deactivated, use REMOTE_BACKEND_TESTS to activate.",
)
@pytest.mark.integration
class TestAuthManagerViaRemoteEndpoints(AuthOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self, remote_client: requests.Session) -> Generator:
        self._endpoint_client = remote_client
        self._auth_manager = AuthClient(self._endpoint_client)
        self._json_db = JsonDocumentClient(self._endpoint_client)

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        yield

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager

    @property
    def json_db(self) -> JsonDocumentOperations:
        return self._json_db

    def login_user(self, username: str, password: str) -> None:
        self.auth_manager.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=username,
                password=password,
                scope=auth_utils.construct_permission(
                    "*", AccessLevel.ADMIN
                ),  # Get full scope
                set_as_cookie=True,
            )
        )
