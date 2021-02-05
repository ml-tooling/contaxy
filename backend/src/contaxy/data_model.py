from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import (
    UUID4,
    BaseModel,
    ByteSize,
    EmailStr,
    Field,
    PositiveInt,
    SecretStr,
    constr,
)

MIN_DISPLAY_NAME_LENGTH = 4
MAX_DISPLAY_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 240
MIN_PROJECT_ID_LENGTH = 4
MAX_PROJECT_ID_LENGTH = 25


class CoreOperations(str, Enum):
    # TODO: LIST API TOKENS
    # LIST_PROJECT_API_TOKENS = "list_user_api_tokens"
    # LIST_USER_API_TOKENS = "list_user_api_tokens"

    # Project Endpoints
    LIST_PROJECTS = "list_projects"
    CREATE_PROJECT = "create_project"
    GET_PROJECT = "get_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    GET_PROJECT_TOKEN = "get_project_token"
    SUGGEST_PROJECT_ID = "suggest_project_id"
    LIST_PROJECT_MEMBERS = "list_project_members"
    ADD_PROJECT_MEMBER = "add_project_member"
    REMOVE_PROJECT_MEMBER = "remove_project_member"
    # User Endpoints
    LIST_USERS = "list_users"
    GET_USER = "get_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    GET_USER_TOKEN = "get_user_token"
    # Auth Endpoints
    REFRESH_TOKEN = "refresh_token"
    VERIFY_TOKEN = "verify_token"
    # Extension Endpoints
    INSTALL_EXTENSION = "install_extension"
    LIST_EXTENSIONS = "list_extensions"
    GET_EXTENSION_METADATA = "get_extension_metadata"
    DELETE_EXTENSION = "delete_extension"
    SUGGEST_EXTENSION_CONFIG = "suggest_extension_config"
    SET_EXTENSION_DEFAULTS = "set_extension_defaults"
    GET_EXTENSION_DEFAULTS = "get_extension_defaults"
    # System Endpoints
    GET_SYSTEM_INFO = "get_system_info"
    GET_SYSTEM_STATISTICS = "get_system_statistics"
    LIST_SYSTEM_NODES = "list_system_nodes"
    # TODO: Implement get_system_events


class ExtensibleOperations(str, Enum):
    # Service Endpoints
    LIST_SERVICES = "list_services"
    GET_SERVICE_METADATA = "get_service_metadata"
    LIST_SERVICE_DEPLOY_OPTIONS = "list_service_deploy_options"
    DEPLOY_SERVICE = "deploy_service"
    DELETE_SERVICE = "delete_service"
    UPDATE_SERVICE = "update_service"
    GET_SERVICE_LOGS = "get_service_logs"
    GET_SERVICE_ACCESS_TOKEN = "get_service_access_token"
    LIST_OPEN_SERVICE_ACTIONS = "list_open_service_actions"
    SUGGEST_SERVICE_CONFIG = "suggest_service_config"
    OPEN_SERVICE = "open_service"
    # Job Endpoints
    LIST_JOBS = "list_jobs"
    GET_JOB_METADATA = "get_job_metadata"
    LIST_JOB_DEPLOY_OPTIONS = "list_job_deploy_options"
    SUGGEST_JOB_CONFIG = "suggest_job_config"
    DEPLOY_JOB = "deploy_job"
    DELETE_JOB = "delete_job"
    GET_JOB_LOGS = "get_job_logs"
    # File Endpoints
    LIST_FILES = "list_files"
    GET_FILE_METADATA = "get_file_metadata"
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    LIST_OPEN_FILE_ACTIONS = "list_open_file_actions"
    OPEN_FILE = "open_file"
    DELETE_FILE = "delete_file"
    GET_FILE_ACCESS_TOKEN = "get_file_access_token"
    UPDATE_FILE_METADATA = "update_file_metadata"
    # Auth Endpoints
    OPEN_LOGIN_PAGE = "open_login_page"
    LIST_API_TOKENS = "list_api_tokens"
    DELETE_API_TOKEN = "delete_api_token"


