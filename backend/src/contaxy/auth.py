from datetime import datetime, timedelta
from typing import List, Optional

from fastapi.param_functions import Form
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pydantic.networks import EmailStr
from pydantic.types import SecretStr

from contaxy.config import Settings
from contaxy.exceptions import AuthenticationError
from contaxy.user import BaseUserManager, User, UserIn, UserOut


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Authenticatable(BaseModel):
    id: str
    permissions: List[str] = []


class AuthManager:
    def __init__(
        self,
        settings: Settings,
        user_manager: BaseUserManager,
    ) -> None:
        self.settings = settings
        self.user_manager = user_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, user: UserIn) -> UserOut:
        if self.settings.user_registration_disabled:
            raise AuthenticationError(AuthenticationError.USER_REGISTRATION_DEACTIVATED)
        if self.user_manager.get_user(user.username):
            raise AuthenticationError(AuthenticationError.USERNAME_EXISTS)
        if self.user_manager.get_user(email=user.email):
            raise AuthenticationError(AuthenticationError.EMAIL_EXISTS)

        user.password = SecretStr(
            self.pwd_context.hash(user.password.get_secret_value())
        )

        # Todo: Enforce password policy here
        new_user = self.user_manager.create_user(user)
        if not new_user:
            raise AuthenticationError(AuthenticationError.USER_REGISTRATION_FAILED)
        return UserOut(**new_user.dict())

    def authenticate_user(self, username: str, password: SecretStr) -> Token:
        user = self.user_manager.get_user(username)
        if not user:
            raise AuthenticationError(AuthenticationError.UNKNOWN_USERNAME)
        if not self.verify_password(password, user.password):
            raise AuthenticationError(AuthenticationError.INCORRECT_PASSWORD)
        return self.create_access_token(user)

    def verify_password(self, password: SecretStr, hashed_password: SecretStr) -> bool:
        return self.pwd_context.verify(
            password.get_secret_value(), hashed_password.get_secret_value()
        )

    def create_access_token(self, user: User) -> Token:
        # Todo: Add dedicated field for the user id
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
        return self.user_manager.get_user_by_id(auth.id)


class LoginForm:
    def __init__(
        self,
        username: str = Form(..., description="Username"),
        password: str = Form(..., description="Password"),
        email: Optional[EmailStr] = Form(None, description="Email"),
        display_name: Optional[str] = Form(
            None,
            description="The display name can be chosen arbritarily. It can be changed anytime by updating the user data.",
        ),
    ):
        self.username = username
        self.password = password
        self.email = email
        self.display_name = display_name
