import pytest
import requests

from tests.endpoint_tests.shared import request_system_info


@pytest.mark.integration
class TestApi:
    def test_echo(self, client: requests.Session, admin_token: str) -> None:
        client.headers.update({"authorization": admin_token})
        response = request_system_info(client=client)
        assert response.status_code == 200
        assert response.json()["namespace"] == "ctxy"
