from abc import ABC, abstractmethod, abstractproperty
from typing import Iterator, List, Optional

from starlette.responses import Response

from contaxy.schema import File, FileInput, ResourceAction


class FileStream(ABC):
    @abstractproperty
    def hash(self) -> str:
        pass

    @abstractmethod
    def read(self, size: int = -1) -> bytes:
        pass


class FileOperations(ABC):
    @abstractmethod
    def list_files(
        self,
        project_id: str,
        recursive: bool = True,
        include_versions: bool = False,
        prefix: Optional[str] = None,
    ) -> List[File]:
        pass

    @abstractmethod
    def get_file_metadata(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        pass

    @abstractmethod
    def update_file_metadata(
        self,
        file: FileInput,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        pass

    @abstractmethod
    def upload_file(
        self,
        project_id: str,
        file_key: str,
        file_stream: FileStream,
        content_type: str = "application/octet-stream",
    ) -> File:
        pass

    @abstractmethod
    def download_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> Iterator[bytes]:
        pass

    @abstractmethod
    def list_file_actions(
        self, project_id: str, file_key: str, version: Optional[str] = None
    ) -> ResourceAction:
        pass

    @abstractmethod
    def execute_file_action(
        self,
        project_id: str,
        file_key: str,
        action_id: str,
        version: Optional[str] = None,
    ) -> Response:
        pass

    @abstractmethod
    def delete_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        keep_latest_version: bool = False,
    ) -> None:
        pass
