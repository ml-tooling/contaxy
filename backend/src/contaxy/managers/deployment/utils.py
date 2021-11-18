import string
import subprocess
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from contaxy.config import settings
from contaxy.managers.auth import AuthManager
from contaxy.schema import AccessLevel, TokenType
from contaxy.schema.auth import TokenPurpose
from contaxy.schema.deployment import DeploymentCompute, DeploymentType
from contaxy.utils import auth_utils, id_utils

DEFAULT_DEPLOYMENT_ACTION_ID = "default"
NO_LOGS_MESSAGE = "No logs available."

_MAX_DEPLOYMENT_NAME_LENGTH = 15

_SERVICE_ID_SEPERATOR = "-s-"
_JOB_ID_SEPERATOR = "-j-"

_MIN_MEMORY_DEFAULT_MB = 100

_ENV_VARIABLE_CONTAXY_BASE_URL = "CONTAXY_BASE_URL"
_ENV_VARIABLE_CONTAXY_API_ENDPOINT = "CONTAXY_API_ENDPOINT"
_ENV_VARIABLE_CONTAXY_API_TOKEN = "CONTAXY_API_TOKEN"
_ENV_VARIABLE_CONTAXY_SERVICE_URL = "CONTAXY_SERVICE_URL"
_ENV_VARIABLE_CONTAXY_DEPLOYMENT_NAME = "CONTAXY_DEPLOYMENT_NAME"


class Labels(Enum):
    CREATED_BY = "ctxy.createdBy"
    DEPLOYMENT_NAME = "ctxy.deploymentName"
    DEPLOYMENT_TYPE = "ctxy.deploymentType"
    DESCRIPTION = "ctxy.description"
    DISPLAY_NAME = "ctxy.displayName"
    ENDPOINTS = "ctxy.endpoints"
    ICON = "ctxy.icon"
    NAMESPACE = "ctxy.namespace"
    MIN_LIFETIME = "ctxy.minLifetime"
    PROJECT_NAME = "ctxy.projectName"
    REQUIREMENTS = "ctxy.requirements"
    VOLUME_PATH = "ctxy.volumePath"


class MappedLabels:
    deployment_type: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    endpoints: Optional[List[str]] = None
    icon: Optional[str] = None
    min_lifetime: Optional[int] = None
    volume_path: Optional[str] = None
    metadata: Optional[dict] = None
    created_by: Optional[str] = None


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
    if Labels.CREATED_BY.value in cleaned_labels:
        del cleaned_labels[Labels.CREATED_BY.value]

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


def get_default_environment_variables(
    project_id: str,
    deployment_id: str,
    auth_manager: AuthManager,
    endpoints: Optional[List[str]] = None,
    compute_resources: Optional[DeploymentCompute] = None,
) -> Dict[str, str]:
    """Sets default environment variables that should be set for each container.

    Args:
        project_id (str): The project id included in the label list
        deployment_id (str)
        auth_manager (AuthManager): Auth manager used for creating an access token for the service
        endpoints (List[str]): List of endpoints
        compute_resources: (Optional[DeploymentCompute]): DeploymentCompute information

    Returns:
        Dict[str, str]: Dict with default environment variables or empty dict.
    """

    default_environment_variables = {
        _ENV_VARIABLE_CONTAXY_DEPLOYMENT_NAME: deployment_id,
        _ENV_VARIABLE_CONTAXY_BASE_URL: settings.CONTAXY_BASE_URL,
        _ENV_VARIABLE_CONTAXY_API_ENDPOINT: settings.CONTAXY_API_ENDPOINT,
    }

    # TODO: This url is only valid for services but not for jobs
    service_access_permission = auth_utils.construct_permission(
        f"/projects/{project_id}/services/{deployment_id}/access/", AccessLevel.READ
    )
    service_api_token = auth_manager.create_token(
        scopes=[service_access_permission],
        token_type=TokenType.API_TOKEN,
        description=f"Access token for service {deployment_id}.",
        token_purpose=TokenPurpose.SERVICE_ACCESS_TOKEN,
    )
    default_environment_variables[_ENV_VARIABLE_CONTAXY_API_TOKEN] = service_api_token

    if endpoints and len(endpoints) > 0:
        endpoint = endpoints[0]
        if len(endpoints) > 1:
            endpoint = "{endpoint}"
        # TODO: This url is only valid for services but not for jobs
        default_environment_variables[
            _ENV_VARIABLE_CONTAXY_SERVICE_URL
        ] = f"{settings.CONTAXY_BASE_URL}/projects/{project_id}/services/{deployment_id}/access/{endpoint}"

    if compute_resources:
        if compute_resources.max_gpus is not None and compute_resources.max_gpus > 0:
            # TODO: add logic to prevent overcommitting of GPUs!
            default_environment_variables["NVIDIA_VISIBLE_DEVICES"] = str(
                compute_resources.max_gpus
            )

        if compute_resources.max_volume_size is not None:
            default_environment_variables["CONTAXY_MAX_VOLUME_SIZE_MB"] = str(
                compute_resources.max_volume_size
            )

    return default_environment_variables


