from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pymongo.database import Database

from contaxy.auth import Authenticatable, AuthManager
from contaxy.config import Settings
from contaxy.user import BaseUserManager, User, UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_settings():
    return Settings()


def get_db(settings: Settings = Depends(get_settings)):
    # Todo: Convert to generator
    client = MongoClient(settings.mongo_host, settings.mongo_port)
    dblist = client.list_database_names()
    if settings.mongo_db_name not in dblist:
        print(f"Seeding database {settings.mongo_db_name} ...")
        seed_db(client, settings.mongo_db_name)
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


def seed_db(client: MongoClient, db_name: str):
    # Todo: Will be removed
    fake_users_db: List[dict] = [
        {
            "id": "1",
            "username": "admin",
            "email": "admin@mltooling.org",
            "display_name": "Lukas Podolski",
            "password": "$2b$12$zzWEQiyZ6BWAprjS9Wg90eOA3QlS1nBrKWVhhNKGR9rSNaY0Z6JZ.",
            "permissions": ["admin"],
        },
    ]
    client[db_name].users.insert_many(fake_users_db)
