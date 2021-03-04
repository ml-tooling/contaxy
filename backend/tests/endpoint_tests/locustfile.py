"""Used for Locust stress tests."""
# import os
import random

# import sys
from logging import error
from urllib.parse import urljoin

from locust import HttpUser, between, task

# Unfortunately, Locust does not allow relative imports
# sys.path.append(os.getcwd())
# from src.contaxy.managers.auth import Authenticator, Token
# from src.contaxy.managers.users import User, UserManager
from tests.endpoint_tests.shared import (
    ADMIN_API_TOKEN,
    BackendClient,
    request_echo,
    request_hello,
)

# from src.contaxy.config import Settings


class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)

    def on_start(self):
        # TODO: replace by endpoint call?
        # token: Token = Authenticator(Settings(), UserManager()).create_access_token(
        #     user=User(username="admin", password="admin", scopes=["admin"])
        # )
        # print(token)
        client_config = BackendClient()

        if client_config.endpoint == "":
            error(
                "For stress testing, the endpoint and an API Token with admin permissions have to be defined"
            )
            self.environment.runner.quit()

        # For Locust, the base_url is set via the `--host` flag when running `locust`
        if client_config.root_path != "":
            self.host = urljoin(self.host, client_config.root_path)
        self.client.headers.update({"Authorization": f"Bearer {ADMIN_API_TOKEN}"})

    @task
    def test_hello(self):
        request_hello(client=self.client)

    @task
    def test_echo(self):
        _input = random.choice(["foo", "short", "long input"])
        request_echo(client=self.client, input=_input)
