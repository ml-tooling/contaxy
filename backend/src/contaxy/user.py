from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel
from pydantic.networks import EmailStr
from pydantic.types import SecretStr
from pymongo.database import Database


class UserIn(BaseModel):
    username: str
    password: SecretStr
    email: Optional[EmailStr]
    display_name: Optional[str]
    permissions: List[str] = []


class User(BaseModel):
    id: str
    username: str
    password: SecretStr
    email: Optional[EmailStr]
    display_name: Optional[str]
    permissions: List[str] = []


class BaseUserManager(ABC):
    @abstractmethod
    def create_user(self, user: UserIn) -> User:
        pass

    @abstractmethod
    def get_user(
        self,
        id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        pass

    @abstractmethod
    def get_users(self) -> List[User]:
        pass

    @abstractmethod
    def update_user(self, id: str, user: UserIn) -> User:
        pass

    @abstractmethod
    def delete_user(self, id: Optional[str], username: Optional[str]) -> None:
        pass


class UserManager(BaseUserManager):

    USERS_COLLECTION = "users"

    def __init__(self, db: Database) -> None:
        super().__init__()
        self._db = db

    def create_user(self, user: UserIn) -> User:
        pass

    def get_user(
        self,
        id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        collection = self._db[self.USERS_COLLECTION]
        if id:
            user_data = collection.find_one({"id": id})
        elif username:
            user_data = collection.find_one({"username": username})
        elif email:
            user_data = collection.find_one({"email": email})
        else:
            raise ValueError("Missing user identifier")

        if not user_data:
            return None

        return User(**user_data)

        return None

    def get_users(self) -> List[User]:
        pass

    def update_user(self, id: str, user: UserIn) -> User:
        pass

    def delete_user(self, id: Optional[str], username: Optional[str]) -> None:
        pass
