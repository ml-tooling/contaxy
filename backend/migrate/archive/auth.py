from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from contaxy.config import Settings
from contaxy.users import User, UserManager


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Authenticator:
    def __init__(
        self,
        settings: Settings,
        user_manager: UserManager,
    ) -> None:
        self.settings = settings
        self.user_manager = user_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_manager.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user: User) -> Token:
        to_encode: dict = {"sub": user.username, "scopes": user.scopes}

        if self.settings.acces_token_expiry_minutes:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.acces_token_expiry_minutes
            )
            to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.settings.jwt_algorithm
        )

        return Token(access_token=encoded_jwt)

    def get_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError:
            return None
        username: str = payload.get("sub")
        if not username:
            return None
        return self.user_manager.get_user(username)


# ----------------------------------------------------------

import json

import pytest


@pytest.mark.skip(reason="Database code to use Postgres has to be finished")
@pytest.mark.integration
class TestAuthApi:
    def test_login(self, client) -> None:

        client.headers.update(
            {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        response = request_login(
            client=client, form_data={"username": "admin", "password": "admin"}
        )
        assert response.status_code == 200
        response_data = json.loads(response.text)
        assert response_data.get("access_token")

    def test_user_profile(self, client, admin_token: str) -> None:
        client.headers.update(
            {"accept": "application/json", "authorization": admin_token}
        )
        response = request_user_profile(client=client)
        assert response.status_code == 200
        response_data = json.loads(response.text)
        assert response_data.get("username") == "admin"
        assert "password" not in response_data
