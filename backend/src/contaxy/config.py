from enum import Enum
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn

API_TOKEN_NAME: str = "ct_token"
SYSTEM_INTERNAL_PROJECT: str = "system"
SYSTEM_ADMIN_USERNAME: str = "admin"
SYSTEM_ADMIN_INITIAL_PASSWORD: str = "admin"


class DeploymentManager(str, Enum):
    KUBERNETES = "kubernetes"
    DOCKER = "docker"

# TODO
# MAX_SYSTEM_NAMESPACE_LENGTH = 5
#def get_system_namespace(system_name: str) -> str:
#    return id_utils.generate_readable_id(
#        system_name,
#        max_length=MAX_SYSTEM_NAMESPACE_LENGTH,
#        min_length=3,
#        max_hash_suffix_length=MAX_SYSTEM_NAMESPACE_LENGTH,
#        separator="",
#    )


class Settings(BaseSettings):
    """Platform Settings."""

    # The system namespace used to managed different versions
    SYSTEM_NAMESPACE: str = "ctxy"

    # Selected deployment manager
    DEPLOYMENT_MANAGER: DeploymentManager = DeploymentManager.DOCKER
    HOST_DATA_ROOT_PATH: Optional[str] = None
    if HOST_DATA_ROOT_PATH is not None and not HOST_DATA_ROOT_PATH.endswith("/"):
        HOST_DATA_ROOT_PATH = f"{HOST_DATA_ROOT_PATH}/"

    # Postgres Connection URI to use for JSON Document Manager
    # If `None`, a dedicated postgres instance will be started as a service (container).
    POSTGRES_CONNECTION_URI: Optional[PostgresDsn] = None

    # S3 Storage Connection Configuration for File Manager
    # If `S3_ENDPOINT` is `None`, a dedicated minio instance will be started as a service (container).
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_SECURE: Optional[bool] = None
    # TODO: support for managing all data in a single bucket S3_BUCKET: Optional[str] = None

    # Usabel to deactivate setting or changing user passwords
    # The `system-admin` account can still set and change passwords for users,
    # or use the basic auth authentication login page
    BASIC_AUTH_ENABLED: bool = True
    USER_REGISTRATION_ENABLED: bool = True

    # JWT Session Tokens
    JWT_TOKEN_SECRET: str = "please-change-this-secret"
    JWT_TOKEN_EXPIRY_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        # Support local .env files
        env_file = ".env"
        env_file_encoding = "utf-8"
        # TODO: Support docker secrets
        # Only newer versions will throw warnings
        # secrets_dir = "/run/secrets"


settings = Settings()
