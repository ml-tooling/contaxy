from typing import Dict, List

import requests
from pydantic.tools import parse_raw_as

from contaxy.clients.shared import handle_errors
from contaxy.operations.system import SystemOperations
from contaxy.schema.system import AllowedImageInfo, SystemInfo, SystemStatistics


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

    def list_allowed_images(self, request_kwargs: Dict = {}) -> List[AllowedImageInfo]:
        response = self._client.get("/system/allowed-images", **request_kwargs)
        handle_errors(response)
        return parse_raw_as(List[AllowedImageInfo], response.text)

    def add_allowed_image(
        self, allowed_image: AllowedImageInfo, request_kwargs: Dict = {}
    ) -> AllowedImageInfo:
        resource = self._client.post(
            "/system/allowed-images",
            data=allowed_image.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(resource)
        return parse_raw_as(AllowedImageInfo, resource.text)

    def delete_allowed_image(
        self, allowed_image_name: str, request_kwargs: Dict = {}
    ) -> None:
        response = self._client.delete(
            "/system/allowed-images",
            params={"image_name": allowed_image_name},
            **request_kwargs,
        )
        handle_errors(response)

    def check_allowed_image(self, image_name: str, image_tag: str) -> None:
        # TODO: Implement
        pass
