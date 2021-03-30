from typing import Dict

import requests
from pydantic.tools import parse_raw_as

from contaxy.clients.shared import handle_errors
from contaxy.operations.system import SystemOperations
from contaxy.schema.system import SystemInfo, SystemStatistics


class SystemClient(SystemOperations):
    def __init__(self, client: requests.Session):
        self._client = client

    def get_system_info(self, request_kwargs: Dict = {}) -> SystemInfo:
        response = self._client.get("/system/info", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(SystemInfo, response.text)

    def is_healthy(self, request_kwargs: Dict = {}) -> bool:
        response = self._client.get("/system/health", **request_kwargs)
        handle_errors(response)
        return True

    def get_system_statistics(self, request_kwargs: Dict = {}) -> SystemStatistics:
        response = self._client.get("/system/statistics", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(SystemStatistics, response.text)

    def initialize_system(self, request_kwargs: Dict = {}) -> None:
        response = self._client.post("/system/initialize", **request_kwargs)
        handle_errors(response)
