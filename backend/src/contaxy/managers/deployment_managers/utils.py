import os
from enum import Enum

APP_NAME = "contaxy"
APP_NAME_UPPER = APP_NAME.upper()

ENV_HOST_DATA_ROOT_PATH = f"{APP_NAME_UPPER}_DATA_ROOT"
# HOST_DATA_ROOT_PATH must end with a trailing slash so that we don't have to put handling of host paths vs. named volumes into if-clauses etc.
HOST_DATA_ROOT_PATH = os.getenv(ENV_HOST_DATA_ROOT_PATH, "")
if HOST_DATA_ROOT_PATH != "" and not HOST_DATA_ROOT_PATH.endswith("/"):
    HOST_DATA_ROOT_PATH = f"{HOST_DATA_ROOT_PATH}/"

ENV_NAMESPACE = f"{APP_NAME_UPPER}_NAMESPACE"
NAMESPACE = os.getenv(ENV_NAMESPACE, APP_NAME)

DEFAULT_DEPLOYMENT_ACTION_ID = "default"


class Labels(Enum):
    DEPLOYMENT_NAME = f"{APP_NAME}.deploymentName"
    DEPLOYMENT_TYPE = f"{APP_NAME}.deploymentType"
    DESCRIPTION = f"{APP_NAME}.description"
    DISPLAY_NAME = f"{APP_NAME}.displayName"
    ENDPOINTS = f"{APP_NAME}.endpoints"
    ICON = f"{APP_NAME}.icon"
    NAMESPACE = f"{APP_NAME}.namespace"
    MIN_LIFETIME = f"{APP_NAME}.minLifetime"
    PROJECT_NAME = f"{APP_NAME}.projectName"
    REQUIREMENTS = f"{APP_NAME}.requirements"
    VOLUME_PATH = f"{APP_NAME}.volumePath"


class ComputeResourcesError(Exception):
    pass


class DeploymentError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass


class TooManyEntitiesFoundError(Exception):
    pass


def get_volume_name(project_id: str, service_id: str) -> str:
    # TODO: follow naming concept for volumes
    return f"{project_id}-{service_id}-vol"


def normalize_service_name(project_id: str, display_name: str) -> str:
    # TODO: follow naming concept for services
    return f"{project_id}-{display_name.replace(' ', '-').lower()}"


def get_label_string(key: str, value: str) -> str:
    return f"{key}={value}"


def log(string: str):
    print(string)
