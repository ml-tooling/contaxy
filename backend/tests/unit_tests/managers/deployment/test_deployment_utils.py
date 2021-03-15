import pytest

from contaxy.config import settings
from contaxy.managers.deployment import deployment_utils
from contaxy.schema.deployment import DeploymentType


@pytest.mark.parametrize(
    "project_id,deployment_name,deployment_type,expected_id",
    [
        (
            "my-project",
            "Foo Bar Service",
            DeploymentType.SERVICE,
            settings.SYSTEM_NAMESPACE + "-p-my-project-s-foo-bar-service",
        ),
        (
            "my-project",
            "Foo Bar Job",
            DeploymentType.JOB,
            settings.SYSTEM_NAMESPACE + "-p-my-project-j-foo-bar-job",
        ),
    ],
)
def test_get_deployment_id(
    project_id: str,
    deployment_name: str,
    deployment_type: DeploymentType,
    expected_id: str,
) -> None:
    deployment_id = deployment_utils.get_deployment_id(
        project_id, deployment_name, deployment_type
    )
    assert deployment_id == expected_id
    # The deployment id should be always under 63 chars
    assert len(deployment_id) <= 63

    # TODO check if the id is DNS conform...
