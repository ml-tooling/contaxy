from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pymongo.database import Database

from contaxy.auth import Authenticatable, AuthenticationManager
from contaxy.config import Settings
from contaxy.user import BaseUserManager, User, UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


def get_authenticator(
    settings: Settings = Depends(get_settings),
    user_manager: UserManager = Depends(get_user_manager),
) -> AuthenticationManager:
    return AuthenticationManager(settings, user_manager)


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


def seed_db(client: MongoClient, db_name: str):
    # Todo: Will be removed
    fake_users_db: List[dict] = [
        {
            "id": "1",
            "username": "admin",
            "email": "admin@mltooling.org",
            "display_name": "Lukas Podolski",
            "password": "$2b$12$zzWEQiyZ6BWAprjS9Wg90eOA3QlS1nBrKWVhhNKGR9rSNaY0Z6JZ.",
            "scopes": ["admin"],
        },
        {
            "id": "2",
            "username": "johndoe",
            "display_name": "John Doe",
            "email": "johndoe@example.com",
            "password": "$2b$12$TMntBg236.H/HLDw/cIJY.pnE7JPBekI3Jlk5/Fb4Pq0ZRsr75hqG",
        },
        {
            "id": "3",
            "username": "hanspeter",
            "display_name": "Hans Peter",
            "email": "hanspeter@example.com",
            "password": "$2b$12$trFr5B9mpkghxqsoM2C8jOjTMil37Ohpmhh9p2dsx0EssTdb75Mo.",
        },
    ]
    client[db_name].users.insert_many(fake_users_db)
