from loguru import logger
from minio import Minio
from minio.deleteobjects import DeleteObject
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


def purge_bucket(client: Minio, bucket_name: str) -> None:
    # TODO: Validate the effect of `bypass_governance_mode`
    delete_object_list = [
        DeleteObject(file.object_name, file.version_id)
        for file in client.list_objects(
            bucket_name, include_version=True, recursive=True
        )
    ]

    if delete_object_list:
        try:
            errors = client.remove_objects(bucket_name, delete_object_list)
            for error in errors:
                print("error occured when deleting object", error)
        except BaseException as err:
            pass


def delete_bucket(client: Minio, bucket_name: str, force: bool = False) -> None:
    try:
        client.remove_bucket(bucket_name)
    except S3Error as err:
        if err.code == "NoSuchBucket":
            logger.info(f"Bucket {bucket_name} not deleted, since it does not exist.")
        elif err.code == "BucketNotEmpty":
            if force:
                purge_bucket(client, bucket_name)
            else:
                msg = (
                    f"Bucket {bucket_name} can not be deleted because it is not empty."
                )
                logger.error(msg)
                raise ServerBaseError(msg)
        else:
            raise ServerBaseError(
                f"The bucket {bucket_name} could not be deleted ({err.code})."
            )


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
    try:
        client.make_bucket(bucket_name)
        logger.info(f"Bucket {bucket_name} created.")
    except S3Error as err:
        if err.code == "BucketAlreadyOwnedByYou":
            logger.info(f"The bucket {bucket_name} already exists and is owned by you.")
        else:
            logger.error(
                f"Could not create create the bucket {bucket_name} for an unknown reason."
            )
            raise ServerBaseError(f"Could not create create the bucket {bucket_name}.")

    if versioning_enabled:
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
