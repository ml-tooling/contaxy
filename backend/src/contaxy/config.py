from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "secret"
    acces_token_expiry_minutes: Optional[int] = 30
    jwt_algorithm = "HS256"
    mongo_host = "localhost"
    mongo_port = 27017
    mongo_db_name = "contaxy"
    mongo_image = "mongo:4.2"
    user_registration_disabled = False
