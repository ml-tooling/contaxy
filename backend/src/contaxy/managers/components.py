from typing import Optional

from fastapi import FastAPI, Request
from loguru import logger
from pydantic.networks import PostgresDsn
from starlette.datastructures import State

from contaxy import config
from contaxy.managers.auth import AuthManager
from contaxy.managers.deployment.manager import DeploymentManager
from contaxy.managers.extension import ExtensionManager
from contaxy.managers.project import ProjectManager
from contaxy.managers.seed import SeedManager
from contaxy.managers.system import SystemManager
from contaxy.operations import (
    FileOperations,
    JobOperations,
    JsonDocumentOperations,
    SeedOperations,
    ServiceOperations,
)
from contaxy.operations.components import ComponentOperations
from contaxy.operations.deployment import DeploymentOperations
from contaxy.schema.auth import AccessLevel, AuthorizedAccess
from contaxy.schema.deployment import ServiceInput
from contaxy.schema.extension import CORE_EXTENSION_ID
from contaxy.utils import auth_utils
from contaxy.utils.state_utils import GlobalState, RequestState


class ComponentManager(ComponentOperations):
    """Initializes and manages all platform components.

    The component manager is created for every request
    and will initialize all platform components based on the platform settings.
    It is the central point to access any other platform component.

    Individual components can store a global state via the `global_state` variable.
    This allows initializing certain objects (DB connections, HTTP clients, ...)
    only once per app instance (process) and share it with other components.

    There is also a `request_state` that can be used to share objects
    for a single request.
    """

    @classmethod
    def from_request(cls, request: Request) -> "ComponentManager":
        return cls(
            GlobalState(request.app.state),
            RequestState(request.state),
        )

    @classmethod
    def from_app(cls, app: FastAPI) -> "ComponentManager":
        return cls(
            GlobalState(app.state),
            RequestState(State()),
        )

    def __init__(self, global_state: GlobalState, request_state: RequestState):
        """Initializes the component manager.

        Args:
            global_state: Global application state.
            request_state: Request scoped state.
        """

        # Individual components can store global state via the `global_state` variable
        self._global_state = global_state
        self._request_state = request_state

        # Initialized variables which will be lazyloaded
        self._auth_manager: Optional[AuthManager] = None
        self._extension_manager: Optional[ExtensionManager] = None
        self._project_manager: Optional[ProjectManager] = None
        self._system_manager: Optional[SystemManager] = None
        # Extensible managers: typed by its interface
        self._json_db_manager: Optional[JsonDocumentOperations] = None
        self._deployment_manager: Optional[DeploymentOperations] = None
        self._file_manager: Optional[FileOperations] = None

        # Debug Manager
        self._seed_manager: Optional[SeedOperations] = None

    # Allow component manger to be used as context manager
    def __enter__(self) -> "ComponentManager":
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self.close()

    def close(self) -> None:
        """Closes the component manager.

        This is called once the request is finished
        and will close the `request_state` and all its registered close callbacks.
        """
        self.request_state.close()
        del self._request_state

    @property
    def global_state(self) -> GlobalState:
        return self._global_state

    @property
    def request_state(self) -> RequestState:
        return self._request_state

    def verify_access(
        self,
        token: str,
        resource_name: Optional[str] = None,
        access_level: Optional[AccessLevel] = None,
    ) -> AuthorizedAccess:
        """Verifies if the authorized token is valid and grants access to the specified resource.

        The token is verfied for its validity and - if provided - if it has the specified permission.

        Args:
            token: Token (session or API) to verify.
            resource_name (optional): The access verification will check if the authroized subject is granted access to this resource.
                If `None`, only the token will be checked for validity.
            access_level (optional): The access verification will check if the authroized subject is allowed to access the resource at this level.
                The access level has to be provided if the resource_name is used.

        Raises:
            PermissionDeniedError: If the requested permission is denied.
            UnauthenticatedError: If the token is invalid or expired.

        Returns:
            AuthorizedAccess: Information about the granted permission, authenticated user, and the token.
        """

        # TODO: dynamic access level check: If `None`, the highest access level that the subject is granted for the given resource will be determined.

        permission = None
        if resource_name:
            # Only check for permission if resource name is provided
            # The access level should be provided
            assert access_level is not None
            processed_resource_name = (
                resource_name.rstrip("/").rstrip(":").lstrip("/").lstrip(":")
            )
            permission = (
                processed_resource_name
                + auth_utils.PERMISSION_SEPERATOR
                + access_level.value
            )
        authorized_access = self.get_auth_manager().verify_access(token, permission)
        # Set the authroized access into the request state
        self.request_state.authorized_access = authorized_access
        return authorized_access

    def get_project_manager(self) -> ProjectManager:
        """Returns a Project Manager instance."""
        if not self._project_manager:
            self._project_manager = ProjectManager(self)

        assert self._project_manager is not None
        return self._project_manager

    def get_auth_manager(self) -> AuthManager:
        """Returns an Auth Manager instance."""
        if not self._auth_manager:
            self._auth_manager = AuthManager(self)
        assert self._auth_manager is not None
        return self._auth_manager

    def get_system_manager(self) -> SystemManager:
        """Returns a System Manager instance."""
        if not self._system_manager:
            self._system_manager = SystemManager(self)

        assert self._system_manager is not None
        return self._system_manager

    def get_extension_manager(self) -> ExtensionManager:
        """Returns an Extension Manager instance."""
        if not self._extension_manager:
            self._extension_manager = ExtensionManager(self)
        return self._extension_manager

    def get_json_db_manager(self) -> JsonDocumentOperations:
        """Returns a JSON DB Manager instance."""
        if not self._json_db_manager:
            from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager

            self._json_db_manager = PostgresJsonDocumentManager(
                self.global_state, self.request_state
            )
        return self._json_db_manager

    def get_file_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> FileOperations:
        """Returns a File Manager instance.

        Depending on the provided `extenion_id`, this is either the configured core component
        or an initialized extension client.

        Args:
            extension_id: ID of the requested extension. Use `core` for the platform components.
        """

        if extension_id is not None and extension_id != CORE_EXTENSION_ID:
            # Request is forwarded to extension
            return self.get_extension_manager().get_extension_client(extension_id)

        if not self._file_manager:
            self._file_manager = self._create_file_manager()
        return self._file_manager

    def _create_file_manager(self) -> FileOperations:
        if self.global_state.settings.S3_ENDPOINT:
            logger.debug("Configuration S3_ENDPOINT set. Using external S3 storage.")
            from contaxy.managers.file.minio import MinioFileManager

            return MinioFileManager(self)
        elif self.global_state.settings.AZURE_BLOB_CONNECTION_STRING:
            logger.debug(
                "Configuration AZURE_BLOB_CONNECTION_STRING set. Using external Azure Blob storage."
            )
            from contaxy.managers.file.azure_blob import AzureBlobFileManager

            return AzureBlobFileManager(self)
        else:
            logger.debug(
                "No external object storage configured. Using internal Minio service."
            )
            raise NotImplementedError(
                "Internal Minio object storage is not implemented! Please configure S3_ENDPOINT or AZURE_BLOB_CONNECTION_STRING."
            )

    def _get_deployment_manager(self) -> DeploymentOperations:
        # Lazyload deployment manager
        if not self._deployment_manager:
            if (
                self.global_state.settings.DEPLOYMENT_MANAGER
                == config.DeploymentManager.DOCKER
            ):
                from contaxy.managers.deployment.docker import DockerDeploymentPlatform

                # Add DB persistence to docker deployment manager
                self._deployment_manager = DeploymentManager(
                    DockerDeploymentPlatform(), self
                )
            elif (
                self.global_state.settings.DEPLOYMENT_MANAGER
                == config.DeploymentManager.KUBERNETES
            ):
                from contaxy.managers.deployment.kubernetes import (
                    KubernetesDeploymentPlatform,
                )

                # Add DB persistence to kubernetes deployment manager
                self._deployment_manager = DeploymentManager(
                    KubernetesDeploymentPlatform(), self
                )

        assert self._deployment_manager is not None
        return self._deployment_manager

    def get_job_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> JobOperations:
        """Returns a Job Manager instance.

        Depending on the provided `extenion_id`, this is either the configured core component
        or an initialized extension client.

        Args:
            extension_id: ID of the requested extension. Use `core` for the platform components.
        """
        if extension_id is not None and extension_id != CORE_EXTENSION_ID:
            # Request is forwarded to extension
            return self.get_extension_manager().get_extension_client(extension_id)

        return self._get_deployment_manager()

    def get_service_manager(
        self, extension_id: Optional[str] = CORE_EXTENSION_ID
    ) -> ServiceOperations:
        """Returns a Service Manager instance.

        Depending on the provided `extenion_id`, this is either the configured core component
        or an initialized extension client.

        Args:
            extension_id: ID of the requested extension. Use `core` for the platform components.
        """
        if extension_id is not None and extension_id != CORE_EXTENSION_ID:
            # Request is forwarded to extension
            return self.get_extension_manager().get_extension_client(extension_id)

        return self._get_deployment_manager()

    def get_seed_manager(self) -> SeedOperations:
        if not self._seed_manager:
            self._seed_manager = SeedManager(self)
        return self._seed_manager


