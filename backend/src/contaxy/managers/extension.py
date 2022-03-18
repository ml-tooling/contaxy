from typing import List, Optional, Tuple, Union

from contaxy import config
from contaxy.clients import DeploymentClient, FileClient
from contaxy.clients.shared import BaseUrlSession
from contaxy.managers.deployment.utils import (
    Labels,
    get_template_mapping,
    replace_template_string,
)
from contaxy.operations import ExtensionOperations, ServiceOperations
from contaxy.operations.components import ComponentOperations
from contaxy.schema import ExtensibleOperations, Extension, ExtensionInput, Service
from contaxy.schema.deployment import DeploymentType, ServiceInput
from contaxy.schema.extension import (
    CORE_EXTENSION_ID,
    GLOBAL_EXTENSION_PROJECT,
    ExtensionType,
)
from contaxy.utils.auth_utils import parse_userid_from_resource_name

COMPOSITE_ID_SEPERATOR = "~"

CAPABILITIES_METADATA_SEPARATOR = ","
METADATA_UI_EXTENSION_ENDPOINT = "ctxy.ui_extension_endpoint"
METADATA_API_EXTENSION_ENDPOINT = "ctxy.api_extension_endpoint"
METADATA_CAPABILITIES = "ctxy.capabilities"
METADATA_EXTENSION_TYPE = "ctxy.extensionType"


def parse_composite_id(composite_id: str) -> Tuple[str, Union[str, None]]:
    """Extracts the resource and extension ID from an composite ID.

    If the provided ID does not contain an composite ID seperator (`~`)
    the ID will be returned as resource ID and the extension ID will be `None`.

    Args:
        composite_id (str): The ID to parse.

    Returns:
        Tuple[str, str]: Resource ID, Extension ID
    """
    # TODO: Only sperate based on the first occurance

    if COMPOSITE_ID_SEPERATOR not in composite_id:
        # The provided id does not contain an extension ID prefix
        return composite_id, None

    resource_id, extension_id = composite_id.split(COMPOSITE_ID_SEPERATOR, 1)
    return resource_id, extension_id


def map_service_to_extension(service: Service, user_id: str) -> Extension:
    extension = Extension(**service.dict())

    if service.metadata:
        project_id = service.metadata[Labels.PROJECT_NAME.value]
        deployment_id = service.id
        endpoint_prefix = f"{config.settings.CONTAXY_BASE_URL}/projects/{project_id}/services/{deployment_id}/access/"

        if METADATA_CAPABILITIES in service.metadata:
            extension.capabilities = service.metadata[METADATA_CAPABILITIES].split(
                CAPABILITIES_METADATA_SEPARATOR
            )

        template_mapping = get_template_mapping(
            project_id=project_id,
            user_id=parse_userid_from_resource_name(user_id),
        )

        if METADATA_UI_EXTENSION_ENDPOINT in service.metadata:
            service_ui_extension_endpoint = replace_template_string(
                input=service.metadata[METADATA_UI_EXTENSION_ENDPOINT],
                templates_mapping=template_mapping,
            )
            extension.ui_extension_endpoint = (
                f"{endpoint_prefix}{service_ui_extension_endpoint}"
            )

        if METADATA_API_EXTENSION_ENDPOINT in service.metadata:
            service_api_extension_endpoint = replace_template_string(
                input=service.metadata[METADATA_API_EXTENSION_ENDPOINT],
                templates_mapping=template_mapping,
            )
            extension.api_extension_endpoint = (
                f"{endpoint_prefix}{service_api_extension_endpoint}"
            )

        if METADATA_EXTENSION_TYPE in service.metadata:
            try:
                extension.extension_type = ExtensionType(
                    service.metadata[METADATA_EXTENSION_TYPE]
                )
            except ValueError:
                pass

    return extension


