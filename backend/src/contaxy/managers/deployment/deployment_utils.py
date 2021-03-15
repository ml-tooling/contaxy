import string

from contaxy.schema.deployment import DeploymentType
from contaxy.utils import id_utils

_MAX_DEPLOYMENT_NAME_LENGTH = 15

_SERVICE_ID_SEPERATOR = "-s-"
_JOB_ID_SEPERATOR = "-j-"


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
