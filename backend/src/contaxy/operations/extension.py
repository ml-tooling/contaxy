from abc import ABC, abstractmethod
from typing import List, Optional

from contaxy.schema import Extension, ExtensionInput


class ExtensionOperations(ABC):
    @abstractmethod
    def list_extensions(self, project_id: str) -> List[Extension]:
        pass

    @abstractmethod
    def install_extension(
        self, extension: ExtensionInput, project_id: str
    ) -> Extension:
        pass

    @abstractmethod
    def delete_extension(
        self, project_id: str, extension_id: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    def suggest_extension_config(
        self,
        container_image: str,
        project_id: str,
    ) -> ExtensionInput:
        pass

    @abstractmethod
    def get_extension_metadata(
        self,
        project_id: str,
        extension_id: str,
    ) -> Extension:
        pass

    # TODO: v2
    # @abstractmethod
    # def set_extension_defaults(
    #    self,
    #    extension_id: str,
    #    operation_id: List[str],
    #    project_id: str,
    # ) -> Any:
    #    pass

    # TODO: v2
    # @abstractmethod
    # def get_extension_defaults(
    #     self,
    #     project_id: str,
    # ) -> Any:
    #     pass
