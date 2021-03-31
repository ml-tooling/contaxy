from abc import ABC, abstractmethod
from typing import List, Optional

from contaxy.schema import JsonDocument


class JsonDocumentOperations(ABC):
    @abstractmethod
    def create_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
        upsert: bool = True,
    ) -> JsonDocument:
        """Creates a JSON document for a given key.

        If a document already exists for the given key, the document will be overwritten if `upsert` is True, otherwise an error is raised.

        Args:
            project_id: Project ID associated with the collection.
            collection_id: ID of the collection (database) to use to store this JSON document.
            key: Key of the JSON document.
            json_document: The actual JSON document value.
            upsert: If `True`, the document will be updated/overwritten if it already exists.

        Raises:
            ClientValueError: If the given json_document does not contain valid json.
            ResourceAlreadyExistsError: If a document already exists for the given key and `upsert` is False.

        Returns:
            JsonDocument: The created JSON document.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
            keys (Optional[List[str]], optional): Json Document Ids, i.e. DB row keys. Defaults to None.

        Raises:
            ClientValueError: If filter is provided and does not contain a valid Json Path filter.

        Returns:
            List[JsonDocument]: List of JSON documents.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_json_collections(
        self,
        project_id: str,
    ) -> None:
        """Deletes all JSON collections for a project.

        Args:
            project_id: Project ID associated with the collections.
        """
        pass

    @abstractmethod
    def delete_json_collection(
        self,
        project_id: str,
        collection_id: str,
    ) -> None:
        """Deletes all documents of a single JSON collection.

        Args:
            project_id: Project ID associated with the collection.
            collection_id: ID of the JSON collection (database).
        """
        pass