def replace_template_string(
    input: str = "", templates_mapping: Dict[str, str] = {}
) -> str:
    """Return the input with replaced value according to the templates mapping.

    For example, if `template = "{env.CONTAXY_BASE_URL}"` and `values = { "{env.CONTAXY_BASE_URL}": "some-value" } }`, the result will be
    `"some-value"`

    Args:
        input (str): The string that should be checked against the values dict and probably replaced by a match.
        templates_mapping (Dict[str, str]): The dict that contains template-strings with corresponding values.

    Returns:
        str: The string with the replaced value or the unmodified string in case of no match.
    """

    modified_input = input
    for key, value in templates_mapping.items():
        modified_input = modified_input.replace(key, value)

    return modified_input
    # if input in templates_mapping:
    #     return templates_mapping[input]
    # return input


def replace_templates(
    input: Dict[str, str] = {}, template_mapping: Dict[str, str] = {}
) -> Dict[str, str]:
    """Returns the input dict where those values that are matching template strings are replaced.

    Args:
        input (Dict[str, str]): The input dict for which the values should be checked for matching template replacements.
        templates_mapping (Dict[str, str]): The dict that contains template-strings with corresponding values.

    Returns:
        Dict[str, str]: A copy of the modified input dict where the template literals are replaced.
    """

    modified_input = {}

    for key, value in input.items():
        modified_input[key] = replace_template_string(
            input=value, templates_mapping=template_mapping
        )

    return modified_input


def get_template_mapping(
    project_id: Optional[str] = None,
    user_id: Optional[str] = None,
    environment: Dict[str, str] = None,
) -> Dict[str, str]:
    template_mapping = {}

    if settings.CONTAXY_BASE_URL:
        template_mapping[
            f"{{env.{_ENV_VARIABLE_CONTAXY_BASE_URL}}}"
        ] = settings.CONTAXY_BASE_URL

    if settings.CONTAXY_API_ENDPOINT:
        template_mapping[
            f"{{env.{_ENV_VARIABLE_CONTAXY_API_ENDPOINT}}}"
        ] = settings.CONTAXY_API_ENDPOINT

    if project_id:
        template_mapping["{env.projectId}"] = project_id

    if user_id:
        template_mapping["{env.userId}"] = user_id

    if environment:
        for env_name, env_value in environment.items():
            template_mapping[f"{{env.{env_name}}}"] = env_value

    return template_mapping


def split_image_name_and_tag(full_image_name: str) -> Tuple[str, str]:
    last_colon_position = full_image_name.rfind(":")
    # If there is no colon then to tag is given and the default is "latest"
    if last_colon_position == -1:
        return full_image_name, "latest"
    # If there is a colon but it comes before a / then it's part of the host (port separator)
    if last_colon_position < full_image_name.rfind("/"):
        return full_image_name, "latest"
    return (
        full_image_name[:last_colon_position],
        full_image_name[last_colon_position + 1 :],
    )
