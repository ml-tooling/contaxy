import pytest

from contaxy.config import settings
from contaxy.managers.deployment import utils
from contaxy.managers.deployment.utils import split_image_name_and_tag
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
@pytest.mark.unit
def test_get_deployment_id(
    project_id: str,
    deployment_name: str,
    deployment_type: DeploymentType,
    expected_id: str,
) -> None:
    deployment_id = utils.get_deployment_id(
        project_id, deployment_name, deployment_type
    )
    assert deployment_id == expected_id
    # The deployment id should be always under 63 chars
    assert len(deployment_id) <= 63

    # TODO check if the id is DNS conform...


@pytest.mark.parametrize(
    "image_full_name,expected_image_name,expected_image_tag",
    [
        (
            "my-image",
            "my-image",
            "latest",
        ),
        (
            "my-image:0.2.2",
            "my-image",
            "0.2.2",
        ),
        (
            "my-host.com/my-image:1-1",
            "my-host.com/my-image",
            "1-1",
        ),
        (
            "my-host.com:8080/my-image:1-1",
            "my-host.com:8080/my-image",
            "1-1",
        ),
        (
            "my-host.com:8080/my-image",
            "my-host.com:8080/my-image",
            "latest",
        ),
    ],
)
@pytest.mark.unit
def test_split_image_name_and_tag(
    image_full_name: str,
    expected_image_name: str,
    expected_image_tag: str,
):
    assert split_image_name_and_tag(image_full_name) == (
        expected_image_name,
        expected_image_tag,
    )
