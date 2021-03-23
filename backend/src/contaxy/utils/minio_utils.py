from loguru import logger
from minio import Minio
from minio.error import S3Error
from minio.versioningconfig import ENABLED, VersioningConfig
from urllib3.exceptions import MaxRetryError

from contaxy.config import Settings
from contaxy.schema.exceptions import ServerBaseError


def get_bucket_name(project_id: str, prefix: str) -> str:
    return project_id if not prefix else f"{prefix}.{project_id}"


def create_minio_client(settings: Settings) -> Minio:
    client = Minio(
        endpoint=settings.S3_ENDPOINT,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        region=settings.S3_REGION,
        secure=settings.S3_SECURE,
    )

    try:
        if not client.bucket_exists("nonexistingbucket"):
            logger.debug("Object storage connected")
    except (MaxRetryError, S3Error):
        logger.critical(
            f"Could not connect to object storage (endpoint: {settings.S3_ENDPOINT}, region: {settings.S3_REGION}, secure: {settings.S3_SECURE})."
        )
        raise ServerBaseError(
            "Could not connect to object storage. Check S3 endpoint configuration."
        )
    return client


def delete_bucket(client: Minio, bucket_name: str) -> None:
    pass


def create_bucket(
    client: Minio,
    bucket_name: str,
    versioning_enabled: bool = True,
) -> None:
    """Create a bucket in the object storage configured by the client.

    Args:
        client (Minio): The initilaized Minio client.
        bucket_name (str): Bucket name.
        versioning_enabled (bool, optional): Controls bucket versioning. Defaults to True.

    Raises:
        ServerBaseError: If the desired action could not be performed.
    """
    # TODO: Handle Errors
    try:
        client.make_bucket(bucket_name)
        logger.debug(f"Bucket {bucket_name} created.")
    except S3Error as err:
        if err.code == "BucketAlreadyOwnedByYou":
            logger.info(f"The bucket {bucket_name} already exists and is owned by you.")
        else:
            logger.error(
                f"Could not create create the bucket {bucket_name} for an unknown reason."
            )
            raise ServerBaseError(f"Could not create create the bucket {bucket_name}.")

    if versioning_enabled:
        # TODO: Add handling if versioning could not be enabled
        try:
            client.set_bucket_versioning(bucket_name, VersioningConfig(ENABLED))
        except S3Error as err:
            msg = ""
            if err.code == "NotImplemented":
                msg = f"Versioning could not be enabled on the bucket {bucket_name}. Ensure that the object storage is configured with versioning enabled."
            else:
                msg = f"Versioning could not be enabled on the bucket {bucket_name} for an unknown reason."

            logger.critical(msg)
            delete_bucket(client, bucket_name)
            raise ServerBaseError(msg)
