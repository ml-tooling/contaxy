from typing import Generator, Union

import pytest
import requests
from fastapi.testclient import TestClient

from .shared import ADMIN_API_TOKEN, BackendClient

pytestmark = pytest.mark.integration


class BaseUrlSession(requests.Session):
    def __init__(self, base_url=None, *args, **kwargs):
        super(BaseUrlSession, self).__init__(*args, **kwargs)
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = self.base_url + url
        return super(BaseUrlSession, self).request(method, url, *args, **kwargs)


@pytest.fixture(scope="session")
def client() -> Generator[requests.Session, None, None]:
    print("Create client fixture")
    client_config = BackendClient()
    test_client: Union[requests.Session, None] = None

    if client_config.base_url == "":
        print("Use FastAPI.TestClient as client_config.endpoint is empty.")
        from ...src.contaxy.dependencies import get_authenticated_user
        from ...src.contaxy.main import app
        from ...src.contaxy.models.users import User

        def _mocked_get_authenticated_user() -> User:
            return User(
                id="admin", username="admin", password="admin", scopes=["admin"]
            )

        app.dependency_overrides[
            get_authenticated_user
        ] = _mocked_get_authenticated_user
        test_client = TestClient(app=app, root_path=client_config.root_path)
    else:
        print(
            f"Use requests.Session as client_config.endpoint is set to {client_config.endpoint}"
        )

        # TODO: check whether the token is valid before doing more tests

        test_client = BaseUrlSession(base_url=client_config.base_url)

    yield test_client
    # do some tear_down stuff here


@pytest.fixture(scope="session")
def admin_token() -> str:
    # Token with username admin and no expiry time
    return f"Bearer {ADMIN_API_TOKEN}"
