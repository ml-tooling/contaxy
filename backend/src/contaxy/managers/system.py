from typing import List, Optional

from contaxy import __version__, config
from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.operations import SystemOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.operations.project import ProjectOperations
from contaxy.schema import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from contaxy.schema.auth import ADMIN_ROLE, USERS_KIND, AccessLevel, UserRegistration
from contaxy.schema.project import ProjectCreation
from contaxy.schema.system import AllowedImageInfo, SystemInfo, SystemStatistics
from contaxy.utils import auth_utils
from contaxy.utils.state_utils import GlobalState, RequestState


class SystemManager(SystemOperations):
    _SYSTEM_INFO_COLLECTION = "system-info"
    _ALLOWED_IMAGES_COLLECTION = "allowed-images"

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
        # Don't execute initialization if there are already existing users
        # TODO: This does not prevent the usage of the contaxy API before the system is initialized
        if len(self._auth_manager.list_users()) > 0:
            raise ResourceAlreadyExistsError("The system has already been initialized")

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

    def check_image(self, image_name: str, image_tag: str) -> None:
        # If allowed image list is empty (default), then allow all images
        if len(self.list_allowed_images()) == 0:
            return
        try:
            allowed_image_info = self.get_allowed_image(image_name)
        except ResourceNotFoundError:
            raise ClientValueError(
                f"Image {image_name} is not on the list of allowed images!"
            )

        if not (
            "*" in allowed_image_info.image_tags
            or image_tag in allowed_image_info.image_tags
        ):
            raise ClientValueError(
                f"Image {image_name} is on the list of allowed images but tag {image_tag} is not allowed!"
            )

    def add_allowed_image(self, allowed_image: AllowedImageInfo) -> AllowedImageInfo:
        allowed_image_doc = self._json_db_manager.create_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._ALLOWED_IMAGES_COLLECTION,
            key=allowed_image.image_name,
            json_document=allowed_image.json(),
            upsert=True,
        )
        return AllowedImageInfo.parse_raw(allowed_image_doc.json_value)

    def list_allowed_images(self) -> List[AllowedImageInfo]:
        allowed_image_docs = self._json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT,
            self._ALLOWED_IMAGES_COLLECTION,
        )
        return [
            AllowedImageInfo.parse_raw(doc.json_value) for doc in allowed_image_docs
        ]

    def get_allowed_image(self, image_name: str) -> AllowedImageInfo:
        allowed_image_doc = self._json_db_manager.get_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._ALLOWED_IMAGES_COLLECTION,
            key=image_name,
        )
        return AllowedImageInfo.parse_raw(allowed_image_doc.json_value)

    def delete_allowed_image(self, image_name: str) -> None:
        self._json_db_manager.delete_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._ALLOWED_IMAGES_COLLECTION,
            key=image_name,
        )
