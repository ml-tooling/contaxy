from random import randint

import pytest
from minio import Minio
from minio.commonconfig import ENABLED

from contaxy.config import Settings, settings
from contaxy.schema.exceptions import ServerBaseError
from contaxy.utils.minio_utils import (
    create_bucket,
    create_minio_client,
    delete_bucket,
    get_bucket_name,
)
from tests.unit_tests.conftest import test_settings


# TODO:
@pytest.fixture(scope="session")
def minio_client() -> Minio:
    return create_minio_client(settings)


@pytest.mark.skipif(
    not test_settings.MINIO_INTEGRATION_TESTS,
    reason="Minio Integration Tests are deactivated, use MINIO_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestMinioUtils:
    def test_create_client(self) -> None:
        client = create_minio_client(settings)
        assert client
        try:
            invalid_settings = Settings()
            invalid_settings.S3_ENDPOINT = "invalid"
            create_minio_client(invalid_settings)
            assert False
        except ServerBaseError:
            pass

        try:
            invalid_settings = Settings()
            invalid_settings.S3_SECRET_KEY = "invalid"
            create_minio_client(invalid_settings)
            assert False
        except ServerBaseError:
            pass

    def test_bucket_management(self, minio_client: Minio) -> None:
        project_id = f"{randint(1,10000)}-minio-utils-test"
        bucket_name = get_bucket_name(project_id, settings.SYSTEM_NAMESPACE)
        create_bucket(minio_client, bucket_name)
        assert minio_client.bucket_exists(bucket_name)
        config = minio_client.get_bucket_versioning(bucket_name)
        assert config.status == ENABLED

        create_bucket(minio_client, bucket_name)

        delete_bucket(minio_client, bucket_name)

        delete_bucket(minio_client, bucket_name)
