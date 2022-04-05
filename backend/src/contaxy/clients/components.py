from typing import Optional

from requests import Session
from starlette.datastructures import State

from contaxy.clients import (
    AuthClient,
    DeploymentClient,
    ExtensionClient,
    FileClient,
    JsonDocumentClient,
    ProjectClient,
    SystemClient,
)
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
from contaxy.operations.components import ComponentOperations
from contaxy.schema.extension import CORE_EXTENSION_ID
from contaxy.utils.state_utils import GlobalState, RequestState


class ComponentClient(ComponentOperations):
    def __init__(self, session: Session):
        self.session = session

    @property
    def global_state(self) -> GlobalState:
        return GlobalState(State())

    @property
    def request_state(self) -> RequestState:
        return RequestState(State())

    def get_project_manager(self) -> ProjectOperations:
        return ProjectClient(self.session)

    def get_auth_manager(self) -> AuthOperations:
        return AuthClient(self.session)

    def get_system_manager(self) -> SystemOperations:
        return SystemClient(self.session)

    def get_extension_manager(self) -> ExtensionOperations:
        return ExtensionClient(self.session)

    def get_json_db_manager(self) -> JsonDocumentOperations:
        return JsonDocumentClient(self.session)

    def get_file_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> FileOperations:
        return FileClient(self.session)

    def get_service_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> ServiceOperations:
        return DeploymentClient(self.session)

    def get_job_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> JobOperations:
        return DeploymentClient(self.session)

    def get_seed_manager(self) -> SeedOperations:
        raise NotImplementedError