class DeploymentType(str, Enum):
    SERVICE = "service"
    JOB = "job"
    EXTENSION = "extension"


class ExtensionType(str, Enum):
    USER_EXTENSION = "user-extension"
    PROJECT_EXTENSION = "project-extension"


class TechnicalProject(str, Enum):
    SYSTEM_INTERNAL = "system-internal"  # only admin access
    SYSTEM_GLOBAL = "system-global"  # services are accesible to all users, but the service needs to set the service session token by itself


class DeploymentRequirement(str, Enum):
    DOCKER_SOCKET = "docker-socket"
    KUBECTL = "kubectl"
    NVIDIA_GPU = "nvidia-gpu"


class TokenType(str, Enum):
    SESSION_TOKEN = "session-token"
    API_TOKEN = "api-token"


class ProjectRole(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"


class DataType(str, Enum):
    DATASET = "dataset"
    CONFIG = "config"
    MODEL = "model"
    OTHER = "other"


class ContainerOrchestrator(str, Enum):
    KUBERNETES = "kubernetes"
    DOCKER_LOCAL = "docker-local"


class DeploymentStatus(str, Enum):
    # Deployment created, but not ready for usage
    PENDING = "pending"
    # Deployment is running.
    RUNNING = "running"
    # Deployment is paused (only on docker?)/
    PAUSED = "paused"
    # Deployment was stopped with successful exit code (== 0).
    SUCCEEDED = "succeeded"
    # Deployment was stopped with failure exit code (> 0).
    FAILED = "failed"
    # Deployment state cannot be obtained.
    UNKNOWN = "unknown"
    # Other possible options:
    # KILLED = "killed"
    # STARTING("starting"),
    # STOPPPED("stopped"),
    # CREATED("created"),


class ActionInstruction(str, Enum):
    NEW_TAB = "new-tab"


class BaseEntity(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        underscore_attrs_are_private = True
        # TODO: should we set a max length for string to prevent to big requests?
        max_anystr_length = 20000


class UserIn(BaseEntity):
    username: str = Field(
        ...,
        example="john.doe@example.com",
        description="A unique username on the system.",
    )
    email: Optional[EmailStr] = Field(
        None, example="john.doe@example.com", description="User email address."
    )
    permissions: Optional[List[str]] = Field(
        None,
        example=["pm-image-search-engine"],
        description="List of user permissions.",
    )
    is_disabled: Optional[bool] = Field(
        False,
        description="Indicates that user is disabled.",
    )
    # password: Optional[SecretStr] = None


class User(UserIn):
    id: UUID4 = Field(
        ...,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="Unique ID of the user.",
    )
    is_technical_user: Optional[bool] = Field(
        False,
        description="Indicates if the user is a technical user created by the system.",
    )


class Quota(BaseEntity):
    max_cpus: Optional[PositiveInt] = Field(
        None,
        example=52,
        description="Maximum number of CPU cores.",
    )
    max_memory: Optional[PositiveInt] = Field(
        None,
        example=80000,
        description="Maximum amount of memory in Megabyte.",
    )
    max_gpus: Optional[int] = Field(
        None,
        example=8,
        ge=0,
        description="Maximum number of GPUs.",
    )
    max_deployment_storage: Optional[PositiveInt] = Field(
        None,
        example=800000,
        description="Maximum storage usage in Megabyte for all deployments.",
    )
    max_file_storage: Optional[PositiveInt] = Field(
        None,
        example=100000,
        description="Maximum storage usage in Megabyte for all files.",
    )
    max_files: Optional[PositiveInt] = Field(
        None,
        example=1000,
        description="Maximum number of files on file storage.",
    )
    max_deployments: Optional[PositiveInt] = Field(
        None,
        example=20,
        description="Maximum number of deployments. This includes services, jobs, and extensions.",
    )


class Statistics(BaseEntity):
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
        description="Number of files on file storage.",
    )
    deployments: Optional[int] = Field(
        None,
        example=10,
        description="Number of deployments. This includes services, jobs, and extensions.",
    )
    last_activity: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="The last activity based on events.",
    )


