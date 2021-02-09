from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "secret"
    acces_token_expiry_minutes: Optional[int] = 30
    jwt_algorithm: str = "HS256"
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db_name: str = "contaxy"
    mongo_image: str = "mongo:4.2"
    user_registration_disabled: bool = False
    # Used for Docker outside Docker scenarios e.g. when developing in the
    # workspace, all containers need to be in the same network
    local_test_docker_network: Optional[str] = None
