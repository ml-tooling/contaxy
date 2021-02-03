from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from contaxy.auth import Authenticatable, AuthenticationManager
from contaxy.config import Settings
from contaxy.users import User, UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_settings():
    return Settings()


def get_authenticator(
    settings: Settings = Depends(get_settings),
) -> AuthenticationManager:
    return AuthenticationManager(settings, UserManager())


def get_authenticatable(
    token: str = Depends(oauth2_scheme),
    authenticator: AuthenticationManager = Depends(get_authenticator),
) -> Authenticatable:

    auth = authenticator.get_authenticatable(token)
    if auth:
        return auth

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
    authenticator: AuthenticationManager = Depends(get_authenticator),
) -> User:

    user = authenticator.get_user(token)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