class ProjectIn(BaseEntity):
    # TODO: add validation regex
    id: str = Field(
        ..., example="image-search-engine", description="ID of the project."
    )
    display_name: str = Field(
        ...,
        min_length=MIN_DISPLAY_NAME_LENGTH,
        max_length=MAX_DISPLAY_NAME_LENGTH,
        example="Image Search Engine",
        description="Display name of the project. This can be changed after creation.",
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        example="Building an awesome image search engine.",
        description="Short description of this project. This can be changed after creation.",
    )
    icon: Optional[str] = Field(
        None,
        max_length=1000,
        example="search",
        description="Material Design Icon name or image URL used for displaying this project.",
    )
    additional_metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata for this project.",
    )
    quota: Optional[Quota] = Field(
        None,
        description="Limitations for resource usage.",
    )


class Project(ProjectIn):
    creation_date: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the project.",
    )
    modification_date: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the project metadata was modified.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has created this project.",
    )
    modified_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last modified this projects metadata.",
    )
    is_available: Optional[bool] = Field(
        False,
        description="Indicates that this project is ready for usage.",
    )
    is_technical_project: Optional[bool] = Field(
        False,
        description="Indicates that this is a technical project created by the system.",
    )
    statistics: Optional[Statistics] = Field(
        None,
        description="Indicates that this is a technical project created by the system.",
    )


class DeploymentCompute(BaseEntity):
    max_cpus: Optional[PositiveInt] = Field(
        None,
        example=4,
        description="Maximum number of CPU cores. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more.",
    )
    max_memory: Optional[PositiveInt] = Field(
        None,
        example=8000,
        description="Maximum amount of memory in Megabyte. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more.",
    )  # in MB
    max_gpus: Optional[int] = Field(
        None,
        example=2,
        ge=0,
        description="Maximum number of GPUs. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more.",
    )
    # TODO: allowed_gpu_types: Optional[List[str]] = None
    volume_path: Optional[Path] = Field(
        None,
        example="/path/to/data",
        description="Container internal directory that should mount a volume for data persistence.",
    )
    max_volume_size: Optional[PositiveInt] = Field(
        None,
        example=32000,
        description="Maximum volume size in Megabyte. This is only applied in combination with volume_path.",
    )
    max_container_size: Optional[PositiveInt] = Field(
        None,
        example=32000,
        description="Maximum container size in Megabyte. The deployment will be killed if it grows above this limit.",
    )
    max_replicas: Optional[PositiveInt] = Field(
        1,
        example=2,
        description="Maximum number of replicas. The system will make sure to optimize the deployment based on the available resources and requests. Use 1 if the deployment is not scalable.",
    )
    min_lifetime: Optional[timedelta] = Field(
        None,
        example=86400,
        description="Minimum guaranteed lifetime in seconds. Once the lifetime is reached, the system is allowed to kill the deployment in case it requires additional resources.",
    )


