from typing import List, Optional

from contaxy import __version__, config
from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.operations import (
    FileOperations,
    JobOperations,
    ServiceOperations,
    SystemOperations,
)
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.operations.project import ProjectOperations
from contaxy.schema import File, Job, Service
from contaxy.schema.auth import (
    ADMIN_ROLE,
    USERS_KIND,
    AccessLevel,
    User,
    UserRegistration,
)
from contaxy.schema.project import Project, ProjectCreation
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
        service_manager: ServiceOperations,
        job_manager: JobOperations,
        file_manager: FileOperations,
    ):
        """Initializes the system manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: Json document manager instance.
            auth_manager: Auth manager instance.
            project_manager: Project manager instance.
            service_manager: Service manager instance.
            job_manager: Job manager instance.
            file_manager: File manager instance.
        """
        self._global_state = global_state
        self._request_state = request_state
        self._auth_manager = auth_manager
        self._project_manager = project_manager
        self._json_db_manager = json_db_manager
        self._service_manager = service_manager
        self._job_manager = job_manager
        self._file_manager = file_manager

    def get_system_info(self) -> SystemInfo:
        return SystemInfo(
            version=__version__,
            namespace=settings.SYSTEM_NAMESPACE,
        )

    def is_healthy(self) -> bool:
        # TODO: do real healthchecks
        return True

    def get_system_statistics(self, include_technical: bool) -> SystemStatistics:
        projects = self._list_all_projects(include_technical)
        users = self._list_all_users(include_technical)
        jobs = self._list_all_jobs(projects)
        services = self._list_all_services(projects)
        files = self._list_all_files(projects)
        return SystemStatistics(
            project_count=len(jobs),
            user_count=len(users),
            job_count=len(jobs),
            service_count=len(services),
            file_count=len(files),
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

        auth_utils.create_user_project(admin_user, self._project_manager)

    def _list_all_projects(self, include_technical: bool) -> List[Project]:
        # Temporarily set authorized_access to None so that list_projects returns all projects
        # TODO: Find better solution to get all projects
        temp = self._request_state.authorized_access
        self._request_state.authorized_access = None
        projects = self._project_manager.list_projects()
        self._request_state.authorized_access = temp

        if not include_technical:
            projects = [proj for proj in projects if not proj.technical_project]
        return projects

    def _list_all_users(self, include_technical: bool) -> List[User]:
        users = self._auth_manager.list_users()
        if not include_technical:
            users = [user for user in users if not user.technical_user]
        return users

    def _list_all_jobs(self, projects: List[Project]) -> List[Job]:
        return [
            job
            for project in projects
            if project.id
            for job in self._job_manager.list_jobs(project.id)
        ]

    def _list_all_services(self, projects: List[Project]) -> List[Service]:
        return [
            service
            for project in projects
            if project.id
            for service in self._service_manager.list_services(project.id)
        ]

    def _list_all_files(self, projects: List[Project]) -> List[File]:
        return [
            file
            for project in projects
            if project.id
            for file in self._file_manager.list_files(project.id)
        ]
