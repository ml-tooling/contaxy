from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from fastapi import Path
from pydantic import BaseModel, Field

from contaxy.schema.shared import Resource, ResourceInput

SERVICE_ID_PARAM = Path(
    ...,
    title="Service ID",
    description="A valid Service ID.",
    # TODO: add length restriction
)

JOB_ID_PARAM = Path(
    ...,
    title="Job ID",
    description="A valid job ID.",
    # TODO: add length restriction
)


class DeploymentType(str, Enum):
    CORE_BACKEND = "core-backend"
    SERVICE = "service"
    JOB = "job"
    EXTENSION = "extension"


class DeploymentStatus(str, Enum):
    # Deployment created, but not ready for usage
    PENDING = "pending"  # Alternative naming: waiting
    # Deployment is running and usable
    RUNNING = "running"
    # Deployment was stopped with successful exit code (== 0).
    SUCCEEDED = "succeeded"
    # Deployment was stopped with failure exit code (> 0).
    FAILED = "failed"
    # Deployment state cannot be obtained.
    UNKNOWN = "unknown"
    # Deployment is paused (only on docker?)/
    # PAUSED = "paused"
    # Other possible options:
    # KILLED = "killed"
    # STARTING("starting"),
    # STOPPPED("stopped"),
    # CREATED("created"),
    # REBOOTING
    # TERMINATED: Container is terminated. This container can’t be started later on.
    # STOPPED:  Container is stopped. This container can be started later on.
    # ERROR – Container is an error state. Usually no operations can be performed on the container once it ends up in the error state.
    # SUSPENDED: Container is suspended.


class DeploymentCompute(BaseModel):
    min_cpus: Optional[int] = Field(
        None,
        example=2,
        ge=0,
        description="Minimum number of CPU cores required by this deployment. The system will make sure that atleast this amount is available to the deployment.",
    )
    max_cpus: Optional[int] = Field(
        None,
        example=4,
        ge=0,
        description="Maximum number of CPU cores. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more. 0 means unlimited.",
    )
    min_memory: Optional[int] = Field(
        None,
        example=4000,
        ge=5,  # 4 is the minimal RAM needed for containers
        description="Minimum amount of memory in Megabyte required by this deployment. The system will make sure that atleast this amount is available to the deployment.",
    )
    max_memory: Optional[int] = Field(
        None,
        example=8000,
        ge=0,
        description="Maximum amount of memory in Megabyte. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more. 0 means unlimited.",
    )  # in MB
    min_gpus: Optional[int] = Field(
        None,
        example=1,
        ge=0,
        description="Minimum number of GPUs required by this deployments. The system will make sure that atleast this amount is available to the deployment.",
    )
    max_gpus: Optional[int] = Field(
        None,
        example=2,
        ge=0,
        description="Maximum number of GPUs. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more.",
    )
    volume_path: Optional[str] = Field(
        None,
        example="/path/to/data",
        description="Container internal directory that should mount a volume for data persistence.",
    )
    # TODO: min_volume_size
    max_volume_size: Optional[int] = Field(
        None,
        example=32000,
        ge=1,
        description="Maximum volume size in Megabyte. This is only applied in combination with volume_path.",
    )
    # TODO: min_container_size
    max_container_size: Optional[int] = Field(
        None,
        example=32000,
        ge=1,
        description="Maximum container size in Megabyte. The deployment will be killed if it grows above this limit.",
    )
    # TODO: min_replicas
    max_replicas: Optional[int] = Field(
        1,
        example=2,
        ge=1,
        description="Maximum number of deployment instances. The system will make sure to optimize the deployment based on the available resources and requests. Use 1 if the deployment is not scalable.",
    )
    # TODO: use timedelta
    min_lifetime: Optional[int] = Field(
        None,
        example=86400,
        description="Minimum guaranteed lifetime in seconds. Once the lifetime is reached, the system is allowed to kill the deployment in case it requires additional resources.",
    )


class DeploymentBase(BaseModel):
    container_image: str = Field(
        ...,
        example="hello-world:latest",
        max_length=2000,
        description="The container image used for this deployment.",
    )
    parameters: Optional[Dict[str, str]] = Field(
        None,
        example={"TEST_PARAM": "param-value"},
        description="Parmeters (enviornment variables) for this deployment.",
    )
    compute: Optional[DeploymentCompute] = Field(
        None,
        description="Compute instructions and limitations for this deployment.",
    )
    command: Optional[str] = Field(
        None,
        description="Command to run within the deployment. This overwrites the existing entrypoint.",
    )
    requirements: Optional[List[str]] = Field(
        None,
        description="Additional requirements for deployment.",
    )
    endpoints: Optional[List[str]] = Field(
        None,
        example=["8080", "9001/webapp/ui", "9002b"],
        description="A list of HTTP endpoints that can be accessed. This should always have an internal port and can include additional instructions, such as the URL path.",
    )
    # TODO: v2
    # input_files: Optional[List[dict]] = Field(
    #    None,
    #    description="A list of files that should be added to the deployment.",
    # )
    # TODO: v2
    # command_args: Optional[List[str]] = Field(
    #    None,
    #    description="Arguments to use for the command of the deployment. This overwrites the existing arguments.",
    # )


class DeploymentInput(ResourceInput, DeploymentBase):
    pass


class Deployment(Resource, DeploymentBase):
    started_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the deployment was started.",
    )
    stopped_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the container has stopped.",
    )
    extension_id: Optional[str] = Field(
        None,
        description="The extension ID in case the deployment is deployed via an extension.",
    )
    deployment_type: Optional[DeploymentType] = Field(
        None,
        description="The type of this deployment.",
    )
    status: Optional[DeploymentStatus] = Field(
        None,
        example=DeploymentStatus.RUNNING,
        description="The status of this deployment.",
    )
    internal_id: Optional[str] = Field(
        None,
        example="73d247087fea5bfb3a67e98da6a07f5bf4e2a90e5b52f3c12875a35600818376",
        description="The ID of the deployment on the orchestration platform.",
    )
    # TODO: All labels should be transformed into the metadata or additional_metadata
    # deployment_labels: Optional[Dict[str, str]] = Field(
    #    None,
    #    example={"foo.bar.label": "label-value"},
    #    description="The labels of the deployment on the orchestration platform.",
    # )
    # TODO: should be a debug information.
    # exit_code: Optional[int] = Field(
    #    None,
    #    example=0,
    #    description="The Exit code of the container, in case the container was stopped.",
    # )


class ServiceBase(BaseModel):
    graphql_endpoint: Optional[str] = Field(
        None,
        example="8080/graphql",
        description="GraphQL endpoint.",
    )
    openapi_endpoint: Optional[str] = Field(
        None,
        example="8080/openapi.yaml",
        description="Endpoint that prorvides an OpenAPI schema definition..",
    )
    health_endpoint: Optional[str] = Field(
        None,
        example="8080/healthz",
        description="The endpoint instruction that can be used for checking the deployment health.",
    )


class ServiceInput(ServiceBase, DeploymentInput):
    pass


class Service(ServiceBase, Deployment):
    pass


class JobBase(BaseModel):
    pass


class JobInput(JobBase, DeploymentInput):
    pass
    # TODO: v2
    # output_files: Optional[List[dict]] = Field(
    #    None,
    #    description="A list of container internal files that should be uploaded to the storage once the job has succeeded.",
    # )


class Job(JobBase, Deployment):
    pass
