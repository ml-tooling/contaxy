import string
import subprocess
from enum import Enum
from typing import Any, Dict, List, Optional

from contaxy.config import settings
from contaxy.schema.deployment import DeploymentType
from contaxy.utils import id_utils

DEFAULT_DEPLOYMENT_ACTION_ID = "default"
NO_LOGS_MESSAGE = "No logs available."

_MAX_DEPLOYMENT_NAME_LENGTH = 15

_SERVICE_ID_SEPERATOR = "-s-"
_JOB_ID_SEPERATOR = "-j-"

_MIN_MEMORY_DEFAULT_MB = 100

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
    endpoints: Optional[List[str]] = None
    icon: Optional[str] = None
    min_lifetime: Optional[int] = None
    volume_path: Optional[str] = None
    metadata: Optional[dict] = None


def map_labels(labels: Dict[str, Any]) -> MappedLabels:
    """Transform label dict to a MappedLabels object.

    Special labels have their own field and additional, non-special labels are added to the MappedLabels.metadata field.

    Args:
        labels (dict): A dictionary containing key-value pairs that, for example, are used as container labels.

    Returns:
        MappedLabels: The labels object transformed to a MappedLabels object.
    """

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
        mapped_labels.endpoints = map_endpoints_label_to_endpoints(
            _labels.get(Labels.ENDPOINTS.value, "")
        )
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

    mapped_labels.metadata = _labels

    return mapped_labels


def clean_labels(labels: Optional[dict] = None) -> dict:
    """Remove system labels that should not be settable by the user.

    Args:
        labels (Optional[dict]): The labels dict from which system labels should be removed.

    Returns:
        dict: The new labels dict that does not contain any system labels or an empty dict.
    """

    if labels is None:
        return {}

    cleaned_labels = dict.copy(labels)

    if Labels.DEPLOYMENT_TYPE.value in cleaned_labels:
        del cleaned_labels[Labels.DEPLOYMENT_TYPE.value]
    if Labels.DESCRIPTION.value in cleaned_labels:
        del cleaned_labels[Labels.DESCRIPTION.value]
    if Labels.DISPLAY_NAME.value in cleaned_labels:
        del cleaned_labels[Labels.DISPLAY_NAME.value]
    if Labels.ENDPOINTS.value in cleaned_labels:
        del cleaned_labels[Labels.ENDPOINTS.value]
    if Labels.ICON.value in cleaned_labels:
        del cleaned_labels[Labels.ICON.value]
    if Labels.MIN_LIFETIME.value in cleaned_labels:
        del cleaned_labels[Labels.MIN_LIFETIME.value]
    if Labels.VOLUME_PATH.value in cleaned_labels:
        del cleaned_labels[Labels.VOLUME_PATH.value]
    if Labels.PROJECT_NAME.value in cleaned_labels:
        del cleaned_labels[Labels.PROJECT_NAME.value]
    if Labels.REQUIREMENTS.value in cleaned_labels:
        del cleaned_labels[Labels.REQUIREMENTS.value]
    if Labels.NAMESPACE.value in cleaned_labels:
        del cleaned_labels[Labels.NAMESPACE.value]

    return cleaned_labels


def get_deployment_id(
    project_id: str, deployment_name: str, deployment_type: DeploymentType
) -> str:
    """Returns a valid deployment ID based on some specified metadata.

    Args:
        project_id (str): The ID of the project associated with the deployment.
        deployment_name (str): The name of the deployment. This can be an arbitrary text.
        deployment_type (DeploymentType): The type of the deployment.

    Returns:
        str: A valid deployment ID.
    """
    separator = _SERVICE_ID_SEPERATOR
    if deployment_type == DeploymentType.JOB:
        # Currently, only job has a different separator
        separator = _JOB_ID_SEPERATOR

    deployment_name_part = id_utils.generate_readable_id(
        deployment_name,
        max_length=_MAX_DEPLOYMENT_NAME_LENGTH,
        min_length=4,
        max_hash_suffix_length=5,
        stopwords=list(string.ascii_lowercase),
    )

    # A resource prefix based on the namespace and project id.
    # has a maximum length of 5 (namespace) + 3 (seperator) + 15 (project id) = 23
    project_resource_prefix = id_utils.get_project_resource_prefix(project_id)

    return project_resource_prefix + separator + deployment_name_part


def get_volume_name(project_id: str, service_id: str) -> str:
    # TODO: follow naming concept for volumes
    return f"{project_id}-{service_id}-vol"


def get_network_name(project_id: str) -> str:
    return f"{id_utils.get_project_resource_prefix(project_id)}-network"


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


def get_project_selection_labels(
    project_id: str, deployment_type: DeploymentType = DeploymentType.SERVICE
) -> List:
    """Return a list of labels identifying project resources (system namespace, project id, deployment type).

    Args:
        project_id (str): The project id included in the label list.
        deployment_type (DeploymentType, optional): The deployment type included in the label list. Defaults to DeploymentType.SERVICE.

    Returns:
        List: Contains the labels identifying project resources.
    """
    return [
        (Labels.NAMESPACE.value, settings.SYSTEM_NAMESPACE),
        (Labels.PROJECT_NAME.value, project_id),
        (Labels.DEPLOYMENT_TYPE.value, deployment_type.value),
    ]


def map_endpoints_to_endpoints_label(endpoints: Optional[List[str]]) -> Optional[str]:
    return ",".join(endpoints) if endpoints else None


def map_endpoints_label_to_endpoints(
    endpoints_label: Optional[str],
) -> Optional[List[str]]:
    return endpoints_label.split(",") if endpoints_label else None