class DeploymentIn(BaseEntity):
    id: str = Field(...)
    container_image: Optional[str] = Field(
        None,
        example="hello-world:latest",
        max_length=2000,
        description="The container image used for this deployment.",
    )
    display_name: str = Field(
        ...,
        min_length=MIN_DISPLAY_NAME_LENGTH,
        max_length=MAX_DISPLAY_NAME_LENGTH,
        example="Hello World Example",
        description="Display name of the deployment.",
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        example="A hello world deployment just for some testing",
        description="Short description of this deployment.",
    )
    icon: Optional[str] = Field(
        None,
        example="search",
        max_length=1000,
        description="Material Design Icon name or image URL used for displaying this deployment.",
    )
    parameters: Optional[Dict[str, str]] = Field(
        None,
        example={"TEST_PARAM": "param-value"},
        description="Parmeters (enviornment variables) for this deployment.",
    )
    input_files: Optional[List[dict]] = Field(
        None,
        description="A list of files that should be added to the deployment.",
    )
    compute: Optional[DeploymentCompute] = Field(
        None,
        description="Compute instructions and limitations for this deployment.",
    )
    requirements: Optional[List[Union[DeploymentRequirement, str]]] = Field(
        None,
        description="Additional requirements for deployment.",
    )
    additional_metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata for this deployment.",
    )


class Deployment(DeploymentIn):
    started_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the deployment was started.",
    )
    stopped_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the container has stopped.",
    )
    extensions_id: Optional[str] = Field(
        None,
        description="The extension ID in case the deployment is deployed via an extension.",
    )
    type: Optional[DeploymentType] = Field(
        None,
        description="The type of this deployment.",
    )
    status: Optional[DeploymentStatus] = Field(
        None,
        example=DeploymentStatus.RUNNING,
        description="The status of this deployment.",
    )
    container_id: Optional[str] = Field(
        None,
        example="73d247087fea5bfb3a67e98da6a07f5bf4e2a90e5b52f3c12875a35600818376",
        description="The ID of the container on the orchestration platform.",
    )
    container_name: Optional[str] = Field(
        None,
        example="hello-world-app",
        description="The name of the container on the orchestration platform.",
    )
    container_labels: Optional[Dict[str, str]] = Field(
        None,
        example={"foo.bar.label": "label-value"},
        description="The labels of the container on the orchestration platform.",
    )
    exit_code: Optional[int] = Field(
        None,
        example=0,
        description="The Exit code of the container, in case the container was stopped.",
    )


class ServiceIn(DeploymentIn):
    endpoints: Optional[List[str]] = Field(
        None,
        example=["8080", "9001/webapp/ui", "9002b"],
        description="A list of HTTP endpoints that can be accessed. This should always have an internal port and can include additional instructions, such as the URL path.",
    )


class Service(Deployment, ServiceIn):
    health_endpoint: Optional[str] = Field(
        None,
        example="8080/healthz",
        description="The endpoint instruction that can be used for checking the deployment health.",
    )
    is_healthy: Optional[bool] = Field(
        True,
        description="Indicates if the deployment is healthy.",
    )


class JobIn(DeploymentIn):
    output_files: Optional[List[dict]] = Field(
        None,
        description="A list of container internal files that should be uploaded to the storage once the job has succeeded.",
    )


class Job(Deployment, JobIn):
    pass


class ExtensionIn(ServiceIn):
    capabilities: Optional[List[Union[ExtensibleOperations, str]]] = Field(
        None,
        # TODO: provide example
        description="List of capabilities implemented by this extension.",
    )
    # TODO: do not use ui or api endpoint -> use endpoints list instead and provide metadata there
    ui_endpoint: Optional[str] = Field(
        None,
        example="8080/webapp/ui",
        description="The endpoint instruction that provide a Web UI. If this is provided, the extension will be integrated into the UI.",
    )
    api_endpoint: Optional[str] = Field(
        None,
        example="8080/extension/api",
        description="The endpoint instruction that provide . If this is provided, the extension will be integrated into the UI.",
    )
    extension_type: ExtensionType = Field(
        None,
        example=ExtensionType.PROJECT_EXTENSION,
        description="The type of the extension.",
    )


class Extension(Service, ExtensionIn):
    pass


