from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from contaxy.schema import JsonDocument


class JsonDocumentOperations(ABC):
    @abstractmethod
    def create_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: Dict,
    ) -> JsonDocument:
        pass

    @abstractmethod
    def update_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: dict,
    ) -> JsonDocument:
        pass

    @abstractmethod
    def list_json_documents(
        self,
        project_id: str,
        collection_id: str,
        filter: Optional[str] = None,
    ) -> List[JsonDocument]:
        pass

    @abstractmethod
    def get_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
    ) -> JsonDocument:
        pass

    @abstractmethod
    def delete_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
    ) -> None:
        pass
