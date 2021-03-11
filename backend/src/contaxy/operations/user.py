from abc import ABC, abstractmethod
from typing import List

from contaxy.schema import User, UserInput


class UserOperations(ABC):
    @abstractmethod
    def list_users(self) -> List[User]:
        pass

    @abstractmethod
    def create_user(self, user_input: UserInput, technical_user: bool = False) -> User:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> User:
        pass

    @abstractmethod
    def update_user(self, user_id: str, user_input: UserInput) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        pass
