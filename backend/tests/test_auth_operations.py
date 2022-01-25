from abc import ABC, abstractmethod
from datetime import datetime, timezone
from random import randrange
from typing import Dict, Generator, List, Set

import pytest
from faker import Faker
from jose import jwt

from contaxy import config
from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2Error,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
    TokenType,
    User,
    UserRegistration,
)
from contaxy.schema.exceptions import PermissionDeniedError, UnauthenticatedError
from contaxy.utils import id_utils
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings
from .utils import ComponentManagerMock

DEFAULT_USERS_TO_GENERATE = 10


def _generate_user_data(users_to_generate: int) -> List[UserRegistration]:
    fake = Faker()
    generated_users: List[UserRegistration] = []
    for _ in range(users_to_generate):
        # TODO: Also some with missing emails/usernames?

        generated_users.append(
            UserRegistration(
                username=fake.user_name() + id_utils.generate_short_uuid(),
                email=fake.email(),
                password=fake.password(length=12),
            )
        )
    return generated_users


@pytest.fixture()
def user_data() -> List[UserRegistration]:
    return _generate_user_data(DEFAULT_USERS_TO_GENERATE)


class AuthOperationsTests(ABC):
    @property
    @abstractmethod
    def auth_manager(self) -> AuthManager:
        pass

    def test_change_password(self, faker: Faker) -> None:
        user_id = id_utils.generate_short_uuid()
        user_password = faker.password()
        self.auth_manager.change_password(user_id, user_password)
        assert self.auth_manager.verify_password(user_id, user_password) is True

    def test_verify_password(self, faker: Faker) -> None:
        # does not need any extra logic, just call the change password method
        self.test_change_password(faker)

    def test_permission_handling(self, faker: Faker) -> None:
        added_resources = set()
        for _ in range(50):
            resource_name = "users/" + id_utils.generate_short_uuid()
            added_permissions = []
            for _ in range(randrange(10)):
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

    def test_remove_permission(self, faker: Faker) -> None:
        resource_name = "users/" + id_utils.generate_short_uuid()
        project = id_utils.generate_short_uuid()
        permission = f"projects/{project}"
        self.auth_manager.add_permission(resource_name, permission)
        self.auth_manager.remove_permission(resource_name, permission)
        assert len(self.auth_manager.list_permissions(resource_name)) == 0

    def test_list_permissions(self, faker: Faker) -> None:
        # create role
        USER_ROLE = "roles/user"
        SYSTEM_READ_PERMISSION = "system#read"
        self.auth_manager.add_permission(USER_ROLE, "projects/shared#read")
        self.auth_manager.add_permission(USER_ROLE, SYSTEM_READ_PERMISSION)

        assert len(self.auth_manager.list_permissions(USER_ROLE)) == 2

        # create user
        USER_RESOURCE = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.add_permission(USER_RESOURCE, USER_ROLE)
        self.auth_manager.add_permission(
            USER_RESOURCE, f"projects/{id_utils.generate_short_uuid()}#admin"
        )

        # If not resolved, it contains the project permission and role
        unresolved_permissions = self.auth_manager.list_permissions(
            USER_RESOURCE, resolve_roles=False
        )
        assert len(unresolved_permissions) == 2
        assert USER_ROLE in unresolved_permissions

        # Resolved permissions should contain the permission of the role
        resolved_permissions = self.auth_manager.list_permissions(
            USER_RESOURCE, resolve_roles=True
        )
        assert len(resolved_permissions) == 3
        assert SYSTEM_READ_PERMISSION in resolved_permissions

        # Add the role to itself
        self.auth_manager.add_permission(USER_ROLE, USER_ROLE)
        resolved_permissions = self.auth_manager.list_permissions(
            USER_ROLE, resolve_roles=True
        )
        # The role should have 2 permissions, sine the added one is not a valid base permission
        assert len(resolved_permissions) == 2

    def test_list_resources_with_permission(self, faker: Faker) -> None:
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

    def test_verify_access(self) -> None:
        PROJECT = "projects/" + id_utils.generate_short_uuid()
        USER_ROLE = "roles/user"
        self.auth_manager.add_permission(USER_ROLE, "projects/shared#read")
        USER = "users/" + id_utils.generate_short_uuid()
        self.auth_manager.add_permission(USER, PROJECT + "#admin")
        self.auth_manager.add_permission(USER, USER_ROLE)
        token = self.auth_manager.create_token(
            token_subject=USER,
            scopes=[PROJECT + "#write", "projects#read"],
            token_type=TokenType.API_TOKEN,
            description="This is a test token.",
        )

        USE_CACHE = True
        assert (
            self.auth_manager.verify_access(
                token, PROJECT + "#write", use_cache=USE_CACHE
            )
            is not None
        )

        assert (
            self.auth_manager.verify_access(
                token, PROJECT + "#read", use_cache=USE_CACHE
            ).access_level
            is AccessLevel.READ
        )

        assert (
            self.auth_manager.verify_access(
                token, PROJECT + "#read", use_cache=USE_CACHE
            ).authorized_subject
            == USER
        )

        assert (
            self.auth_manager.verify_access(
                token, PROJECT + "#read", use_cache=USE_CACHE
            ).resource_name
            == PROJECT
        )

        assert (
            self.auth_manager.verify_access(
                token, PROJECT + "/services#read", use_cache=USE_CACHE
            )
            is not None
        )

        assert (
            self.auth_manager.verify_access(
                token, "projects/shared#read", use_cache=USE_CACHE
            )
            is not None
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
            scopes=[PROJECT + "#write", "projects#read"],
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
        assert token_introspection.sub == USER
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
            created_user = self.auth_manager.create_user(user_input)

            assert created_user.id not in user_ids, "User IDs MUST be unique."
            user_ids.add(created_user.id)

            assert created_user.username == user_input.username
            assert created_user.email == user_input.email
            assert (
                datetime.now(timezone.utc) - created_user.created_at
            ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."

    def test_list_users(self, user_data: List[UserRegistration]) -> None:
        created_users: Dict = {}
        # create all users
        for user_input in user_data:
            created_user = self.auth_manager.create_user(user_input)
            created_users[created_user.id] = created_user

        users_in_db = self.auth_manager.list_users()

        assert len(users_in_db) == len(
            user_data
        ), "The user count is not equal the the number of created users."

        for user in users_in_db:
            assert user.id in created_users
            assert user.username == created_users[user.id].username
            assert user.email == created_users[user.id].email

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
            # To make sure, get the updated user
            updated_user = self.auth_manager.get_user(created_user.id)
            assert updated_user.id == created_user.id
            assert updated_user.username == updated_user_data.username
            assert updated_user.email == updated_user_data.email
            assert created_user.created_at == updated_user.created_at

    def test_delete_user(self, user_data: List[UserRegistration]) -> None:
        # Create and delete single user
        created_user = self.auth_manager.create_user(_generate_user_data(1)[0])
        self.auth_manager.delete_user(created_user.id)
        assert len(self.auth_manager.list_users()) == 0

        # Create and delete multiple users
        created_users: List[User] = []
        for user in user_data:
            created_users.append(self.auth_manager.create_user(user))

        assert len(self.auth_manager.list_users()) == len(user_data)

        for user in created_users:
            self.auth_manager.delete_user(user.id)

        assert len(self.auth_manager.list_users()) == 0


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
        json_db = PostgresJsonDocumentManager(global_state, request_state)
        # Cleanup everything at the startup
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        self._auth_manager = AuthManager(
            ComponentManagerMock(global_state, request_state, json_db_manager=json_db)
        )
        yield
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        # Do cleanup

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager


@pytest.mark.unit
class TestAuthManagerWithInMemoryDB(AuthOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_auth_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        self._auth_manager = AuthManager(
            ComponentManagerMock(global_state, request_state, json_db_manager=json_db)
        )
        yield
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager
