from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "secret"
    acces_token_expiry_minutes: Optional[int] = 30
    jwt_algorithm = "HS256"
