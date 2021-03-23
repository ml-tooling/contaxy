from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Set

import pytest
from faker import Faker
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.user import UserManager
from contaxy.operations import UserOperations
from contaxy.schema.user import User, UserInput
from contaxy.utils.state_utils import GlobalState, RequestState
from tests.unit_tests.conftest import test_settings

DEFAULT_USERS_TO_GENERATE = 100


@pytest.fixture()  # TODO: if the state should be preserved, use: scope="session"
def global_state() -> GlobalState:
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    return RequestState(State())


# @pytest.fixture
# def markers(request) -> List[str]:  # type: ignore
#    marks = [m.name for m in request.node.iter_markers()]
#    if request.node.parent:
#        marks += [m.name for m in request.node.parent.iter_markers()]
#    yield marks


def _generate_user_data(users_to_generate: int) -> List[UserInput]:
    fake = Faker()
    generated_users: List[UserInput] = []
    for _ in range(users_to_generate):
        # TODO: Also some with missing emails/usernames?
        generated_users.append(UserInput(username=fake.user_name(), email=fake.email()))
    return generated_users


@pytest.fixture()
def user_data() -> List[UserInput]:
    return _generate_user_data(DEFAULT_USERS_TO_GENERATE)


class UserOperationsTests(ABC):
    @property
    @abstractmethod
    def user_manager(self) -> UserOperations:
        pass

    def test_create_user(self, user_data: List[UserInput]) -> None:
        user_ids: Set[str] = set()
        for user_input in user_data:
            created_user = self.user_manager.create_user(user_input)

            assert created_user.id not in user_ids, "User IDs MUST be unique."
            user_ids.add(created_user.id)

            assert created_user.username == user_input.username
            assert created_user.email == user_input.email
            assert (
                datetime.today() - created_user.created_at
            ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."

    def test_list_users(self, user_data: List[UserInput]) -> None:
        created_users: Dict = {}
        # create all users
        for user_input in user_data:
            created_user = self.user_manager.create_user(user_input)
            created_users[created_user.id] = created_user

        users_in_db = self.user_manager.list_users()

        assert len(users_in_db) == len(
            user_data
        ), "The user count is not equal the the number of created users."

        for user in users_in_db:
            assert user.id in created_users
            assert user.username == created_users[user.id].username
            assert user.email == created_users[user.id].email

    def test_get_user(self, user_data: List[UserInput]) -> None:
        # Create and get a single user
        created_user = self.user_manager.create_user(user_data[0])
        retrieved_user = self.user_manager.get_user(created_user.id)
        assert retrieved_user.dict() == created_user.dict()

        # Create and get multiple users
        created_users: List[User] = []
        for user in user_data:
            created_users.append(self.user_manager.create_user(user))

        for created_user in created_users:
            retrieved_user = self.user_manager.get_user(created_user.id)
            # compare all properties
            assert retrieved_user.dict() == created_user.dict()

    def test_update_user(self, user_data: List[UserInput]) -> None:
        updated_users = _generate_user_data(len(user_data))
        # Create and update a single user
        for user_data, updated_user_data in zip(user_data, updated_users):
            created_user = self.user_manager.create_user(user_data)
            updated_user = self.user_manager.update_user(
                created_user.id, updated_user_data
            )
            # To make sure, get the updated user
            updated_user = self.user_manager.get_user(created_user.id)
            assert updated_user.id == created_user.id
            assert updated_user.username == updated_user_data.username
            assert updated_user.email == updated_user_data.email
            assert created_user.created_at == updated_user.created_at

    def test_delete_user(self, user_data: List[UserInput]) -> None:
        # Create and delete single user
        created_user = self.user_manager.create_user(user_data[0])
        self.user_manager.delete_user(created_user.id)
        assert len(self.user_manager.list_users()) == 0

        # Create and delete multiple users
        created_users: List[User] = []
        for user in user_data:
            created_users.append(self.user_manager.create_user(user))

        assert len(self.user_manager.list_users()) == len(user_data)

        for user in created_users:
            self.user_manager.delete_user(user.id)

        assert len(self.user_manager.list_users()) == 0


@pytest.mark.skipif(
    test_settings.POSTGRES_INTEGRATION_TESTS is False,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestUserManagerWithPostgresDB(UserOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_user_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> None:
        json_db = PostgresJsonDocumentManager(global_state, request_state)
        self._user_manager = UserManager(global_state, request_state, json_db)

    @property
    def user_manager(self) -> UserOperations:
        return self._user_manager


@pytest.mark.unit
class TestUserManagerWithInMemoryDB(UserOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_user_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> None:
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        self._user_manager = UserManager(global_state, request_state, json_db)

    @property
    def user_manager(self) -> UserOperations:
        return self._user_manager
