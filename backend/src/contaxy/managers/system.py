import json
from typing import Any, List, Optional

from loguru import logger

from contaxy import __version__, config
from contaxy.config import settings
from contaxy.operations import AuthOperations, SystemOperations
from contaxy.operations.components import ComponentOperations
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.operations.project import ProjectOperations
from contaxy.schema import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from contaxy.schema.auth import (
    ADMIN_ROLE,
    USER_ROLE,
    USERS_KIND,
    AccessLevel,
    UserRegistration,
)
from contaxy.schema.extension import GLOBAL_EXTENSION_PROJECT
from contaxy.schema.project import PROJECTS_KIND, ProjectCreation
from contaxy.schema.system import (
    AllowedImageInfo,
    SystemInfo,
    SystemState,
    SystemStatistics,
)
from contaxy.utils import auth_utils


class SystemManager(SystemOperations):
    _ALLOWED_IMAGES_COLLECTION = "allowed-images"

    _SYSTEM_PROPERTIES_COLLECTION = "system-properties"
    _SYSTEM_PROPERTY_IS_INITIALIZED = "is-initialized"

    def __init__(
        self,
        component_manager: ComponentOperations,
    ):
        """Initializes the system manager.

        Args:
            component_manager: Instance of the component manager that grants access to the other managers.
        """
        self._global_state = component_manager.global_state
        self._request_state = component_manager.request_state
        self._component_manager = component_manager

    @property
    def _json_db_manager(self) -> JsonDocumentOperations:
        return self._component_manager.get_json_db_manager()

    @property
    def _auth_manager(self) -> AuthOperations:
        return self._component_manager.get_auth_manager()

    @property
    def _project_manager(self) -> ProjectOperations:
        return self._component_manager.get_project_manager()

    def get_system_info(self) -> SystemInfo:
        if self._is_initialized():
            system_state = SystemState.RUNNING
        else:
            system_state = SystemState.UNINITIALIZED
        return SystemInfo(
            version=__version__,
            namespace=settings.SYSTEM_NAMESPACE,
            system_state=system_state,
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
        # Only allow initialization once
        if self._is_initialized():
            raise ResourceAlreadyExistsError("The system has already been initialized")
        logger.debug("Started system initialization.")

        # Remove authorized access info
        self._request_state.authorized_access = None

        # Create System Internal Project
        logger.debug("System initialization: Create system project.")
        self._project_manager.create_project(
            ProjectCreation(
                id=config.SYSTEM_INTERNAL_PROJECT,
                display_name=config.SYSTEM_INTERNAL_PROJECT,
                description="This project holds all system internal services and data.",
            ),
            technical_project=True,
        )

        # Create admin role
        logger.debug("System initialization: Creating admin role.")
        self._auth_manager.add_permission(
            ADMIN_ROLE,
            auth_utils.construct_permission("*", AccessLevel.ADMIN),
        )

        # Create user role
        logger.debug("System initialization: Creating user role.")
        # Users needs to know which images are allowed for deployments
        self._auth_manager.add_permission(
            USER_ROLE,
            auth_utils.construct_permission("system/allowed-images", AccessLevel.READ),
        )
        # Users requires read access to the global extension project to access the extension endpoints
        self._auth_manager.add_permission(
            USER_ROLE,
            auth_utils.construct_permission(
                f"{PROJECTS_KIND}/{GLOBAL_EXTENSION_PROJECT}", AccessLevel.READ
            ),
        )

        # Create Admin User
        logger.debug("System initialization: Creating default admin user.")
        # Set initial user password -> SHOULD be changed after the first login
        admin_user = auth_utils.create_and_setup_user(
            user_input=UserRegistration(
                username=config.SYSTEM_ADMIN_USERNAME,
                password=password or config.SYSTEM_ADMIN_INITIAL_PASSWORD,  # type: ignore
            ),
            technical_user=True,
            auth_manager=self._auth_manager,
            project_manager=self._project_manager,
        )
        # Add admin role to admin user
        # TODO: use resource name
        admin_user_resource_name = USERS_KIND + "/" + admin_user.id
        self._auth_manager.add_permission(
            admin_user_resource_name,
            ADMIN_ROLE,
        )

        self._set_system_property(SystemManager._SYSTEM_PROPERTY_IS_INITIALIZED, True)

    def check_allowed_image(self, image_name: str, image_tag: str) -> None:
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

    _is_initialized_cache = False

    def _is_initialized(self) -> bool:
        # After the initialization was successful, is_initialized cannot be set back to false, so caching it is safe
        if not SystemManager._is_initialized_cache:
            # Cache says that system is not initialized. Check if that is correct.
            SystemManager._is_initialized_cache = self._get_system_property(
                self._SYSTEM_PROPERTY_IS_INITIALIZED, default=False
            )
        return SystemManager._is_initialized_cache

    def _get_system_property(self, property_name: str, default: Any = ...) -> Any:
        """Returns the value of the system property.

        Args:
            property_name (str): Name of the system property that should be retrieved
            default (None): Default value to return if property is not set. If not set, ResourceNotFoundError will be raised instead.

        Raises:
            ResourceNotFoundError: If no system property with the given name is found

        Returns:
            The value of the system property
        """
        try:
            system_property_doc = self._json_db_manager.get_json_document(
                config.SYSTEM_INTERNAL_PROJECT,
                self._SYSTEM_PROPERTIES_COLLECTION,
                key=property_name,
            )
        except ResourceNotFoundError as e:
            if default is ...:
                raise e
            else:
                return default
        is_initialized = json.loads(system_property_doc.json_value)
        return is_initialized

    def _set_system_property(self, property_name: str, property_value: Any) -> None:
        """Sets the specified value for the given system property.

        Args:
            property_name (str): The name of the property to set
            property_value (Any): The new value of the property
        """
        self._json_db_manager.create_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._SYSTEM_PROPERTIES_COLLECTION,
            key=property_name,
            json_document=json.dumps(property_value),
            upsert=True,
        )
