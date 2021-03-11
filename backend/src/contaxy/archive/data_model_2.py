from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import (
    UUID4,
    BaseModel,
    BaseSettings,
    ByteSize,
    EmailStr,
    Field,
    Json,
    SecretStr,
    constr,
)
from pydantic.errors import DateError
from pydantic.networks import stricturl

MIN_DISPLAY_NAME_LENGTH = 4
MAX_DISPLAY_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 240
MIN_PROJECT_ID_LENGTH = 4
MAX_PROJECT_ID_LENGTH = 25


RESOURCE_ID_REGEX = r"^(?!.*--)[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
QUALIFIED_RESOURCE_ID_REGEX = (
    r"^(?!.*--)[a-z0-9\-]{1,61}[a-z0-9]$"  # TODO: start with [a-z]
)
FILE_KEY_REGEX = r"^(?!.*(\r|\n|\.\.)).{1,1024}$"  # no new lines or consecutive dots


class Settings(BaseSettings):
    """Platform Settings."""

    # Deactivate Setting or changing password from user accounts
    # Admins can still set and change passwords for users, or use the basic auth authentication login page
    DISABLE_BASIC_AUTH: str


class DeploymentType(str, Enum):
    SERVICE = "service"
    JOB = "job"
    EXTENSION = "extension"


class ExtensionType(str, Enum):
    USER_EXTENSION = "user-extension"
    PROJECT_EXTENSION = "project-extension"


class TechnicalProject(str, Enum):
    SYSTEM_INTERNAL = "system-internal"  # only admin access
    SYSTEM_GLOBAL = "system-global"  # services are accesible to all users, but the service needs to set the service session token by itself


class DeploymentRequirement(str, Enum):
    DOCKER_SOCKET = "docker-socket"
    KUBECTL = "kubectl"
    NVIDIA_GPU = "nvidia-gpu"


class TokenType(str, Enum):
    SESSION_TOKEN = "session-token"
    API_TOKEN = "api-token"


class ResourceType(str, Enum):
    USER = "user"
    PROJECT = "project"
    DEPLOYMENT = "deployment"
    FILE = "file"
    SECRET = "secret"
    JSON_DOCUMENT = "json-document"


class DataType(str, Enum):
    DATASET = "dataset"
    CONFIG = "config"
    MODEL = "model"
    OTHER = "other"


class ContainerOrchestrator(str, Enum):
    KUBERNETES = "kubernetes"
    DOCKER_LOCAL = "docker-local"


class BaseEntity(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        underscore_attrs_are_private = True
        # TODO: should we set a max length for string to prevent to big requests?
        max_anystr_length = 20000


class GlobalID(BaseEntity):
    format_version: int = Field(1, description="Version of the ID structure.")
    resource_type: str = Field(..., description="Type of the resource")
    subject_id: str = Field(...)
    project_id: Optional[str] = Field(None)
    extension_id: Optional[str] = Field(
        None,
        example="john-doe",
        description="The extension ID in case the deployment is deployed via an extension.",
    )


class Permission(BaseEntity):
    global_id: GlobalID = Field(..., description="The global ID of the entity ")
    permission_level: PermissionLevel = Field(
        ..., description="The kind of access that is granted on the resource."
    )
    restriction: Optional[str] = Field(None)


class ConfigurationType(str, Enum):
    MONGO_DB_CONNECTION = "mongo-db-connection"
    SSH_CONNECTION = "ssh-connection"
    POSTGRES_DB_CONNECTION = "postgres-connection"


class ConfigurationInput(BaseEntity):
    id: str = Field(
        ...,
        example="customer-mongo-db",
        description="ID of the configuration.",
    )
    configuration_type: Optional[ConfigurationType] = Field(
        None,
        example=ConfigurationType.MONGO_DB_CONNECTION,
        description="Predefined type of this configuration.",
    )
    parameters: Optional[Dict[str, str]] = Field(
        None,
        example={
            "MONGO_DB_URI": "mongodb://mongodb0.example.com:27017",
            "MONGO_DB_USER": "admin",
            "MONGO_DB_PASSWORD": "f4528e540a133dd53ba6809e74e16774ebe4777a",
        },
        description="Parmeters (enviornment variables) shared with this configuration.",
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        example="Mongo DB connection to customer database.",
        description="Short description about this configuration.",
    )
    icon: Optional[str] = Field(
        None,
        example="table_chart",
        max_length=1000,
        description="Material Design Icon name or image URL used for displaying this configuration.",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags associated with this configuration.",
    )


class Configuration(ConfigurationInput):
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Date when the configuration was created.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this configuration.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the configuration was updated.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last modified this configuration.",
    )


class SecretInput(BaseEntity):
    # TODO: Use value encryption like in Github API, but Vault is not encrypting
    value: str = Field(
        ...,
        example="f4528e540a133dd53ba6809e74e16774ebe4777a",
        description="Value of the secret.",
    )
    # TODO: group_name -> group secrets together (e.g. all details for a db conenction)


class Secret(SecretInput):
    key: str = Field(
        ...,
        example="MY_API_TOKEN",
        description="Name of the secret.",
    )
    # == Shared Parameters
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the secret.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this secret.",
    )


class SystemStatistics(BaseEntity):
    # TODO: finish model
    project_count: int
    user_count: int
    job_count: int
    service_count: int
    file_count: int