class ExtensionClient(FileClient, DeploymentClient):
    """Handels the request forwarding to the installed extensions.

    The extension client implements all extensible manager interfaces
    and uses the generated HTTP client to forward requests to the respective extension.

    Extension clients are initialized and managed by the `ExtensionManager`.
    """

    def __init__(self, endpoint_url: str, access_token: Optional[str] = None):
        """Initializes the extension client.

        Args:
            endpoint_url: The endpoint base URL of the extension.
            access_token: An access token that is attached to all requests.
        """
        client_session = BaseUrlSession(base_url=endpoint_url)
        if access_token:
            client_session.headers.update({config.API_TOKEN_NAME: access_token})
            # client_session.cookies.set(config.API_TOKEN_NAME, access_token)
        super(ExtensionClient, self).__init__(client=client_session)


class ExtensionManager(ExtensionOperations):
    """Installs and manages extensions.

    The extension manager implements all methods for the full extension lifecycle.
    It is the central entry point for all interactions with extensions.
    """

    def __init__(
        self,
        component_manager: ComponentOperations,
    ):
        """Initializes the extension manager.

        Args:
            component_manager: Instance of the component manager that grants access to the other managers.
        """
        self.global_state = component_manager.global_state
        self.request_state = component_manager.request_state
        self._component_manager = component_manager

    @property
    def _service_manager(self) -> ServiceOperations:
        return self._component_manager.get_service_manager()

    def get_extension_client(self, extension_id: str) -> ExtensionClient:
        endpoint_url = f"http://{config.settings.SYSTEM_NAMESPACE}-{extension_id}:8080"
        access_token = (
            self.request_state.authorized_access.access_token.token
            if self.request_state.authorized_access
            and self.request_state.authorized_access.access_token
            else ""
        )
        return ExtensionClient(
            endpoint_url=endpoint_url,
            access_token=access_token,
        )

    def list_extensions(self, project_id: str) -> List[Extension]:
        if project_id != GLOBAL_EXTENSION_PROJECT:
            project_services = self._service_manager.list_services(
                project_id=project_id, deployment_type=DeploymentType.EXTENSION
            )
        else:
            project_services = []
        global_services = self._service_manager.list_services(
            project_id=GLOBAL_EXTENSION_PROJECT,
            deployment_type=DeploymentType.EXTENSION,
        )

        extension_services = []
        for service in [*project_services, *global_services]:
            # TODO: Add a function to deployment-manager that allows direct filtering
            if service.deployment_type != DeploymentType.EXTENSION.value:
                continue

            extension = map_service_to_extension(
                service=service,
                user_id=self.request_state.authorized_subject,
            )
            extension_services.append(extension)

        return extension_services

    def get_default_extension(self, operation: ExtensibleOperations) -> str:
        return CORE_EXTENSION_ID

    def delete_extension(
        self, project_id: str, extension_id: Optional[str] = None
    ) -> None:
        raise NotImplementedError

    def get_extension_metadata(self, project_id: str, extension_id: str) -> Extension:
        raise NotImplementedError

    def install_extension(
        self, extension: ExtensionInput, project_id: str
    ) -> Extension:
        service_input = ServiceInput(**extension.dict())
        if not service_input.metadata:
            service_input.metadata = {}
        if extension.capabilities:
            service_input.metadata[
                METADATA_CAPABILITIES
            ] = CAPABILITIES_METADATA_SEPARATOR.join(extension.capabilities)
        if extension.ui_extension_endpoint:
            service_input.metadata[
                METADATA_UI_EXTENSION_ENDPOINT
            ] = extension.ui_extension_endpoint
        if extension.api_extension_endpoint:
            service_input.metadata[
                METADATA_API_EXTENSION_ENDPOINT
            ] = extension.api_extension_endpoint
        if extension.extension_type:
            service_input.metadata[METADATA_EXTENSION_TYPE] = extension.extension_type

        service = self._service_manager.deploy_service(
            project_id=project_id,
            service_input=service_input,
            deployment_type=DeploymentType.EXTENSION,
        )
        return map_service_to_extension(
            service=service,
            user_id=self.request_state.authorized_subject,
        )

    def suggest_extension_config(
        self, container_image: str, project_id: str
    ) -> ExtensionInput:
        raise NotImplementedError
