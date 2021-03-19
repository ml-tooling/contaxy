from abc import ABC, abstractmethod

import pytest
from faker import Faker
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.operations.auth import AuthOperations
from contaxy.utils import id_utils
from contaxy.utils.state_utils import GlobalState, RequestState
from tests.unit_tests.conftest import test_settings


@pytest.fixture()
def global_state() -> GlobalState:
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    return RequestState(State())


class AuthOperationsTests(ABC):
    @property
    @abstractmethod
    def auth_manager(self) -> AuthOperations:
        pass

    def test_change_password(self, faker: Faker) -> None:
        user_id = id_utils.generate_short_uuid()
        user_password = faker.password()
        self.auth_manager.change_password(user_id, user_password)
        assert self.auth_manager.verify_password(user_id, user_password) is True

    def test_verify_password(self, faker: Faker) -> None:
        # does not need any extra logic, just call the change password method
        self.test_change_password(faker)


@pytest.mark.skipif(
    test_settings.POSTGRES_INTEGRATION_TESTS is None,
    reason="POSTGRES_INTEGRATION_TESTS is not configured.",
)
@pytest.mark.integration
class TestAuthManagerWithPostgresDB(AuthOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_auth_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> None:
        json_db = PostgresJsonDocumentManager(global_state, request_state)
        self._auth_manager = AuthManager(global_state, request_state, json_db)

    @property
    def auth_manager(self) -> AuthOperations:
        return self._auth_manager


@pytest.mark.unit
class TestAuthManagerWithInMemoryDB(AuthOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_auth_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> None:
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        self._auth_manager = AuthManager(global_state, request_state, json_db)

    @property
    def auth_manager(self) -> AuthOperations:
        return self._auth_manager
