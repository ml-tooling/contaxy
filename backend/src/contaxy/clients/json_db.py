from json.decoder import JSONDecodeError
from typing import Dict, List, Optional

import requests
from pydantic import parse_raw_as

from contaxy.clients.shared import handle_errors
from contaxy.operations import JsonDocumentOperations
from contaxy.schema import JsonDocument
from contaxy.schema.exceptions import ClientValueError


class JsonDocumentClient(JsonDocumentOperations):
    def __init__(self, client: requests.Session):
        self._client = client

    def create_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
        upsert: bool = True,
        request_kwargs: Dict = {},
    ) -> JsonDocument:
        try:
            response = self._client.put(
                f"/projects/{project_id}/json/{collection_id}/{key}",
                data=json_document,
                params={"upsert": upsert},
                **request_kwargs,
            )
            handle_errors(response)
            return parse_raw_as(JsonDocument, response.text)
        except JSONDecodeError as ex:
            raise ClientValueError("The loaded JSON is invalid.") from ex

    def update_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
        request_kwargs: Dict = {},
    ) -> JsonDocument:
        try:
            response = self._client.patch(
                f"/projects/{project_id}/json/{collection_id}/{key}",
                data=json_document,
                **request_kwargs,
            )
            handle_errors(response)
            return parse_raw_as(JsonDocument, response.text)
        except JSONDecodeError as ex:
            raise ClientValueError("The loaded JSON is invalid.") from ex

    def list_json_documents(
        self,
        project_id: str,
        collection_id: str,
        filter: Optional[str] = None,
        keys: Optional[List[str]] = None,
        request_kwargs: Dict = {},
    ) -> List[JsonDocument]:
        response = self._client.get(
            f"/projects/{project_id}/json/{collection_id}",
            params={"filter": filter},
            # TODO: support filters
            **request_kwargs,
        )
        handle_errors(response)
        return parse_raw_as(List[JsonDocument], response.text)

    def get_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        request_kwargs: Dict = {},
    ) -> JsonDocument:
        response = self._client.get(
            f"/projects/{project_id}/json/{collection_id}/{key}", **request_kwargs
        )
        handle_errors(response)
        return parse_raw_as(JsonDocument, response.text)

    def delete_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        request_kwargs: Dict = {},
    ) -> None:
        response = self._client.delete(
            f"/projects/{project_id}/json/{collection_id}/{key}", **request_kwargs
        )
        handle_errors(response)

    def delete_json_collection(
        self,
        project_id: str,
        collection_id: str,
        request_kwargs: Dict = {},
    ) -> None:
        response = self._client.delete(
            f"/projects/{project_id}/json/{collection_id}", **request_kwargs
        )
        handle_errors(response)

    def delete_json_collections(
        self,
        project_id: str,
        request_kwargs: Dict = {},
    ) -> None:
        response = self._client.delete(f"/projects/{project_id}/json", **request_kwargs)
        handle_errors(response)
