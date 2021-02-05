import json

from fastapi.testclient import TestClient


def test_login(client: TestClient) -> None:

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    form_data = {
        "username": "admin",
        "password": "admin",
    }

    response = client.post("/auth/login", headers=headers, data=form_data)
    assert response.status_code == 200
    response_data = json.loads(response.text)
    assert response_data.get("access_token")


def test_user_profile(client: TestClient, admin_token: str) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": admin_token,
    }
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    response_data = json.loads(response.text)
    assert response_data.get("username") == "admin"
    assert "password" not in response_data
