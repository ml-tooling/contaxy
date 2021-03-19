from typing import List, Optional

from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from contaxy import config
from contaxy.operations import AuthOperations, JsonDocumentOperations
from contaxy.schema import GrantedPermission, TokenType
from contaxy.schema.auth import AccessLevel
from contaxy.utils.state_utils import GlobalState, RequestState

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserPassword(BaseModel):
    hashed_password: str


class ResourcePermissions(BaseModel):
    permissions: List[str]


# TODO: OAuthOperations
class AuthManager(AuthOperations):

    _USER_PASSWORD_COLLECTION = "passwords"
    _PERMISSION_COLLECTION = "permission"

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
        self._global_state = global_state
        self._request_state = request_state
        self._json_db_manager = json_db_manager

    def login_page(self) -> RedirectResponse:
        pass

    def logout_session(self) -> RedirectResponse:
        pass

    def create_token(
        self,
        user_id: str = None,
        scopes: Optional[List[str]] = None,
        token_type: TokenType = TokenType.SESSION_TOKEN,
        description: Optional[str] = None,
    ) -> str:
        pass

    def verify_token(
        self,
        token: str,
        permission: Optional[str] = None,
    ) -> GrantedPermission:
        return GrantedPermission(
            authorized_user="abc", resource_name="abcd", access_level=AccessLevel.WRITE
        )

    def change_password(
        self,
        user_id: str,
        password: str,
    ) -> None:
        user_password = UserPassword(hashed_password=PWD_CONTEXT.hash(password))

        # TODO: salt and hash the user id to make it more complicated to link the password to a user

        # This method creteas or overwrites the
        self._json_db_manager.create_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._USER_PASSWORD_COLLECTION,
            user_id,
            user_password.dict(),
        )

    def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool:

        password_document = self._json_db_manager.get_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._USER_PASSWORD_COLLECTION, user_id
        )

        user_password = UserPassword(**password_document.json_value)
        return PWD_CONTEXT.verify(password, user_password.hashed_password)

    # Permission Operations

    def add_permission(
        self,
        resource_name: str,
        permission: str,
    ) -> None:
        self._json_db_manager.create_json_document(
            config.SYSTEM_INTERNAL_PROJECT,
            self._PERMISSION_COLLECTION,
            resource_name,
            ResourcePermissions(permissions=[permission]).dict(),
        )

    def remove_permission(
        self, resource_name: str, permission: str, apply_as_prefix: bool = False
    ) -> None:
        pass

    def list_permissions(
        self, resource_name: str, resolve_groups: bool = True
    ) -> List[str]:
        # TODO: Support resolve_groups
        # TODO: try catch if document cannot be found
        permission_doc = self._json_db_manager.get_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._PERMISSION_COLLECTION, resource_name
        )

        return ResourcePermissions(**permission_doc.json_value).permissions

    def list_resources_with_permission(
        self, permission: str, resource_name_prefix: Optional[str] = None
    ) -> List[str]:
        pass
