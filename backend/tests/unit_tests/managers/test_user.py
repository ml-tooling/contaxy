from datetime import datetime
from typing import Dict, List, Set

import pytest
from faker import Faker
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.user import UserManager
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema.user import User, UserInput
from contaxy.utils.state_utils import GlobalState, RequestState

DEFAULT_USERS_TO_GENERATE = 100


@pytest.fixture()  # TODO: if the state should be preserved, use: scope="session"
def global_state() -> GlobalState:
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    return RequestState(State())


@pytest.fixture()
def json_document_manager(
    global_state: GlobalState, request_state: RequestState
) -> JsonDocumentOperations:
    return InMemoryDictJsonDocumentManager(global_state, request_state)


@pytest.fixture()
def user_manager(
    global_state: GlobalState,
    request_state: RequestState,
    json_document_manager: JsonDocumentOperations,
) -> JsonDocumentOperations:
    return UserManager(global_state, request_state, json_document_manager)


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


def test_create_user(user_manager: UserManager, user_data: List[UserInput]) -> None:
    user_ids: Set[str] = set()
    for user_input in user_data:
        created_user = user_manager.create_user(user_input)

        assert created_user.id not in user_ids, "User IDs MUST be unique."
        user_ids.add(created_user.id)

        assert created_user.username == user_input.username
        assert created_user.email == user_input.email
        assert (
            datetime.today() - created_user.created_at
        ).seconds < 300, "Creation timestamp MUST be from a few seconds ago."


def test_list_users(user_manager: UserManager, user_data: List[UserInput]) -> None:
    created_users: Dict = {}
    # create all users
    for user_input in user_data:
        created_user = user_manager.create_user(user_input)
        created_users[created_user.id] = created_user

    users_in_db = user_manager.list_users()

    assert len(users_in_db) == len(
        user_data
    ), "The user count is not equal the the number of created users."

    for user in users_in_db:
        assert user.id in created_users
        assert user.username == created_users[user.id].username
        assert user.email == created_users[user.id].email


def test_get_user(user_manager: UserManager, user_data: List[UserInput]) -> None:
    # Create and get a single user
    created_user = user_manager.create_user(user_data[0])
    retrieved_user = user_manager.get_user(created_user.id)
    assert retrieved_user.dict() == created_user.dict()

    # Create and get multiple users
    created_users: List[User] = []
    for user in user_data:
        created_users.append(user_manager.create_user(user))

    for created_user in created_users:
        retrieved_user = user_manager.get_user(created_user.id)
        # compare all properties
        assert retrieved_user.dict() == created_user.dict()


def test_update_user(user_manager: UserManager, user_data: List[UserInput]) -> None:
    # Create and update a single user
    for user in user_data:
        created_user = user_manager.create_user(user)
        updated_user_data = _generate_user_data(1)[0]
        updated_user = user_manager.update_user(created_user.id, updated_user_data)
        # To make sure, get the updated user
        updated_user = user_manager.get_user(created_user.id)
        assert updated_user.id == created_user.id
        assert updated_user.username == updated_user_data.username
        assert updated_user.email == updated_user_data.email
        assert created_user.created_at == updated_user.created_at


def test_delete_user(user_manager: UserManager, user_data: List[UserInput]) -> None:
    # Create and delete single user
    created_user = user_manager.create_user(user_data[0])
    user_manager.delete_user(created_user.id)
    assert len(user_manager.list_users()) == 0

    # Create and delete multiple users
    created_users: List[User] = []
    for user in user_data:
        created_users.append(user_manager.create_user(user))

    assert len(user_manager.list_users()) == len(user_data)

    for user in created_users:
        user_manager.delete_user(user.id)

    assert len(user_manager.list_users()) == 0
