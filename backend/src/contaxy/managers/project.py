from contaxy.operations import JsonDocumentOperations, ProjectOperations
from contaxy.utils.state_utils import GlobalState, RequestState


class ProjectManager(ProjectOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
    ):
        """Initializes the project manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
        """
        self.global_state = global_state
        self.request_state = request_state
        self.json_db_manager = json_db_manager
