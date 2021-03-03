from typing import Generator, Union
from urllib.parse import urljoin

import pytest
import requests
from fastapi.testclient import TestClient

from .shared import BackendClient, MissingTokenException, request_echo, request_hello


class BaseUrlSession(requests.Session):
    def __init__(self, base_url=None, *args, **kwargs):
        super(BaseUrlSession, self).__init__(*args, **kwargs)
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super(BaseUrlSession, self).request(method, url, *args, **kwargs)


@pytest.fixture(scope="session")
def client() -> Generator[requests.Session, None, None]:
    client_config = BackendClient()
    test_client: Union[requests.Session, None] = None
    if client_config.base_url == "":
        print("Use FastAPI.TestClient as client_config.endpoint is empty.")
        from ...src.contaxy.dependencies import get_authenticated_user
        from ...src.contaxy.main import app
        from ...src.contaxy.users import User

        def _mocked_get_authenticated_user() -> User:
            return User(
                username="TestAdmin", password="TestAdminPass", scopes=["admin"]
            )

        app.dependency_overrides[
            get_authenticated_user
        ] = _mocked_get_authenticated_user
        test_client = TestClient(app=app, root_path=client_config.root_path)
    else:
        print(
            f"Use requests.Session as client_config.endpoint is set to {client_config.endpoint}"
        )
        if client_config.admin_api_token == "":
            raise MissingTokenException(
                "When specifying an endpoint, the test client needs an API Token with admin permissions to perform endpoint tests!"
            )

        test_client = BaseUrlSession(base_url=client_config.base_url)

    test_client.headers.update(
        {"Authorization": f"Bearer {client_config.admin_api_token}"}
    )
    yield test_client
    # do some tear_down stuff here


@pytest.mark.integration
class TestApi:
    def test_hello(self, client: requests.Session):
        response = request_hello(client=client)
        assert response.status_code == 200

    @pytest.mark.parametrize("input", ["foo", "bar"])
    def test_echo(self, client: requests.Session, input: str):
        response = request_echo(client=client, input=input)
        assert response.status_code == 200
        assert len(response.json()) == len(input)
        assert response.json() == input
