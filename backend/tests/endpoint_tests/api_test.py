import pytest
import requests

from .shared import request_echo


@pytest.mark.integration
class TestApi:
    @pytest.mark.parametrize("input", ["foo", "bar"])
    def test_echo(self, client: requests.Session, admin_token: str, input: str):
        client.headers.update({"authorization": admin_token})
        response = request_echo(client=client, input=input)
        assert response.status_code == 200
        assert len(response.json()) == len(input)
        assert response.json() == input
