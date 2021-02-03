from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel

fake_users_db: Dict[str, dict] = {
    "1": {
        "id": "1",
        "username": "admin",
        "email": "admin@mltooling.org",
        "full_name": "Lukas Podolski",
        "password": "$2b$12$zzWEQiyZ6BWAprjS9Wg90eOA3QlS1nBrKWVhhNKGR9rSNaY0Z6JZ.",
        "scopes": ["admin"],
    },
    "2": {
        "id": "2",
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "$2b$12$TMntBg236.H/HLDw/cIJY.pnE7JPBekI3Jlk5/Fb4Pq0ZRsr75hqG",
    },
    "3": {
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
    def create_user(self, user: UserIn) -> User:
        pass

    def get_user(
        self,
        id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        # Todo: Implement
        if id:
            return User(**fake_users_db[id])

        for user in fake_users_db.values():
            if username == user.get("username"):
                return User(**user)
            if email == user.get("email"):
                return User(**user)

        return None

    def get_users(self) -> List[User]:
        pass

    def update_user(self, id: str, user: UserIn) -> User:
        pass

    def delete_user(self, id: Optional[str], username: Optional[str]) -> None:
        pass
