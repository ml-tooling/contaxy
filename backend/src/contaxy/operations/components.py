from abc import ABC, abstractmethod
from typing import Optional

from contaxy.operations import (
    AuthOperations,
    ExtensionOperations,
    FileOperations,
    JobOperations,
    JsonDocumentOperations,
    ProjectOperations,
    SeedOperations,
    ServiceOperations,
    SystemOperations,
)
from contaxy.schema.extension import CORE_EXTENSION_ID
from contaxy.utils.state_utils import GlobalState, RequestState


class ComponentOperations(ABC):
    @property
    @abstractmethod
    def global_state(self) -> GlobalState:
        pass

    @property
    @abstractmethod
    def request_state(self) -> RequestState:
        pass

    @abstractmethod
    def get_project_manager(self) -> ProjectOperations:
        """Returns a Project Manager instance."""
        pass

    @abstractmethod
    def get_auth_manager(self) -> AuthOperations:
        """Returns an Auth Manager instance."""
        pass

    @abstractmethod
    def get_system_manager(self) -> SystemOperations:
        """Returns a System Manager instance."""
        pass

    @abstractmethod
    def get_extension_manager(self) -> ExtensionOperations:
        """Returns an Extension Manager instance."""
        pass

    @abstractmethod
    def get_json_db_manager(self) -> JsonDocumentOperations:
        """Returns a JSON DB Manager instance."""
        pass

    @abstractmethod
    def get_file_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> FileOperations:
        """Returns a File Manager instance.

        Depending on the provided `extenion_id`, this is either the configured core component
        or an initialized extension client.

        Args:
            extension_id: ID of the requested extension. Use `core` for the platform components.
        """
        pass

    @abstractmethod
    def get_job_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> JobOperations:
        """Returns a Job Manager instance.

        Depending on the provided `extenion_id`, this is either the configured core component
        or an initialized extension client.

        Args:
            extension_id: ID of the requested extension. Use `core` for the platform components.
        """
        pass

    @abstractmethod
    def get_service_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> ServiceOperations:
        """Returns a Service Manager instance.

        Depending on the provided `extenion_id`, this is either the configured core component
        or an initialized extension client.

        Args:
            extension_id: ID of the requested extension. Use `core` for the platform components.
        """
        pass

    @abstractmethod
    def get_seed_manager(self) -> SeedOperations:
        pass
