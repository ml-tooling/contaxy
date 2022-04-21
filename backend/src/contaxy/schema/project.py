from datetime import datetime
from typing import Optional

from fastapi import Path
from pydantic import BaseModel, Field

from contaxy.schema.shared import Resource, ResourceInput

PROJECTS_KIND = "projects"

MIN_PROJECT_ID_LENGTH = 4
MAX_PROJECT_ID_LENGTH = 25

PROJECT_ID_PARAM = Path(
    ...,
    title="Project ID",
    example="image-search-engine",
    description="A valid project ID.",
    min_length=MIN_PROJECT_ID_LENGTH,
    max_length=MAX_PROJECT_ID_LENGTH,
)


class Quota(BaseModel):
    max_cpus: Optional[int] = Field(
        None,
        example=52,
        ge=0,
        description="Maximum number of CPU cores.",
    )
    max_memory: Optional[int] = Field(
        None,
        example=80000,
        ge=0,
        description="Maximum amount of memory in Megabyte.",
    )
    max_gpus: Optional[int] = Field(
        None,
        example=8,
        ge=0,
        description="Maximum number of GPUs.",
    )
    max_deployment_storage: Optional[int] = Field(
        None,
        example=800000,
        ge=0,
        description="Maximum storage usage in Megabyte for all deployments.",
    )
    max_file_storage: Optional[int] = Field(
        None,
        example=100000,
        ge=0,
        description="Maximum storage usage in Megabyte for all files.",
    )
    max_files: Optional[int] = Field(
        None,
        example=1000,
        ge=0,
        description="Maximum number of files on file storage.",
    )
    max_deployments: Optional[int] = Field(
        None,
        example=20,
        ge=0,
        description="Maximum number of deployments. This includes services, jobs, and extensions.",
    )
    max_collections: Optional[int] = Field(
        None,
        example=20,
        ge=0,
        description="Maximum number of JSON document collections.",
    )


class ProjectBase(BaseModel):
    # TODO: add quota
    # quota: Optional[Quota] = Field(
    #    None,
    #    description="Limitations for resource usage.",
    # )
    pass


class ProjectInput(ResourceInput, ProjectBase):
    pass


class ProjectCreation(ProjectInput):
    id: str = Field(
        ...,
        example="my-awesome-project",
        description="Project ID used for creating the project.",
        min_length=MIN_PROJECT_ID_LENGTH,
        max_length=MAX_PROJECT_ID_LENGTH,
    )


class Project(Resource, ProjectBase):
    technical_project: Optional[bool] = Field(
        False,
        description="Indicates that this is a technical project created by the system.",
    )
    # TODO: v2
    # statistics: Optional[Statistics] = Field(
    #    None,
    #    description="Project statistics.",
    # )


class Statistics(BaseModel):
    cpus: Optional[int] = Field(
        None,
        ge=0,
        example=32,
        description="Number of CPU cores requested by active deployments.",
    )
    memory: Optional[int] = Field(
        None,
        ge=0,
        example=60000,
        description="Amount of memory in Megabyte requested by active deployments.",
    )
    gpus: Optional[int] = Field(
        None,
        ge=0,
        example=8,
        description="Number of GPUs requested by active deployments.",
    )
    deployment_storage: Optional[int] = Field(
        None,
        ge=0,
        example=400000,
        description="Storage usage in Megabyte for all deployments.",
    )
    file_storage: Optional[int] = Field(
        None,
        ge=0,
        example=50000,
        description="Storage usage in Megabyte for all files.",
    )
    files: Optional[int] = Field(
        None,
        example=320,
        ge=0,
        description="Number of files on file storage.",
    )
    deployments: Optional[int] = Field(
        None,
        example=10,
        ge=0,
        description="Number of deployments. This includes services, jobs, and extensions.",
    )
    collections: Optional[int] = Field(
        None,
        example=10,
        ge=0,
        description="Number of JSON document collections.",
    )
    last_activity: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="The last activity based on events.",
    )
