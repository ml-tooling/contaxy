from typing import List, Optional, Tuple, Union

from contaxy import config
from contaxy.clients import DeploymentManagerClient, FileClient
from contaxy.clients.shared import BaseUrlSession
from contaxy.managers.deployment.manager import DeploymentManager
from contaxy.managers.deployment.utils import (
    Labels,
    get_template_mapping,
    replace_template_string,
)
from contaxy.operations import ExtensionOperations
from contaxy.schema import ExtensibleOperations, Extension, ExtensionInput
from contaxy.schema.deployment import DeploymentType
from contaxy.schema.extension import CORE_EXTENSION_ID
from contaxy.utils.auth_utils import parse_userid_from_resource_name
from contaxy.utils.state_utils import GlobalState, RequestState

COMPOSITE_ID_SEPERATOR = "~"


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


class ExtensionClient(FileClient, DeploymentManagerClient):
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
        global_state: GlobalState,
        request_state: RequestState,
        deployment_manager: DeploymentManager,
    ):
        """Initializes the extension manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            deployment_manager: The current deployment manager instance.
        """
        self.global_state = global_state
        self.request_state = request_state
        self.deployment_manager = deployment_manager

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
        project_services = self.deployment_manager.list_services(
            project_id=project_id, deployment_type=DeploymentType.EXTENSION
        )
        global_services = self.deployment_manager.list_services(
            project_id=f"{config.settings.SYSTEM_NAMESPACE}-global",
            deployment_type=DeploymentType.EXTENSION,
        )

        extension_services = []
        for service in [*project_services, *global_services]:
            # TODO: Add a function to deployment-manager that allows direct filtering
            if service.deployment_type != DeploymentType.EXTENSION.value:
                continue

            extension = Extension(**service.dict())
            # TODO: set extension type
            # extension.extension_type = ""
            if service.metadata:
                endpoint_prefix = f"{config.settings.LAB_BASE_URL}/projects/{project_id}/services/{service.metadata[Labels.DEPLOYMENT_NAME.value]}/access/"
                template_mapping = get_template_mapping(
                    project_id=project_id,
                    user_id=parse_userid_from_resource_name(
                        self.request_state.authorized_subject
                    ),
                )
                if (
                    f"{config.settings.SYSTEM_NAMESPACE}.ui_extension_endpoint"
                    in service.metadata
                ):
                    service_ui_extension_endpoint = replace_template_string(
                        input=service.metadata[
                            f"{config.settings.SYSTEM_NAMESPACE}.ui_extension_endpoint"
                        ],
                        templates_mapping=template_mapping,
                    )
                    extension.ui_extension_endpoint = (
                        f"{endpoint_prefix}{service_ui_extension_endpoint}"
                    )

                if (
                    f"{config.settings.SYSTEM_NAMESPACE}.api_extension_endpoints"
                    in service.metadata
                ):
                    service_api_extension_endpoint = replace_template_string(
                        input=service.metadata[
                            f"{config.settings.SYSTEM_NAMESPACE}.api_extension_endpoints"
                        ],
                        templates_mapping=template_mapping,
                    )
                    extension.api_extension_endpoint = (
                        f"{endpoint_prefix}{service_api_extension_endpoint}"
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
        raise NotImplementedError

    def suggest_extension_config(
        self, container_image: str, project_id: str
    ) -> ExtensionInput:
        raise NotImplementedError
