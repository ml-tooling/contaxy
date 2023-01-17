from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi import Path
from pydantic import BaseModel, ByteSize, Field

from contaxy.schema.shared import Resource, ResourceInput

FILE_KEY_REGEX = r"^(?!.*(\r|\n|\.\.)).{1,1024}$"  # no new lines or consecutive dots

FILE_KEY_PARAM = Path(
    ...,
    title="File Key",
    example="datasets/customer-table.csv",
    description="A valid file key.",
    regex=FILE_KEY_REGEX,
    min_length=1,
    max_length=1024,
)


class FileStream(ABC):
    @property
    @abstractmethod
    def hash(self) -> str:
        pass

    @abstractmethod
    def read(self, size: int = -1) -> bytes:
        pass


class FileBase(BaseModel):
    pass
    # TODO: v2
    # content_encoding: Specifies what content encodings have been applied to the object and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field.
    # content_disposition: Specifies presentational information for the object.
    # content_language: The language the content is in.


class FileInput(ResourceInput, FileBase):
    pass


class File(Resource, FileBase):
    key: str = Field(
        ...,
        example="datasets/customer-table.csv",
        description="The (virtual) path of the file. This path might not correspond to the actual path on the file storage.",
        min_length=1,
        max_length=1024,  # Keys can only be 1024 chars long
        regex=FILE_KEY_REGEX,
    )
    content_type: str = Field(
        "",
        example="text/csv",
        description="A standard MIME type describing the format of the contents. If an file is stored without a Content-Type, it is served as application/octet-stream.",
    )
    external_id: Optional[str] = Field(
        None,
        example="datasets/customer-table.csv",
        description="The ID (or access instruction) of the file on the file storage provider.",
    )
    file_extension: str = Field(
        "",
        example="csv",
        description="The full file extension extracted from the key field. May contain multiple concatenated extensions, such as `tar.gz`.",
    )
    file_size: ByteSize = Field(
        ByteSize(0),
        example=1073741824,
        description="The file size in bytes.",
    )
    version: str = Field(
        ...,
        example="1614204512210009",
        description="Version tag of this file. The version order might not be inferable from the version tag.",
    )
    available_versions: List[str] = Field(
        [],
        example=["1614204512210009", "23424512210009", "6144204512210009"],
        description="All version tags available for the given file.",
    )
    latest_version: bool = Field(
        ...,
        example=True,
        description="Indicates if this is the latest available version of the file.",
    )
    md5_hash: Optional[str] = Field(
        None,
        example="2a53375ff139d9837e93a38a279d63e5",
        description="The base64-encoded 128-bit MD5 digest of the file. This can be used for checking the file integrity.",
    )
    etag: Optional[str] = Field(
        None,
        example="57f456164b0e5f365aaf9bb549731f32-95",
        description="The etag of the file (mainly used by S3 storage). An entity-tag is an opaque validator for differentiating between multiple representations of the same resource",
    )
    extension_id: Optional[str] = Field(
        None,
        description="The extension ID in case the file is provided via an extension.",
    )
