import subprocess
from enum import Enum
from typing import Optional

from contaxy.config import settings

DEFAULT_DEPLOYMENT_ACTION_ID = "default"
NO_LOGS_MESSAGE = "No logs available."


class Labels(Enum):
    DEPLOYMENT_NAME = f"{settings.SYSTEM_NAMESPACE}.deploymentName"
    DEPLOYMENT_TYPE = f"{settings.SYSTEM_NAMESPACE}.deploymentType"
    DESCRIPTION = f"{settings.SYSTEM_NAMESPACE}.description"
    DISPLAY_NAME = f"{settings.SYSTEM_NAMESPACE}.displayName"
    ENDPOINTS = f"{settings.SYSTEM_NAMESPACE}.endpoints"
    ICON = f"{settings.SYSTEM_NAMESPACE}.icon"
    NAMESPACE = f"{settings.SYSTEM_NAMESPACE}.namespace"
    MIN_LIFETIME = f"{settings.SYSTEM_NAMESPACE}.minLifetime"
    PROJECT_NAME = f"{settings.SYSTEM_NAMESPACE}.projectName"
    REQUIREMENTS = f"{settings.SYSTEM_NAMESPACE}.requirements"
    VOLUME_PATH = f"{settings.SYSTEM_NAMESPACE}.volumePath"


class MappedLabels:
    deployment_type: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    endpoints: Optional[str] = None
    icon: Optional[str] = None
    min_lifetime: Optional[int] = None
    volume_path: Optional[str] = None
    additional_metadata: Optional[dict] = None


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


def get_volume_name(project_id: str, service_id: str) -> str:
    # TODO: follow naming concept for volumes
    return f"{project_id}-{service_id}-vol"


def get_network_name(project_id: str) -> str:
    # TODO: follow naming concept for networks
    return f"{project_id}-network"


def normalize_service_name(project_id: str, display_name: str) -> str:
    # TODO: follow naming concept for services
    return f"{project_id}-{display_name.replace(' ', '-').lower()}"


def get_label_string(key: str, value: str) -> str:
    return f"{key}={value}"


def get_gpu_info() -> int:
    count_gpu = 0
    try:
        # NOTE: this approach currently only works for nvidia gpus.
        ps = subprocess.Popen(
            ("find", "/proc/irq/", "-name", "nvidia"), stdout=subprocess.PIPE
        )
        output = subprocess.check_output(("wc", "-l"), stdin=ps.stdout)
        ps.wait()
        count_gpu = int(output.decode("utf-8"))
    except Exception:
        pass

    return count_gpu


# TODO: replace!
def log(input: str) -> None:
    print(input)
