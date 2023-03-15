from abc import ABC, abstractmethod
from datetime import datetime
from typing import IO, Any, Dict, Iterator, List, Optional, Tuple

from contaxy.schema import File, FileInput, ResourceAction


class FileOperations(ABC):
    @abstractmethod
    def list_files(
        self,
        project_id: str,
        recursive: bool = True,
        include_versions: bool = False,
        prefix: Optional[str] = None,
    ) -> List[File]:
        """List files.

        Args:
            project_id (str): Project ID associated with the file.
            recursive (bool, optional): List recursively as directory structure emulation. Defaults to True.
            include_versions (bool, optional): Flag to control whether include object versions. Defaults to False.
            prefix (Optional[str], optional): File key starts with prefix. Defaults to None.

        Returns:
            List[File]: List of file metadata objects.
        """
        pass

    @abstractmethod
    def get_file_metadata(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        """Get file metadata of a single file.

        If no version is provided then the latest version will be returned.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.

        Raises:
            ResourceNotFoundError: If no file is found.

        Returns:
            File: The file metadata object.
        """
        pass

    @abstractmethod
    def update_file_metadata(
        self,
        file: FileInput,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> File:
        """Update the file metadata.

        If no version is provided then the latest version will be returned. Moreover, additional custom metadata provied via `file.metadata` will executed with json merge patch strategy in case a specific version is updated. But if a new version was created it is treated as a new file and hence the metadata from older versions will not be considered. If a version should inherit the metadata from a previous version, then this data needs to be set explictly.

        Args:
            file (FileInput): The file metadata object. All unset attributes or None values will be ignored.
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.

        Raises:
            ClientValueError: If the provided keys do not match.

        Returns:
            File: The updated file metadata object.
        """
        pass

    @abstractmethod
    def upload_file(
        self,
        project_id: str,
        file_key: str,
        file_stream: IO[bytes],
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ) -> File:
        """Upload a file.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            file_stream (IO): The actual file stream object.
            metadata (Dict, optional): Additional key-value pairs of file meta data
            content_type (str, optional): The mime-type of the file. Defaults to "application/octet-stream".

        Raises:
            ServerBaseError: If the upload failed.

        Returns:
            File: The file metadata object of the uploaded file.
        """
        pass

    @abstractmethod
    def download_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
    ) -> Tuple[Iterator[bytes], int]:
        """Download a file.

        Either the latest version will be returned or the specified one.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.

        Raises:
            ResourceNotFoundError: If file does not exist.

        Yields:
            Iterator[bytes]: [description]
        """
        pass

    @abstractmethod
    def delete_file(
        self,
        project_id: str,
        file_key: str,
        version: Optional[str] = None,
        keep_latest_version: bool = False,
    ) -> None:
        """Deletes a file.

        If a specific file `version` is provided, only this one will be deleted. If no `version` is provided and `keep_latest_version` is True, all but the latest version will be deleted. Otherwise, all existing versions will be removed.

        Args:
            project_id (str): Project ID associated with the file.
            file_key (str): Key of the file.
            version (Optional[str], optional): File version. Defaults to None.
            keep_latest_version (bool, optional): [description]. Defaults to False.
        """
        pass

    @abstractmethod
    def delete_files(
        self,
        project_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> None:
        """Delete all files and storage resources related to a project.

        Args:
            project_id (str): Project ID associated with the files.
            date_from (Optional[datetime], optional): The start date to delete the files. If not specified, all files will be deleted.
            date_to (Optional[datetime], optional): The end date to delete the files. If not specified, all files will be deleted.
        """
        pass

    @abstractmethod
    def list_file_actions(
        self, project_id: str, file_key: str, version: Optional[str] = None
    ) -> List[ResourceAction]:
        pass

    @abstractmethod
    def execute_file_action(
        self,
        project_id: str,
        file_key: str,
        action_id: str,
        version: Optional[str] = None,
    ) -> Any:
        pass
