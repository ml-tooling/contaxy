import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from contaxy import dependencies, main
from contaxy.config import Settings


def get_settings_override():
    return Settings(mongo_host="mongo-test")


main.app.dependency_overrides[dependencies.get_settings] = get_settings_override


@pytest.fixture(scope="session")
def api_app() -> FastAPI:
    print("Create api_app fixture")
    return main.app


@pytest.fixture(scope="session")
def client(api_app: FastAPI) -> TestClient:
    print("Create client fixture")
    return TestClient(api_app)


@pytest.fixture(scope="session")
def admin_token() -> str:
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwic2NvcGVzIjpbImFkbWluIl0sImV4cCI6MTYxMjU0MjM4OH0.fULjUl3eSjIy0zMFxopbIG5XT1LebXPgmPeRZfotUUk"
