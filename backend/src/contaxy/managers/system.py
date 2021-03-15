from contaxy.operations import SystemOperations
from contaxy.utils import id_utils
from contaxy.utils.state_utils import GlobalState, RequestState

MAX_SYSTEM_NAMESPACE_LENGTH = 5


def get_system_namespace(system_name: str) -> str:
    return id_utils.generate_readable_id(
        system_name,
        max_length=MAX_SYSTEM_NAMESPACE_LENGTH,
        min_length=3,
        max_hash_suffix_length=MAX_SYSTEM_NAMESPACE_LENGTH,
        separator="",
    )


class SystemManager(SystemOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the system manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self.global_state = global_state
        self.request_state = request_state
