from typing import Optional

from minio import Minio
from minio.versioningconfig import ENABLED, VersioningConfig


def create_bucket(
    client: Minio,
    bucket_name: str,
    region: Optional[str] = None,
    versioning_enabled: bool = True,
) -> None:
    """Create a object storage bucket.

    Args:
        client (Minio): The initilaized Minio client.
        bucket_name (str): Bucket name.
        region (Optional[str], optional): The region. Defaults to None.
        versioning_enabled (bool, optional): Controls bucket versioning. Defaults to True.
    """
    client.make_bucket(bucket_name, region)
    if versioning_enabled:
        client.set_bucket_versioning(bucket_name, VersioningConfig(ENABLED))
