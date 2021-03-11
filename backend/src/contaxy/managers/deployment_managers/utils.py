import os
from enum import Enum
from typing import Optional

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

NO_LOGS_MESSAGE = "No logs available"
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


class MappedLabels:
    deployment_type: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    endpoints: Optional[str] = None
    icon: Optional[str] = None
    min_lifetime: Optional[int] = None
    volume_path: Optional[str] = None
    additional_metadata: Optional[dict] = None


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


def log(string: str) -> None:
    print(string)


def map_labels(labels: dict) -> MappedLabels:
    _labels = dict.copy(labels)
    mapped_labels = MappedLabels()

    if Labels.DEPLOYMENT_TYPE.value in _labels:
        mapped_labels.deployment_type = _labels.get(Labels.DEPLOYMENT_TYPE.value)
        del _labels[Labels.DEPLOYMENT_TYPE.value]
    if Labels.DESCRIPTION.value in _labels:
        mapped_labels.description = _labels.get(Labels.DESCRIPTION.value)
        del _labels[Labels.DESCRIPTION.value]
    if Labels.DISPLAY_NAME.value in _labels:
        mapped_labels.display_name = _labels.get(Labels.DISPLAY_NAME.value)
        del _labels[Labels.DISPLAY_NAME.value]
    if Labels.ENDPOINTS.value in _labels:
        mapped_labels.endpoints = _labels.get(Labels.ENDPOINTS.value, "").split(",")
        del _labels[Labels.ENDPOINTS.value]
    if Labels.ICON.value in _labels:
        mapped_labels.icon = _labels.get(Labels.ICON.value)
        del _labels[Labels.ICON.value]
    if Labels.MIN_LIFETIME.value in _labels:
        mapped_labels.min_lifetime = _labels.get(Labels.MIN_LIFETIME.value)
        del _labels[Labels.MIN_LIFETIME.value]
    if Labels.VOLUME_PATH.value in _labels:
        mapped_labels.volume_path = _labels.get(Labels.VOLUME_PATH.value)
        del _labels[Labels.VOLUME_PATH.value]

    mapped_labels.additional_metadata = _labels

    return mapped_labels
