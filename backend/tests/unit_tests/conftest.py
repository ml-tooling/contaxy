import os

import pytest

pytestmark = pytest.mark.unit

from ...src.contaxy import dependencies, main
from ...src.contaxy.config import Settings
from .utils import MONGO_CONTAINER_NAME, remove_mongo_db, start_mongo_db


def get_settings_override():
    if os.getenv("LOCAL_TEST_DOCKER_NETWORK"):
        # Docker outside Docker case e.g. when developing in the workspace
        mongo_host = MONGO_CONTAINER_NAME
        return Settings(mongo_host=mongo_host)
    else:
        # Change the default port, to prevent possible collisions with another running instance
        return Settings(mongo_host="localhost", mongo_port=27018)


main.app.dependency_overrides[dependencies.get_settings] = get_settings_override


@pytest.fixture(autouse=True, scope="session")
def setup_mongodb():
    settings = get_settings_override()
    start_mongo_db(settings)
    yield
    remove_mongo_db(settings)
