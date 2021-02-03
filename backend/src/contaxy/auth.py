from datetime import datetime, timedelta
from typing import List, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from contaxy.config import Settings
from contaxy.user import BaseUserManager, User


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Authenticatable(BaseModel):
    id: str
    permissions: List[str] = []


class AuthenticationManager:
    def __init__(
        self,
        settings: Settings,
        user_manager: BaseUserManager,
    ) -> None:
        self.settings = settings
        self.user_manager = user_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_manager.get_user(username=username)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user: User) -> Token:
        # ? Should we use the user.id here?
        to_encode: dict = {"sub": user.id, "scopes": user.permissions}

        if self.settings.acces_token_expiry_minutes:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.acces_token_expiry_minutes
            )
            to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.settings.jwt_algorithm
        )

        return Token(access_token=encoded_jwt)

    def get_authenticatable(self, token: str) -> Optional[Authenticatable]:
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError:
            return None

        data = {"id": payload.get("sub"), "permissions": payload.get("scopes", [])}

        if not data.get("id"):
            return None

        return Authenticatable(**data)

    def get_user(self, token: str) -> Optional[User]:
        auth = self.get_authenticatable(token)
        if not auth:
            return None
        return self.user_manager.get_user(id=auth.id)
