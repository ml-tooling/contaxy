from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pymongo.database import Database

from .config import Settings
from .managers.auth import Authenticatable, AuthManager
from .managers.users import BaseUserManager, UserManager
from .models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_settings():
    return Settings()


def get_db(settings: Settings = Depends(get_settings)):
    # Todo: Convert to generator
    client = MongoClient(settings.mongo_host, settings.mongo_port)
    dblist = client.list_database_names()
    if settings.mongo_db_name not in dblist:
        print(f"Seeding database {settings.mongo_db_name} ...")
    return client["contaxy"]


def get_user_manager(db: Database = Depends(get_db)) -> BaseUserManager:
    return UserManager(db)


def get_auth_manager(
    settings: Settings = Depends(get_settings),
    user_manager: UserManager = Depends(get_user_manager),
) -> AuthManager:
    return AuthManager(settings, user_manager)


def get_authenticatable(
    token: str = Depends(oauth2_scheme),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> Authenticatable:

    auth = auth_manager.get_authenticatable(token)

    if auth:
        return auth

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> User:
    user = auth_manager.get_user(token)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
