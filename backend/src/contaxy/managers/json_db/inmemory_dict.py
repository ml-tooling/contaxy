import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

import json_merge_patch

from contaxy.operations import JsonDocumentOperations
from contaxy.schema.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from contaxy.schema.json_db import JsonDocument
from contaxy.utils.state_utils import GlobalState, RequestState


class InMemoryDictJsonDocumentManager(JsonDocumentOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the Postgres Json Document Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self._global_state = global_state
        self._request_state = request_state
        self._dict_db: Optional[Dict] = None

    def _get_collection(self, project_id: str, collection_id: str) -> Dict:
        """Lazyloads the specified collection.

        Args:
            project_id: The ID of the project
            collection_id: The ID of the collection.

        Returns:
            Dict: The collection Dict.
        """
        if self._dict_db is None:
            state_namespace = self._global_state[InMemoryDictJsonDocumentManager]
            if not state_namespace.dict_db:
                state_namespace.dict_db = {}
            self._dict_db = state_namespace.dict_db

        assert self._dict_db is not None
        if project_id not in self._dict_db:
            self._dict_db[project_id] = {}

        project_db = self._dict_db[project_id]
        if collection_id not in project_db:
            project_db[collection_id] = {}

        return project_db[collection_id]

    def create_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
        upsert: bool = True,
    ) -> JsonDocument:
        """Creates a JSON document for a given key.

        If a document already exists for the given key, the document will be overwritten.

        Args:
            project_id: Project ID associated with the collection.
            collection_id: ID of the collection (database) to use to store this JSON document.
            key: Key of the JSON document.
            json_document: The actual JSON document value.
            upsert: If `True`, the document will be updated/overwritten if it already exists.

        Returns:
            JsonDocument: The created JSON document.
        """
        collection = self._get_collection(project_id, collection_id)

        if not upsert and key in collection:
            raise ResourceAlreadyExistsError(
                "A document with the key {key} already exists."
            )

        created_document = JsonDocument(
            key=key,
            json_value=json_document,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        collection[key] = created_document.dict()
        return created_document

    def update_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
    ) -> JsonDocument:
        """Updates a JSON document.

        The update is applied on the existing document based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).

        Args:
            project_id: Project ID associated with the collection.
            collection_id: ID of the collection (database) that the JSON document is stored in.
            key: Key of the JSON document.
            json_document: The actual JSON document value.

        Raises:
            ResourceNotFoundError: If no JSON document is found with the given `key`.

        Returns:
            JsonDocument: The updated JSON document.
        """
        collection = self._get_collection(project_id, collection_id)

        current_document = self.get_json_document(project_id, collection_id, key)

        updated_json = json_merge_patch.merge(
            json.loads(current_document.json_value), json.loads(json_document)
        )

        current_document.json_value = json.dumps(updated_json)
        current_document.updated_at = datetime.now(timezone.utc)
        collection[key] = current_document.dict()

        return self.get_json_document(project_id, collection_id, key)

    def list_json_documents(
        self,
        project_id: str,
        collection_id: str,
        filter: Optional[str] = None,
        keys: Optional[List[str]] = None,
    ) -> List[JsonDocument]:
        """Lists all JSON documents for the given project collection.

        Args:
            project_id: Project ID associated with the collection.
            collection_id: ID of the collection (database) that the JSON document is stored in.
            filter (optional): Allows to filter the result documents based on a JSONPath expression ([JSON Path Specification](https://goessner.net/articles/JsonPath/)). The filter is only applied to filter documents in the list. It is not usable to extract specific properties.
            keys (optional): Json Document Ids, i.e. DB row keys. Defaults to `None`.

        Returns:
            List[JsonDocument]: List of JSON documents.
        """
        # TODO: support keys parameter
        collection = self._get_collection(project_id, collection_id)
        documents: List[JsonDocument] = []
        for doc_key in collection.keys():
            documents.append(JsonDocument(**collection[doc_key]))

        if filter:
            # TODO: filter currently not working since json path of postgres is different than the impl below
            # TODO: just return all data -> implmenetation needs to take on filtering
            pass
            # Filter based on jsonpath
            # filtered_documents: List[JsonDocument] = []
            # jsonpath_expr = jsonpath_ng.ext.parse(filter)
            # for document in documents:
            #    if [
            #        match.value
            #        for match in jsonpath_expr.find([json.loads(document.json_value)])
            #    ]:
            #        filtered_documents.append(document)
            # documents = filtered_documents

        return documents

    def get_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
    ) -> JsonDocument:
        """Returns a single JSON document.

        Args:
            project_id: Project ID associated with the JSON document.
            collection_id: ID of the collection (database) that the JSON document is stored in.
            key: Key of the JSON document.

        Raises:
            ResourceNotFoundError: If no JSON document is found with the given `key`.

        Returns:
            JsonDocument: A JSON document.
        """
        collection = self._get_collection(project_id, collection_id)
        if key not in collection:
            raise ResourceNotFoundError(
                f"The json document with the key {key} does not exist."
            )

        return JsonDocument(**collection[key])

    def delete_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
    ) -> None:
        """Deletes a single JSON document.

        If no other document exists in the project collection, the collection will be deleted.

        Args:
            project_id: Project ID associated with the JSON document.
            collection_id: ID of the collection (database) that the JSON document is stored in.
            key: Key of the JSON document.

        Raises:
            ResourceNotFoundError: If no JSON document is found with the given `key`.
        """
        collection = self._get_collection(project_id, collection_id)
        if key not in collection:
            raise ResourceNotFoundError(
                f"The json document with the key {key} does not exists."
            )
        del collection[key]

    def delete_json_collection(
        self,
        project_id: str,
        collection_id: str,
    ) -> None:
        # Lazy load if not already happend
        self._get_collection(project_id, collection_id)
        # Empty out collection
        if self._dict_db and self._dict_db[project_id]:
            self._dict_db[project_id][collection_id] = {}

    def delete_json_collections(self, project_id: str) -> None:
        state_namespace = self._global_state[InMemoryDictJsonDocumentManager]
        if state_namespace.dict_db:
            state_namespace.dict_db[project_id] = {}

        if self._dict_db:
            self._dict_db[project_id] = {}  # type: ignore