def install_components() -> None:
    """Currently only a mock implementation."""

    # create a mocked request for initializing the component manager
    import addict

    mocked_request = addict.Dict()
    # Load and add platform settings to
    global_state = GlobalState(mocked_request.app.state)  # type: ignore
    global_state.settings = config.settings

    # Initialize component manager
    component_manager = ComponentManager(mocked_request)  # type: ignore

    if not global_state.settings.POSTGRES_CONNECTION_URI:
        # Deploy postgres service in system project
        # Set database to use the system namespace
        POSTGRES_DB = global_state.settings.SYSTEM_NAMESPACE
        POSTGRES_PORT = "5432"
        # TODO: Generate credentials?
        POSTGRES_USER = "admin"
        POSTGRES_PASSWORD = "admin"

        service = component_manager.get_service_manager().deploy_service(
            config.SYSTEM_INTERNAL_PROJECT,
            ServiceInput(
                display_name="postgres",
                container_image="postgres",
                endpoints=[POSTGRES_PORT],
                parameters={
                    "POSTGRES_USER": POSTGRES_USER,
                    "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
                    "POSTGRES_DB": POSTGRES_DB,
                },
            ),
        )

        global_state.settings.POSTGRES_CONNECTION_URI = PostgresDsn(
            f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{service.id}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

    # TODO: Do other configurations

    # Close states
    component_manager.close()
    global_state.close()