class FileIn(BaseEntity):
    # TODO: allow description and icon...
    filename: str = Field(  # TODO: renme to display name
        ...,
        example="customer-table.csv",
        description="The filename.",
    )
    data_type: Optional[DataType] = Field(
        None,
        example=DataType.DATASET,
        description="The categorization of the file.",
    )
    file_extension: Optional[str] = Field(  # TODO: remove file extension?
        None,
        example="csv",
        description="The file extension (suffix).",
    )
    content_type: Optional[str] = Field(
        None,
        example="text/csv",
        description="The content type of the file.",
    )
    is_archive: Optional[bool] = Field(
        None,
        example=False,
        description="Indicates if the file is an archive which can be unpacked.",
    )
    additional_metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata for this file.",
    )


class File(FileIn):
    key: str = Field(
        ...,
        example="datasets/customer-table.csv.v1",
        description="The key of the file.",
    )
    extensions_id: Optional[str] = Field(
        None,
        description="The extension ID in case the file is provided via an extension.",
    )
    creation_date: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Date when the file was uploaded.",
    )
    modification_date: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the file was modified.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has uploaded this file.",
    )
    modified_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last modified this file.",
    )
    file_size: Optional[ByteSize] = Field(
        None,
        example=1073741824,
        description="The file size in bytes.",
    )
    version: Optional[str] = Field(
        None,
        example="1",
        description="Version information of the file.",
    )
    is_latest_version: Optional[bool] = Field(
        None,
        example=True,
        description="Indicates if this is the latest available version of the file.",
    )
    checksum: Optional[str] = Field(
        None,
        example="2a53375ff139d9837e93a38a279d63e5",
        description="The md5 checksum of the file for checking integrity.",
    )
    etag: Optional[str] = Field(
        None,
        example="57f456164b0e5f365aaf9bb549731f32-95",
        description="The etag of the file (mainly used by S3 storage).",
    )


class ApiToken(BaseEntity):
    token: str = Field(
        ...,
        example="f4528e540a133dd53ba6809e74e16774ebe4777a",
        description="API Token.",
    )
    permissions: List[str] = Field(
        ...,
        example=["pm-image-search-engine"],
        description="List of permissions associated with the token.",
    )
    description: Optional[str] = Field(
        None,
        example="Token used for accesing project resources on my local machine.",
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Short description about the context and usage of the token.",
    )
    creation_date: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the token.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this token.",
    )
    associated_project: Optional[str] = Field(
        None,
        example="image-search-engine",
        description="Project ID associated with this token.",
    )


class ResourceAction(BaseEntity):
    action_id: Optional[str] = Field(
        ...,
        example="access-8080",
        description="ID used to identify this action.",
    )
    display_name: Optional[str] = Field(
        None,
        min_length=MIN_DISPLAY_NAME_LENGTH,
        max_length=MAX_DISPLAY_NAME_LENGTH,
        example="Access Port 8080",
        description="Display name of this action.",
    )
    icon: Optional[str] = Field(
        None,
        max_length=1000,
        example="open_in_new",
        description="Material Design Icon name or image URL used for displaying this action.",
    )
    extensions_id: Optional[str] = Field(
        None,
        description="The extension ID associated with this action.",
    )
    extension_name: Optional[str] = Field(
        None,
        description="The extension name associated with this action.",
    )
    instructions: Optional[List[Union[ActionInstruction, str]]] = Field(
        None,
        example=["new-tab"],
        description="A list of instructions for the frontend application.",
    )


class SystemInfo(BaseEntity):
    version: str = Field(
        ...,
        example="0.1.0",
        description="Platform version.",
    )
    orchestrator: ContainerOrchestrator = Field(
        ...,
        example=ContainerOrchestrator.KUBERNETES,
        description="Selected container orchestration runtime (e.g. kubernetes, docker local).",
    )
    namespace: str = Field(
        ...,
        example="mlhub",
        description="Namespace of this system.",
    )
    additional_metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata associated with this system.",
    )


class SystemStatistics(BaseEntity):
    # TODO: finish model
    project_count: int
    user_count: int
    job_count: int
    service_count: int
    file_count: int
