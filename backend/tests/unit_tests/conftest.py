import os

import pytest
from pydantic import BaseSettings
from pyinstrument import Profiler

from contaxy import config


@pytest.fixture(autouse=True)
def auto_profile_tests(request) -> None:  # type: ignore
    if not config.settings.DEBUG:
        # Only execute if debug is activated
        yield None
    else:
        profiler = Profiler()
        profiler.start()
        yield None
        profiler.stop()
        try:
            output_file = (
                "./prof/"
                + request.node.nodeid.split("::")[0].lstrip("tests/")
                + "/"
                + request.node.name
                + ".html"
            )
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as f:
                f.write(profiler.output_html())
        except Exception:
            # Fail silently
            pass


class TestSettings(BaseSettings):
    """Test Settings."""

    POSTGRES_INTEGRATION_TESTS: bool = False


test_settings = TestSettings()
