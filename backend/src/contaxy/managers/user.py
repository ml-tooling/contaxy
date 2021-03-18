from datetime import datetime
from typing import List

from contaxy import config
from contaxy.operations import JsonDocumentOperations, UserOperations
from contaxy.schema import User, UserInput
from contaxy.utils import id_utils
from contaxy.utils.state_utils import GlobalState, RequestState


class UserManager(UserOperations):
    _COLLECTION_ID = "users"

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
    ):
        """Initializes the user manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
        """
        self.global_state = global_state
        self.request_state = request_state
        self.json_db_manager = json_db_manager

    def list_users(self) -> List[User]:
        """Lists all users.

        TODO: Filter based on authenticated user?

        Returns:
            List[User]: List of users.
        """
        user_list: List[User] = []
        for json_document in self.json_db_manager.list_json_documents(
            config.SYSTEM_INTERNAL_PROJECT, self._COLLECTION_ID
        ):
            user_list.append(User(**json_document.json_value))
        return user_list

    def create_user(self, user_input: UserInput, technical_user: bool = False) -> User:
        """Creates a user.

        Args:
            user_input: The user data to create the new user.
            technical_user: If `True`, the created user will be marked as technical user. Defaults to `False`.

        Raises:
            ResourceAlreadyExistsError: If a user with the same username or email already exists.

        Returns:
            User: The created user information.
        """
        user_id = id_utils.generate_short_uuid()
        user = User(
            id=user_id,
            technical_user=technical_user,
            created_at=datetime.now(),
            **user_input.dict(exclude_unset=True),
        )

        created_document = self.json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._COLLECTION_ID,
            key=user_id,
            json_document=user.dict(),
        )

        return User(**created_document.json_value)

    def get_user(self, user_id: str) -> User:
        """Returns the user metadata for a single user.

        Args:
            user_id: The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The user information.
        """
        json_document = self.json_db_manager.get_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._COLLECTION_ID,
            key=user_id,
        )
        return User(**json_document.json_value)

    def update_user(self, user_id: str, user_input: UserInput) -> User:
        """Updates the user metadata.

        This will update only the properties that are explicitly set in the `user_input`.
        The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).

        Args:
            user_id (str): The ID of the user.
            user_input (UserInput): The user data used to update the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The updated user information.
        """
        updated_document = self.json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._COLLECTION_ID,
            key=user_id,
            json_document=user_input.dict(exclude_unset=True),
        )
        return User(**updated_document.json_value)

    def delete_user(self, user_id: str) -> None:
        """Deletes a user.

        Args:
            user_id (str): The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.
        """
        self.json_db_manager.delete_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._COLLECTION_ID, user_id
        )
