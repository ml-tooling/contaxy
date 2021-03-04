import json

import pytest

from .shared import request_login, request_user_profile


@pytest.mark.skip(reason="Database code to use Postgres has to be finished")
@pytest.mark.integration
class TestAuthApi:
    def test_login(self, client) -> None:

        client.headers.update(
            {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        response = request_login(
            client=client, form_data={"username": "admin", "password": "admin"}
        )
        assert response.status_code == 200
        response_data = json.loads(response.text)
        assert response_data.get("access_token")

    def test_user_profile(self, client, admin_token: str) -> None:
        client.headers.update(
            {"accept": "application/json", "authorization": admin_token}
        )
        response = request_user_profile(client=client)
        assert response.status_code == 200
        response_data = json.loads(response.text)
        assert response_data.get("username") == "admin"
        assert "password" not in response_data
