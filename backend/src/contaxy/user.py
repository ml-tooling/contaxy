import uuid
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
    def create_user(self, user: UserIn) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_id(
        self,
        id: str,
    ) -> Optional[User]:
        pass

    @abstractmethod
    def get_user(
        self,
        username: Optional[str] = None,
        email: Optional[EmailStr] = None,
    ) -> Optional[User]:
        pass

    @abstractmethod
    def get_users(self) -> List[User]:
        pass

    @abstractmethod
    def update_user(self, id: str, user: UserIn) -> Optional[User]:
        pass

    @abstractmethod
    def delete_user(self, id: Optional[str], username: Optional[str]) -> bool:
        pass


class UserManager(BaseUserManager):

    USERS_COLLECTION = "users"

    def __init__(self, db: Database) -> None:
        super().__init__()
        self._db = db
        self._collection = self._db[self.USERS_COLLECTION]

    def create_user(self, user: UserIn) -> Optional[User]:
        user_data = user.dict()
        user_data["id"] = str(uuid.uuid4())
        new_user = User(**user_data)
        user_data["password"] = user.password.get_secret_value()
        result = self._collection.insert_one(user_data)
        return new_user if result.inserted_id else None

    def get_user_by_id(self, id: str) -> Optional[User]:
        user_data = self._collection.find_one({"id": id})
        return User(**user_data) if user_data else None

    def get_user(
        self,
        username: Optional[str] = None,
        email: Optional[EmailStr] = None,
    ) -> Optional[User]:

        if not username and not email:
            return None
        collection = self._db[self.USERS_COLLECTION]

        filter = {}

        if username:
            filter.update({"username": username})
        if email:
            filter.update({"email": email})

        user_data = collection.find_one(filter)

        return User(**user_data) if user_data else None

    def get_users(self) -> List[User]:
        pass

    def update_user(self, id: str, user: UserIn) -> Optional[User]:
        pass

    def delete_user(self, id: Optional[str], username: Optional[str]) -> bool:
        pass
