import os
from datetime import timedelta
from enum import Enum
from typing import List, Optional, Union

from loguru import logger
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

API_TOKEN_NAME: str = "ct_token"
AUTHORIZED_USER_COOKIE: str = "ctxy_authorized_user"
SYSTEM_INTERNAL_PROJECT: str = "system"
SYSTEM_ADMIN_USERNAME: str = "admin"
SYSTEM_ADMIN_INITIAL_PASSWORD: str = "admin"


class DeploymentManager(str, Enum):
    KUBERNETES = "kubernetes"
    DOCKER = "docker"


# MAX_SYSTEM_NAMESPACE_LENGTH = 5
# def get_system_namespace(system_name: str) -> str:
#    return id_utils.generate_readable_id(
#        system_name,
#        max_length=MAX_SYSTEM_NAMESPACE_LENGTH,
#        min_length=3,
#        max_hash_suffix_length=MAX_SYSTEM_NAMESPACE_LENGTH,
#        separator="",
#    )


class Settings(BaseSettings):
    """Platform Settings."""

    # TODO Decide on default values
    CONTAXY_HOST: Optional[str] = None
    # Set the base url prefix
    CONTAXY_BASE_URL: str = ""
    # ? Maybe mobe up to system constants for now
    # TODO Make actually configurable, i.e. ensure no hardcoded paths exists anymore (backend/webapp/nginx)
    CONTAXY_API_PATH: str = "api"
    CONTAXY_WEBAPP_PATH: str = "app"

    # TODO: handle HTTP/HTTPS
    # bypass Contaxy nginx and access FastAPI directly
    CONTAXY_API_ENDPOINT: str = "http://contaxy:8090/api"

    # The system namespace used to managed different versions
    SYSTEM_NAMESPACE: str = "ctxy"

    # Selected deployment manager
    DEPLOYMENT_MANAGER: DeploymentManager = DeploymentManager.DOCKER
    KUBERNETES_NAMESPACE: Optional[str] = None
    HOST_DATA_ROOT_PATH: Optional[str] = None
    SERVICE_IDLE_CHECK_INTERVAL: timedelta = timedelta(minutes=20)

    # Ensure host data root path ends with a slash
    @validator("HOST_DATA_ROOT_PATH")
    def _validate_host_data_root_path(cls, host_data_root_path: str) -> str:
        if host_data_root_path is None or host_data_root_path.endswith("/"):
            return host_data_root_path
        return f"{host_data_root_path}/"

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

    # Azure Blob Storage Connection Configuration for File Manager
    AZURE_BLOB_CONNECTION_STRING: Optional[str] = None
    AZURE_BLOB_TOKEN: Optional[str] = None

    # Cache Settings
    # VERIFY_ACCESS_CACHE caches all token <-> permission verifications
    VERIFY_ACCESS_CACHE_ENABLED: bool = True  # Enable or disable the cache
    VERIFY_ACCESS_CACHE_SIZE: int = 10000  # number of items in the cache
    VERIFY_ACCESS_CACHE_EXPIRY: int = 300  # Time to live of cache items in seconds
    # API_TOKEN_CACHE caches all db request to get the api token metadata
    API_TOKEN_CACHE_ENABLED: bool = True  # Enable or disable the cache
    API_TOKEN_CACHE_SIZE: int = 10000  # number of items in the cache
    API_TOKEN_CACHE_EXPIRY: int = 300  # Time to live of cache items in seconds
    # RESOURCE_PERMISSIONS caches all permissions granted to resources.
    RESOURCE_PERMISSIONS_CACHE_ENABLED: bool = (
        False  # Enable or disable the cache # TODO: currently not working -> deadlock
    )
    RESOURCE_PERMISSIONS_CACHE_SIZE: int = 10000  # number of items in the cache
    RESOURCE_PERMISSIONS_CACHE_EXPIRY: int = 10  # Time to live of cache items in seconds - This cache should have a very short lifetime

    # Usabel to deactivate setting or changing user passwords
    # The `system-admin` account can still set and change passwords for users,
    # or use the basic auth authentication login page
    # TODO: Maybe only introduce (rename?) a flag indicating whether an external identity provider based on OIDC is used for authentication or whether the default "contaxy password flow" will be used
    PASSWORD_AUTH_ENABLED: bool = True
    USER_REGISTRATION_ENABLED: bool = True

    # External Identity provider configuration
    # ! To test this locally OAUTHLIB_INSECURE_TRANSPORT=1 needs to be set as env variable
    OIDC_AUTH_ENABLED: bool = False
    OIDC_AUTH_URL: Optional[str] = None
    OIDC_TOKEN_URL: Optional[str] = None
    OIDC_CLIENT_ID: Optional[str] = None
    OIDC_CLIENT_SECRET: Optional[str] = None

    # JWT Session Tokens
    JWT_TOKEN_SECRET: str = "please-change-this-secret"
    JWT_TOKEN_EXPIRY_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"

    # API Token Length
    API_TOKEN_LENGTH: int = 40

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    # see this GitHub issue for issue with env list decoding and why validator is needed: https://github.com/samuelcolvin/pydantic/issues/1458
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def _assemble_cors_origins(
        cls, cors_origins: Union[str, List[AnyHttpUrl]]
    ) -> Union[str, List[AnyHttpUrl]]:
        if isinstance(cors_origins, str):
            return [item.strip() for item in cors_origins.split(",")]  # type: ignore
        return cors_origins

    # TODO: Finalize
    DEBUG: bool = False
    DEBUG_DEACTIVATE_VERIFICATION: bool = False

    def get_redirect_uri(self, omit_host: bool = False) -> str:
        """Get the redirect URI composed of the CONTAXY_HOST and CONTAXY_API_BASE_URL."""

        if not omit_host and not self.CONTAXY_HOST:
            logger.critical(
                "The CONTAXY_HOST configuration is missing and OIDC_AUTH_ENABLED."
            )
            return ""

        if omit_host:
            host = ""
            base_url = "" if not self.CONTAXY_BASE_URL else self.CONTAXY_BASE_URL
        else:
            assert self.CONTAXY_HOST
            host = self.CONTAXY_HOST
            base_url = (
                "" if not self.CONTAXY_BASE_URL else self.CONTAXY_BASE_URL.lstrip("/")
            )

        return os.path.join(host, base_url)

    class Config:
        # Support local .env files
        env_file = ".env"
        env_file_encoding = "utf-8"
        # TODO: Support docker secrets
        # Only newer versions will throw warnings
        # secrets_dir = "/run/secrets"


settings = Settings()
