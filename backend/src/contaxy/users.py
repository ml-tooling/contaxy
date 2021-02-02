from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel

fake_users_db: Dict[str, dict] = {
    "admin": {
        "id": "1",
        "username": "admin",
        "email": "admin@mltooling.org",
        "password": "$2b$12$zzWEQiyZ6BWAprjS9Wg90eOA3QlS1nBrKWVhhNKGR9rSNaY0Z6JZ.",
        "scopes": ["admin"],
    },
    "johndoe": {
        "id": "2",
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "$2b$12$TMntBg236.H/HLDw/cIJY.pnE7JPBekI3Jlk5/Fb4Pq0ZRsr75hqG",
    },
    "hanspeter": {
        "id": "3",
        "username": "hanspeter",
        "full_name": "Hans Peter",
        "email": "hanspeter@example.com",
        "password": "$2b$12$trFr5B9mpkghxqsoM2C8jOjTMil37Ohpmhh9p2dsx0EssTdb75Mo.",
        "disabled": False,
    },
}


class UserIn(BaseModel):
    username: str
    password: str
    email: Optional[str]
    display_name: Optional[str]
    permissions: List[str] = []


class User(BaseModel):
    id: str
    username: str
    password: str
    email: Optional[str]
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
    ) -> User:
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
    def create_user(self, user: UserIn) -> User:
        pass

    def get_user(
        self,
        id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> User:
        assert username
        user_data = fake_users_db.get(username)
        assert user_data
        return User(**user_data)

    def get_users(self) -> List[User]:
        pass

    def update_user(self, id: str, user: UserIn) -> User:
        pass

    def delete_user(self, id: Optional[str], username: Optional[str]) -> None:
        pass
