from typing import Dict, List, Optional

import requests
from pydantic.tools import parse_raw_as

from contaxy.clients.shared import handle_errors
from contaxy.operations import ExtensionOperations
from contaxy.schema.extension import Extension, ExtensionInput


class ExtensionClient(ExtensionOperations):
    def __init__(self, client: requests.Session):
        self._client = client

    @property
    def client(self) -> requests.Session:
        return self._client

    def list_extensions(
        self, project_id: str, request_kwargs: Dict = {}
    ) -> List[Extension]:
        response = self.client.get(
            f"/projects/{project_id}/extensions", **request_kwargs
        )
        handle_errors(response)
        return parse_raw_as(List[Extension], response.text)

    def install_extension(
        self, extension: ExtensionInput, project_id: str, request_kwargs: Dict = {}
    ) -> Extension:
        response = self.client.post(
            f"/projects/{project_id}/extensions",
            data=extension.json(exclude_unset=True),
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(Extension, response.text)

    def delete_extension(
        self, project_id: str, extension_id: Optional[str] = None
    ) -> None:
        raise NotImplementedError

    def suggest_extension_config(
        self,
        container_image: str,
        project_id: str,
    ) -> ExtensionInput:
        raise NotImplementedError

    def get_extension_metadata(
        self,
        project_id: str,
        extension_id: str,
    ) -> Extension:
        raise NotImplementedError
