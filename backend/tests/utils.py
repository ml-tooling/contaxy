"""Shared Testing Utilities."""
from typing import Optional, Union

from contaxy.managers.auth import AuthManager
from contaxy.managers.extension import ExtensionManager
from contaxy.managers.project import ProjectManager
from contaxy.managers.system import SystemManager
from contaxy.operations import (
    FileOperations,
    JobOperations,
    JsonDocumentOperations,
    SeedOperations,
    ServiceOperations,
)
from contaxy.operations.components import ComponentOperations
from contaxy.utils.state_utils import GlobalState, RequestState


class ComponentManagerMock(ComponentOperations):
    def __init__(
        self,
        global_state: Optional[GlobalState] = None,
        request_state: Optional[RequestState] = None,
        project_manager: Optional[ProjectManager] = None,
        auth_manager: Optional[AuthManager] = None,
        system_manager: Optional[SystemManager] = None,
        extension_manager: Optional[ExtensionManager] = None,
        json_db_manager: Optional[JsonDocumentOperations] = None,
        file_manager: Optional[FileOperations] = None,
        deployment_manager: Optional[Union[JobOperations, ServiceOperations]] = None,
        seed_manager: Optional[SeedOperations] = None,
    ):
        self._global_state = global_state
        self._request_state = request_state
        self.project_manager = project_manager
        self.auth_manager = auth_manager
        self.system_manager = system_manager
        self.extension_manager = extension_manager
        self.json_db_manager = json_db_manager
        self.file_manager = file_manager
        self.deployment_manager = deployment_manager
        self.seed_manager = seed_manager

    @property
    def global_state(self) -> GlobalState:
        return self._global_state

    @property
    def request_state(self) -> RequestState:
        return self._request_state

    def get_project_manager(self) -> ProjectManager:
        return self.project_manager

    def get_auth_manager(self) -> AuthManager:
        return self.auth_manager

    def get_system_manager(self) -> SystemManager:
        return self.system_manager

    def get_extension_manager(self) -> ExtensionManager:
        return self.extension_manager

    def get_json_db_manager(self) -> JsonDocumentOperations:
        return self.json_db_manager

    def get_file_manager(self) -> FileOperations:
        return self.file_manager

    def get_job_manager(self) -> JobOperations:
        return self.deployment_manager

    def get_service_manager(self) -> ServiceOperations:
        return self.deployment_manager

    def get_seed_manager(self) -> SeedOperations:
        return self.seed_manager
