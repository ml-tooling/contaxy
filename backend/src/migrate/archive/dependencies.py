from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from contaxy.auth import Authenticator
from contaxy.config import Settings
from contaxy.users import User, UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_settings():
    return Settings()


def get_authenticator(settings: Settings = Depends(get_settings)) -> Authenticator:
    return Authenticator(settings, UserManager())


def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
    auth: Authenticator = Depends(get_authenticator),
) -> User:

    user = auth.get_user(token)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
