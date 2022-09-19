from enum import Enum
from typing import Dict, List, Optional

from fastapi import Query
from pydantic import BaseModel, Field, validator


class SystemState(str, Enum):
    UNINITIALIZED = "uninitialized"
    RUNNING = "running"


class SystemInfo(BaseModel):
    version: str = Field(
        ...,
        example="0.1.0",
        description="Platform version.",
    )
    # TODO: orchestrator or other selected settings
    namespace: str = Field(
        ...,
        example="mlhub",
        description="Namespace of this system.",
    )
    system_state: SystemState = Field(..., description="The state of the system.")
    metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata associated with this system.",
    )


class SystemStatistics(BaseModel):
    # TODO: finish model
    project_count: int
    user_count: int
    job_count: int
    service_count: int
    file_count: int


class AllowedImageInfo(BaseModel):
    image_name: str = Field(
        ...,
        example="my-docker-registry.com/my-image",
        description="Name of the docker image to allow. Do not specify the image tag (the part after the colon)",
    )
    image_tags: List[str] = Field(
        ...,
        example=["0.2.1", "0.3.0"],
        description='List of tags that are allowed for this image. Can be set to ["*"] to allow all tags.',
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="A collection of arbitrary key-value pairs associated with this image that does not need predefined structure.",
    )

    @validator("image_name", pre=True)
    def ensure_lowercase(cls, value: str) -> str:
        return value.lower()


IMAGE_NAME_PARAM = Query(
    ...,
    title="Docker image name",
    description="Name of a docker image without the tag",
)
