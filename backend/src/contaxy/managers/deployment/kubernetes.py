from contaxy.operations import DeploymentOperations
from contaxy.utils.state_utils import GlobalState, RequestState


class KubernetesDeploymentManager(DeploymentOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the Kubernetes Deployment Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self.global_state = global_state
        self.request_state = request_state
