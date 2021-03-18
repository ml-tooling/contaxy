"""Operations associated with the user handling."""

from abc import ABC, abstractmethod
from typing import List

from contaxy.schema import User, UserInput


class UserOperations(ABC):
    """Interface with operations associated with the user handling.

    This interface should be implemented by a user manager.
    """

    @abstractmethod
    def list_users(self) -> List[User]:
        """Lists all users.

        TODO: Filter based on authenticated user?

        Returns:
            List[User]: List of users.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> User:
        """Returns the user metadata for a single user.

        Args:
            user_id: The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.

        Returns:
            User: The user information.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        """Deletes a user.

        Args:
            user_id (str): The ID of the user.

        Raises:
            ResourceNotFoundError: If no user with the specified ID exists.
        """
        pass
