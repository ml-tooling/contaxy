from typing import Tuple, Union

from contaxy.operations import ExtensionOperations
from contaxy.operations.deployment import DeploymentOperations
from contaxy.operations.file import FileOperations
from contaxy.schema import ExtensibleOperations
from contaxy.schema.extension import CORE_EXTENSION_ID
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


class ExtensionClient(FileOperations, DeploymentOperations):
    """Handels the request forwarding to the installed extensions.

    The extension client implements all extensible manager interfaces
    and uses the generated HTTP client to forward requests to the respective extension.

    Extension clients are initialized and managed by the `ExtensionManager`.
    """

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the extension client.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self._global_state = global_state
        self._request_state = request_state
        # TODO: Initialize Extension Client correctly


class ExtensionManager(ExtensionOperations):
    """Installs and manages extensions.

    The extension manager implements all methods for the full extension lifecycle.
    It is the central entry point for all interactions with extensions.
    """

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the extension manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self.global_state = global_state
        self.request_state = request_state

    def get_extension_client(self, extension_id: str) -> ExtensionClient:
        pass

    def get_default_extension(self, operation: ExtensibleOperations) -> str:
        return CORE_EXTENSION_ID
