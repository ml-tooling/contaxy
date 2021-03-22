import os

import pytest
from pydantic import BaseSettings
from pyinstrument import Profiler


class TestSettings(BaseSettings):
    """Test Settings."""

    ACTIVATE_TEST_PROFILING: bool = True
    POSTGRES_INTEGRATION_TESTS: bool = False


test_settings = TestSettings()


@pytest.fixture(autouse=True)
def auto_profile_tests(request) -> None:  # type: ignore
    if not test_settings.ACTIVATE_TEST_PROFILING:
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
