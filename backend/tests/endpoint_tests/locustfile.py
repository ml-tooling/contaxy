"""Used for Locust stress tests."""
from logging import error
from urllib.parse import urljoin

from locust import HttpUser, between, task

from tests.endpoint_tests.shared import (
    ADMIN_API_TOKEN,
    BackendClient,
    request_system_info,
)


class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)
    # For Locust, the base_url is set via the `--host` flag when running `locust`
    host: str

    def on_start(self) -> None:
        client_config = BackendClient(endpoint=self.host)

        if client_config.endpoint == "":
            error(
                "For stress testing, the endpoint has to be defined by setting `CONTAXY_ENDPOINT` (e.g `CONTAXY_ENDPOINT=http://localhost:8000`)."
            )
            self.environment.runner.quit()

        if client_config.root_path != "":
            self.host = urljoin(self.host, client_config.root_path)
        self.client.headers.update({"Authorization": f"Bearer {ADMIN_API_TOKEN}"})

    @task
    def test_system_info(self) -> None:
        request_system_info(client=self.client)
