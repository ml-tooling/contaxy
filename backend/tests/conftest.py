import os
from typing import Optional

import pytest
import requests
from pydantic import BaseSettings
from pyinstrument import Profiler
from starlette.datastructures import State

from contaxy.clients.shared import BaseUrlSession
from contaxy.config import settings
from contaxy.utils.state_utils import GlobalState, RequestState


class TestSettings(BaseSettings):
    """Test Settings."""

    ACTIVATE_TEST_PROFILING: bool = True
    POSTGRES_INTEGRATION_TESTS: bool = False
    MINIO_INTEGRATION_TESTS: bool = False
    AZURE_BLOB_INTEGRATION_TESTS: bool = False
    REMOTE_BACKEND_TESTS: bool = True
    REMOTE_BACKEND_ENDPOINT: Optional[str] = None
    DOCKER_INTEGRATION_TESTS: bool = True
    KUBERNETES_INTEGRATION_TESTS: bool = False


test_settings = TestSettings()


@pytest.fixture()
def remote_client() -> requests.Session:
    """Initializes a remote client using the configured remote backend endpoint."""
    return BaseUrlSession(base_url=test_settings.REMOTE_BACKEND_ENDPOINT)


@pytest.fixture()
def global_state() -> GlobalState:
    """Initializes global state."""
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    """Initializes request state."""
    request_state = RequestState(State())
    return request_state


@pytest.fixture(autouse=True)
def auto_profile_tests(request) -> None:  # type: ignore
    """Activates automatic profiling."""
    if not test_settings.ACTIVATE_TEST_PROFILING:
        # Only execute if debug is activated
        yield None
    else:
        profiler = Profiler()
        profiler.start()
        yield None
        profiler.stop()
        try:
            output_file = "./prof/" + request.node.nodeid.replace("::", "/") + ".html"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as f:
                f.write(profiler.output_html())
        except Exception:
            # Fail silently
            pass
