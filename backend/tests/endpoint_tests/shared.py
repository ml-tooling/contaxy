import os
from urllib.parse import urljoin

from requests import Response, Session


class MissingTokenException(Exception):
    pass


class BackendClient:
    def __init__(self, admin_api_token: str = ""):
        self.endpoint = os.getenv("CONTAXY_ENDPOINT", "")
        self.root_path = os.getenv("CONTAXY_ROOT_PATH", "/")
        self.base_url = self.endpoint
        if self.endpoint != "":
            self.base_url = urljoin(self.endpoint, self.root_path)

        self.admin_api_token = os.getenv("CONTAXY_ADMIN_API_TOKEN", admin_api_token)

        if self.endpoint != "":
            # TODO: make a request to one of the endpoints to check whether it is reachable (e.g. the health endpoint). If not, abort the test here
            pass


def request_hello(client: Session) -> Response:
    return client.get("/hello")


def request_echo(client: Session, input: str = "") -> Response:
    return client.get("/echo", params={"input": input})
