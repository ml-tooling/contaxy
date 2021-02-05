import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from contaxy import dependencies, main
from contaxy.config import Settings

from .utils import remove_mongo_db, start_mongo_db

MONGO_CONTAINER_NAME = "contaxy-test-mongo"


def get_settings_override():
    return Settings(mongo_host=MONGO_CONTAINER_NAME, acces_token_expiry_minutes=0)


main.app.dependency_overrides[dependencies.get_settings] = get_settings_override


@pytest.fixture(autouse=True, scope="session")
def mongodb():
    settings = get_settings_override()
    start_mongo_db(settings)
    yield
    remove_mongo_db(settings)


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
    # Token with username admin and no expiry time
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwic2NvcGVzIjpbImFkbWluIl19.CU7bQ1g_ygvhRNnnc0BTwNn54NHY5Yj4SugF1G2_hvA"
