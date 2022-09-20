from datetime import datetime, timedelta
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
    UNKNOWN = "unknown"


class DeploymentStatus(str, Enum):
    # Deployment created, but not ready for usage
    PENDING = "pending"  # Alternative naming: waiting
    # Deployment is running and usable
    RUNNING = "running"
    # Deployment was stopped with successful exit code (== 0).
    SUCCEEDED = "succeeded"
    # Deployment was stopped with failure exit code (> 0).
    FAILED = "failed"
    # Deployment was deleted and is now terminating the pods.
    TERMINATING = "terminating"
    # Deployment is stopped (it still exists in the DB but no container is running)
    STOPPED = "stopped"
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
    min_cpus: Optional[float] = Field(
        1,
        example=2,
        ge=0,
        description="Minimum number of CPU cores required by this deployment. The system will make sure that atleast this amount is available to the deployment.",
    )
    max_cpus: Optional[float] = Field(
        None,
        example=4,
        ge=0,
        description="Maximum number of CPU cores. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more. 0 means unlimited.",
    )
    min_memory: Optional[int] = Field(
        1000,
        example=4000,
        ge=4,  # 4 is the minimal RAM needed for containers
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
    max_replicas: int = Field(
        1,
        example=2,
        ge=1,
        description="Maximum number of deployment instances. The system will make sure to optimize the deployment based on the available resources and requests. Use 1 if the deployment is not scalable.",
    )
    # TODO: use timedelta
    min_lifetime: int = Field(
        0,
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
    parameters: Dict[str, str] = Field(
        {},
        example={"TEST_PARAM": "param-value"},
        description="Parameters (environment variables) for this deployment.",
    )
    compute: DeploymentCompute = Field(
        DeploymentCompute(),
        description="Compute instructions and limitations for this deployment.",
    )
    command: Optional[List[str]] = Field(
        None,
        description="Command to run within the deployment. This overwrites the existing docker ENTRYPOINT.",
    )
    args: Optional[List[str]] = Field(
        None,
        description="Arguments to the command/entrypoint. This overwrites the existing docker CMD.",
    )
    requirements: List[str] = Field(
        [],
        description="Additional requirements for deployment.",
    )
    endpoints: List[str] = Field(
        [],
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
    deployment_type: DeploymentType = Field(
        DeploymentType.UNKNOWN,
        description="The type of this deployment.",
    )
    status: DeploymentStatus = Field(
        DeploymentStatus.UNKNOWN,
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
    idle_timeout: Optional[timedelta] = Field(
        None,
        description="Time after which the service is considered idling and will be stopped during the next idle check."
        "If set to None, the service will never be considered idling."
        "Can be specified as seconds or ISO 8601 time delta.",
    )
    clear_volume_on_stop: bool = Field(
        False,
        description="If set to true, any volume attached to the service be deleted when the service is stopped."
        "This means all persisted data will be cleared on service stop.",
    )


class ServiceInput(ServiceBase, DeploymentInput):
    is_stopped: bool = Field(
        False,
        description="If set to true, the service will be created in the DB but not started. The service status will be 'stopped'.",
    )


class ServiceUpdate(ServiceInput):
    # Add default value for container_image so it is not required to be set in an update request
    container_image: str = Field(
        "",
        example="hello-world:latest",
        max_length=2000,
        description="The container image used for this deployment.",
    )
    # Allow None for parameters and metadata values so they can be completely removed in an update request
    parameters: Dict[str, Optional[str]] = Field(  # type: ignore[assignment]
        {},
        example={"TEST_PARAM": "param-value"},
        description="Parmeters (enviornment variables) for this deployment.",
    )
    metadata: Dict[str, Optional[str]] = Field(  # type: ignore[assignment]
        {},
        example={"additional-metadata": "value"},
        description="A collection of arbitrary key-value pairs associated with this resource that does not need predefined structure. Enable third-party integrations to decorate objects with additional metadata for their own use.",
    )


class Service(ServiceBase, Deployment):
    # Store the last time this service was accessed and by which user
    last_access_time: Optional[datetime] = Field(
        None, description="Timestamp of the last time the service was accessed."
    )
    last_access_user: Optional[str] = Field(
        None, description="Id of the user that last accessed the service."
    )


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


ACTION_DELIMITER = "-"
ACTION_ACCESS = "access"
ACTION_START = "start"
ACTION_STOP = "stop"
ACTION_RESTART = "restart"
