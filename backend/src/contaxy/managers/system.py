from contaxy import __version__
from contaxy.config import settings
from contaxy.operations import SystemOperations
from contaxy.schema.system import SystemInfo, SystemStatistics
from contaxy.utils.state_utils import GlobalState, RequestState


class SystemManager(SystemOperations):
    _SYSTEM_INFO_COLLECTION = "system-info"

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        # json_db_manager: JsonDocumentOperations,
    ):
        """Initializes the system manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
        """
        self._global_state = global_state
        self._request_state = request_state
        # self._json_db_manager = json_db_manager

    def get_system_info(self) -> SystemInfo:
        return SystemInfo(
            version=__version__,
            namespace=settings.SYSTEM_NAMESPACE,
        )

    def is_healthy(self) -> bool:
        # TODO: do real healthchecks
        return True

    def get_system_statistics(self) -> SystemStatistics:
        # TODO: Implement system statistics
        return SystemStatistics(
            project_count=0, user_count=0, job_count=0, service_count=0, file_count=0
        )

    def setup_system(self) -> SystemStatistics:
        # TODO: Implement system statistics
        return SystemStatistics(
            project_count=0, user_count=0, job_count=0, service_count=0, file_count=0
        )
