import os
from typing import Dict
from urllib.parse import urljoin

import pytest
from requests import Response, Session

pytestmark = pytest.mark.integration

ADMIN_API_TOKEN = os.getenv(
    "CONTAXY_ADMIN_API_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwic2NvcGVzIjpbImFkbWluIl19.CU7bQ1g_ygvhRNnnc0BTwNn54NHY5Yj4SugF1G2_hvA",
)


class BackendClient:
    def __init__(self):
        self.endpoint = os.getenv("CONTAXY_ENDPOINT", "")
        self.root_path = os.getenv("CONTAXY_ROOT_PATH", "/")
        self.base_url = self.endpoint
        if self.endpoint != "":
            self.base_url = urljoin(self.endpoint, self.root_path)

        if self.endpoint != "":
            # TODO: make a request to one of the endpoints to check whether it is reachable (e.g. the health endpoint). If not, abort the test here
            pass


def request_echo(client: Session, input: str = "") -> Response:
    return client.get("/echo", params={"input": input})


def request_authorized_echo(client: Session, input: str = "") -> Response:
    return client.get("/authorized-echo", params={"input": input})


def request_login(client: Session, form_data: Dict[str, str] = {}) -> Response:
    return client.post("/auth/login", data=form_data)


def request_user_profile(client: Session) -> Response:
    return client.get("/users/me")
