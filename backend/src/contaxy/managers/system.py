from typing import Optional

from contaxy import __version__, config
from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.operations import SystemOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.operations.project import ProjectOperations
from contaxy.schema.auth import ADMIN_ROLE, USERS_KIND, AccessLevel, UserRegistration
from contaxy.schema.project import ProjectCreation
from contaxy.schema.system import SystemInfo, SystemStatistics
from contaxy.utils import auth_utils
from contaxy.utils.state_utils import GlobalState, RequestState


class SystemManager(SystemOperations):
    _SYSTEM_INFO_COLLECTION = "system-info"

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
        auth_manager: AuthManager,
        project_manager: ProjectOperations,
    ):
        """Initializes the system manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: Json document manager instance.
            auth_manager: Auth manager instance.
            project_manager: Project manager instance.
        """
        self._global_state = global_state
        self._request_state = request_state
        self._auth_manager = auth_manager
        self._project_manager = project_manager
        self._json_db_manager = json_db_manager

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

    def initialize_system(
        self,
        password: Optional[str] = None,
    ) -> None:
        # Remove authorized access info
        self._request_state.authorized_access = None

        # TODO: do not clean up?
        # Clean up all documents
        for project in self._project_manager.list_projects():
            assert project.id is not None
            self._json_db_manager.delete_json_collections(project.id)

        # Create Admin Role
        self._auth_manager.add_permission(
            ADMIN_ROLE,
            auth_utils.construct_permission("*", AccessLevel.ADMIN),
        )

        # Create Admin User
        # Set initial user password -> SHOULD be changed after the first login
        admin_user = self._auth_manager.create_user(
            UserRegistration(
                username=config.SYSTEM_ADMIN_USERNAME,
                password=password or config.SYSTEM_ADMIN_INITIAL_PASSWORD,  # type: ignore
            ),
            technical_user=True,
        )

        # Add admin role to admin user
        # TODO: use resource name
        admin_user_resource_name = USERS_KIND + "/" + admin_user.id
        self._auth_manager.add_permission(
            admin_user_resource_name,
            ADMIN_ROLE,
        )

        # Create System Internal Project
        self._project_manager.create_project(
            ProjectCreation(
                id=config.SYSTEM_INTERNAL_PROJECT,
                display_name=config.SYSTEM_INTERNAL_PROJECT,
                description="This project holds all system internal services and data.",
            ),
            technical_project=True,
        )

        auth_utils.setup_user(admin_user, self._project_manager)
