from typing import List, Optional

from pydantic import BaseModel
from pydantic.networks import EmailStr
from pydantic.types import SecretStr


class UserOut(BaseModel):
    username: str
    email: Optional[EmailStr]
    display_name: Optional[str]


class UserIn(UserOut):
    password: SecretStr


class User(UserIn):
    id: str
    password: SecretStr
    permissions: List[str] = []
