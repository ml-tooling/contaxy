from typing import Optional

from contaxy.operations import AuthOperations, JsonDocumentOperations, OAuthOperations
from contaxy.schema import GrantedPermission
from contaxy.schema.auth import AccessLevel
from contaxy.utils.state_utils import GlobalState, RequestState


class AuthManager(AuthOperations, OAuthOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
    ):
        """Initializes the Auth Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
        """
        self.global_state = global_state
        self.request_state = request_state
        self.json_db_manager = json_db_manager

    def verify_token(
        self,
        token: str,
        permission: Optional[str] = None,
    ) -> GrantedPermission:
        # TODO: implement
        return GrantedPermission(
            authorized_user="abc", resource_name="abcd", access_level=AccessLevel.WRITE
        )
