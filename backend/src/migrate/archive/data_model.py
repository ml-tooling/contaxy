from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import (
    UUID4,
    BaseModel,
    BaseSettings,
    ByteSize,
    EmailStr,
    Field,
    Json,
    SecretStr,
    constr,
)
from pydantic.errors import DateError
from pydantic.networks import stricturl

MIN_DISPLAY_NAME_LENGTH = 4
MAX_DISPLAY_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 240
MIN_PROJECT_ID_LENGTH = 4
MAX_PROJECT_ID_LENGTH = 25


RESOURCE_ID_REGEX = r"^(?!.*--)[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
QUALIFIED_RESOURCE_ID_REGEX = (
    r"^(?!.*--)[a-z0-9\-]{1,61}[a-z0-9]$"  # TODO: start with [a-z]
)
FILE_KEY_REGEX = r"^(?!.*(\r|\n|\.\.)).{1,1024}$"  # no new lines or consecutive dots


class Settings(BaseSettings):
    """Platform Settings."""

    # Deactivate Setting or changing password from user accounts
    # Admins can still set and change passwords for users, or use the basic auth authentication login page
    DISABLE_BASIC_AUTH: str


class CoreOperations(str, Enum):
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
    GET_MY_USER = "get_my_user"
    GET_USER = "get_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    GET_USER_TOKEN = "get_user_token"
    CREATE_USER = "create_user"
    # Auth Endpoints
    REFRESH_TOKEN = "refresh_token"
    VERIFY_TOKEN = "verify_token"
    LIST_API_TOKENS = "list_api_tokens"
    CREATE_TOKEN = "create_token"
    LOGOUT_SESSION = "logout_session"
    # OAuth2 Endpoints
    AUTHORIZE_CLIENT = "authorize_client"
    REQUEST_TOKEN = "request_token"
    REVOKE_TOKEN = "revoke_token"
    INTROSPECT_TOKEN = "introspect_token"
    LOGIN_CALLBACK = "login_callback"
    GET_USERINFO = "get_userinfo"
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
    # Secrets Endpoints
    CREATE_SECRET = "create_secret"
    DELETE_SECRET = "delete_secret"
    LIST_SECRETS = "list_secrets"
    # Configuration Endpoints
    LIST_CONFIGURATIONS = "list_configurations"
    CREATE_CONFIGURATION = "create_configuration"
    UPDATE_CONFIGURATION = "update_configuration"
    DELETE_CONFIGURATION = "delete_configuration"
    GET_CONFIGURATION = "get_configuration"
    GET_CONFIGURATION_PARAMETER = "get_configuration_parameter"
    # JSON Document Endpoints
    LIST_JSON_DOCUMENTS = "list_json_documents"
    CREATE_JSON_DOCUMENT = "create_json_document"
    UPDATE_JSON_DOCUMENT = "update_json_document"
    DELETE_JSON_DOCUMENT = "delete_json_document"
    GET_JSON_DOCUMENT = "get_json_document"


class ExtensibleOperations(str, Enum):
    # Service Endpoints
    LIST_SERVICES = "list_services"
    GET_SERVICE_METADATA = "get_service_metadata"
    LIST_DEPLOY_SERVICE_ACTIONS = "list_deploy_service_actions"
    DEPLOY_SERVICE = "deploy_service"
    DELETE_SERVICE = "delete_service"
    UPDATE_SERVICE = "update_service"
    GET_SERVICE_LOGS = "get_service_logs"
    GET_SERVICE_ACCESS_TOKEN = "get_service_access_token"
    LIST_SERVICE_ACTIONS = "list_service_actions"
    EXECUTE_SERVICE_ACTION = "execute_service_action"
    SUGGEST_SERVICE_CONFIG = "suggest_service_config"
    ACCESS_SERVICE = "access_service"
    # Job Endpoints
    LIST_JOBS = "list_jobs"
    GET_JOB_METADATA = "get_job_metadata"
    LIST_DEPLOY_JOB_ACTIONS = "list_deploy_job_actions"
    LIST_JOB_ACTIONS = "list_job_actions"
    EXECUTE_JOB_ACTION = "execute_job_action"
    SUGGEST_JOB_CONFIG = "suggest_job_config"
    DEPLOY_JOB = "deploy_job"
    DELETE_JOB = "delete_job"
    GET_JOB_LOGS = "get_job_logs"
    # File Endpoints
    LIST_FILES = "list_files"
    GET_FILE_METADATA = "get_file_metadata"
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    LIST_FILE_ACTIONS = "list_file_actions"
    EXECUTE_FILE_ACTION = "execute_file_action"
    DELETE_FILE = "delete_file"
    GET_FILE_ACCESS_TOKEN = "get_file_access_token"
    UPDATE_FILE_METADATA = "update_file_metadata"
    # Auth Endpoints
    OPEN_LOGIN_PAGE = "open_login_page"


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


class ResourceType(str, Enum):
    USER = "user"
    PROJECT = "project"
    DEPLOYMENT = "deployment"
    FILE = "file"
    SECRET = "secret"
    JSON_DOCUMENT = "json-document"


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


class ActionInstruction(str, Enum):
    NEW_TAB = "new-tab"


class PermissionLevel(str, Enum):
    # Map to: select, insert, update, delete
    READ = "read"  # Viewer, view: Allows admin access , Can only view existing resources. Permissions for read-only actions that do not affect state, such as viewing (but not modifying) existing resources or data.
    WRITE = "write"  # Editor, edit, Contributor : Allows read/write access , Can create and manage all types of resources but can’t grant access to others.  All viewer permissions, plus permissions for actions that modify state, such as changing existing resources.
    ADMIN = "admin"  # Owner : Allows read-only access. Has full access to all resources including the right to edit IAM, invite users, edit roles. All editor permissions and permissions for the following actions:
    # none


class OauthToken(BaseModel):
    token_type: str = Field(
        ..., description="The type of token this is, typically just the string `bearer`"
    )
    access_token: str = Field(..., description="The access token string.")
    expires_in: Optional[int] = Field(
        None,
        description="The expiration time of the access token in seconds.",
    )
    refresh_token: Optional[str] = Field(
        None, description="API token to refresh the sesion token (if it expires)."
    )
    scope: Optional[str] = Field(
        None, description="The scopes contained in the access token."
    )
    id_token: Optional[str] = Field(
        None,
        description="OpenID Connect ID Token that encodes the user’s authentication information.",
    )


class OpenIDUserInfo(BaseModel):
    # Based on: https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
    sub: str = Field(
        ..., description="Subject - Identifier for the End-User at the Issuer."
    )
    name: Optional[str] = Field(
        None,
        description="End-User's full name in displayable form including all name parts, possibly including titles and suffixes, ordered according to the End-User's locale and preferences.",
    )
    # TODO: this is actually
    preferred_username: Optional[str] = Field(
        None,
        description="Shorthand name by which the End-User wishes to be referred to.",
    )
    email: Optional[str] = Field(
        None,
        description="End-User's preferred e-mail address",
    )
    updated_at: Optional[int] = Field(
        None,
        description="Time the End-User's information was last updated. Number of seconds from 1970-01-01T0:0:0Z as measured in UTC until the date/time.",
    )


class TokenIntrospection(BaseModel):
    active: bool = Field(
        ...,
        description="Indicator of whether or not the presented token is currently active.",
    )
    scope: Optional[str] = Field(
        None,
        description="A space-delimited list of scopes.",
    )
    client_id: Optional[str] = Field(
        None,
        description="Client identifier for the OAuth 2.0 client that requested this token.",
    )
    username: Optional[str] = Field(
        None,
        description="Human-readable identifier for the resource owner who authorized this token.",
    )
    token_type: Optional[str] = Field(
        None,
        description="Type of the token as defined in Section 5.1 of OAuth 2.0 [RFC6749].",
    )
    exp: Optional[int] = Field(
        None,
        description="Timestamp, measured in the number of seconds since January 1 1970 UTC, indicating when this token will expire, as defined in JWT [RFC7519].",
    )
    iat: Optional[int] = Field(
        None,
        description="Timestamp, measured in the number of seconds since January 1 1970 UTC, indicating when this token was originally issued, as defined in JWT [RFC7519].",
    )
    nbf: Optional[int] = Field(
        None,
        description="Timestamp, measured in the number of seconds since January 1 1970 UTC, indicating when this token is not to be used before, as defined in JWT [RFC7519].",
    )
    sub: Optional[str] = Field(
        None,
        description="Subject of the token, as defined in JWT [RFC7519]. Usually a machine-readable identifier of the resource owner who authorized this token.",
    )
    aud: Optional[str] = Field(
        None,
        description="Service-specific string identifier or list of string identifiers representing the intended audience for this token, as defined in JWT [RFC7519].",
    )
    iss: Optional[str] = Field(
        None,
        description="String representing the issuer of this token, as defined in JWT [RFC7519].",
    )
    jti: Optional[str] = Field(
        None,
        description="String identifier for the token, as defined in JWT [RFC7519].",
    )
    uid: Optional[str] = Field(
        None,
        description="The user ID. This parameter is returned only if the token is an access token and the subject is an end user.",
    )


class ResourceInput(BaseModel):
    display_name: Optional[str] = Field(
        None,
        max_length=128,
        description="A user-defined human-readable name of the resource. The name can be up to 128 characters long and can consist of any UTF-8 character.",
    )
    description: Optional[str] = Field(
        None,
        # TODO: max_length restriction
        description="A user-defined short description about the resource. Can consist of any UTF-8 character.",
    )
    icon: Optional[str] = Field(
        None,
        description="Identifier or image URL used for displaying this resource.",
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="A collection of arbitrary key-value pairs associated with this resource that does not need predefined structure. Enable third-party integrations to decorate objects with additional metadata for their own use.",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="List of tags associated with this resource.",
    )
    disabled: Optional[bool] = Field(
        None,
        description="Allows to disable a resource without requiring deletion. A disabled resource is not shown and not accessible.",
    )


class ResourceBasics(BaseModel):
    id: Optional[str] = Field(
        None,
        example="ac9ldprwdi68oihk34jli3kdp",
        description="Resource ID. Identifies a resource in a given context and time, for example, in combination with its type. Used in API operations and/or configuration files.",
    )
    name: Optional[str] = Field(
        None,
        example="resources/ac9ldprwdi68oihk34jli3kdp",
        description="Resource Name. A relative URI-path that uniquely identifies a resource within the system. Assigned by the server and read-only.",
    )
    kind: Optional[str] = Field(
        None,
        example="resources",
        description="Resource Type (Schema). Identifies what kind of resource this is. Assigned by the server and read-only.",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the resource creation. Assigned by the server and read-only.",
    )
    created_by: Optional[str] = Field(
        None,
        example="resources/ac9ldprwdi68oihk34jli3kdp",
        description="Resource name of the entity responsible for the creation of this resource. Assigned by the server and read-only.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the last resource modification. Is updated when create/patch/delete operation is performed. Assigned by the server and read-only.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="resources/ac9ldprwdi68oihk34jli3kdp",
        description="Resource name of the entity responsible for the last modification of this resource. Assigned by the server and read-only.",
    )
    # TODO: v2
    # global_id: Optional[str] = Field(
    #    None,
    #    description="Globally unique ID of this resource.",
    # )
    # TODO: v2
    # deleted_at: Optional[datetime] = Field(
    #    None,
    #    description="Timestamp when the resource should be deleted.",
    # )


class Resource(ResourceInput, ResourceBasics):
    pass


class BaseEntity(BaseModel):
    class Config:
        anystr_strip_whitespace = True
        underscore_attrs_are_private = True
        # TODO: should we set a max length for string to prevent to big requests?
        max_anystr_length = 20000


class GlobalID(BaseEntity):
    format_version: int = Field(1, description="Version of the ID structure.")
    resource_type: str = Field(..., description="Type of the resource")
    subject_id: str = Field(...)
    project_id: Optional[str] = Field(None)
    extension_id: Optional[str] = Field(
        None,
        example="john-doe",
        description="The extension ID in case the deployment is deployed via an extension.",
    )


class Permission(BaseEntity):
    global_id: GlobalID = Field(..., description="The global ID of the entity ")
    permission_level: PermissionLevel = Field(
        ..., description="The kind of access that is granted on the resource."
    )
    restriction: Optional[str] = Field(None)


class UserInput(BaseEntity):
    username: Optional[str] = Field(
        None,
        example="john-doe",
        description="A unique username on the system.",
    )  # nickname
    email: Optional[EmailStr] = Field(
        None, example="john.doe@example.com", description="User email address."
    )
    # TODO: this field should be only usable by system administrators
    permissions: Optional[List[str]] = Field(
        None,
        example=["project:my-awesome-project:write"],
        description="List of user permissions.",
    )
    disabled: Optional[bool] = Field(
        False,
        description="Indicates that user is disabled. Disabling a user will prevent any access to user-accesible resources.",
    )


class UserRegistration(UserInput):
    # The password is only part of the user input object and should never returned
    # TODO: a password can only be changed when used via oauth password bearer
    # TODO: System admin can change passwords for all users
    password: Optional[SecretStr] = Field(
        ...,
        description="Password for the user. The password will be stored in as a hash.",
    )


class User(UserInput):
    id: UUID4 = Field(
        ...,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="Unique ID of the user.",
    )
    technical_user: Optional[bool] = Field(
        False,
        description="Indicates if the user is a technical user created by the system.",
    )


class Quota(BaseEntity):
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


class ProjectInput(BaseEntity):
    # TODO: add validation regex
    id: str = Field(
        None, example="my-awesome-project", description="ID of the project."
    )
    display_name: str = Field(
        None,
        min_length=MIN_DISPLAY_NAME_LENGTH,
        max_length=MAX_DISPLAY_NAME_LENGTH,
        example="My Awesome Project",
        description="Display name of the project. This can be changed after creation.",
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        example="Building an awesome ML model.",
        description="Short description of this project. This can be changed after creation.",
    )
    icon: Optional[str] = Field(
        None,
        max_length=1000,
        example="search",
        description="Material Design Icon name or image URL used for displaying this project.",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags associated with this project.",
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
    disabled: Optional[bool] = Field(
        False,
        description="Indicates that project is disabled. Disabling a project will prevent any access to project resources.",
    )


class Project(ProjectInput):
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the project.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the project metadata was modified.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has created this project.",
    )
    update_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last updated this projects metadata.",
    )
    # available: Optional[bool] = Field(
    #    False,
    #    description="Indicates that this project is ready for usage.",
    # )
    technical_project: Optional[bool] = Field(
        False,
        description="Indicates that this is a technical project created by the system.",
    )
    statistics: Optional[Statistics] = Field(
        None,
        description="Project statistics.",
    )


class DeploymentCompute(BaseEntity):
    min_cpus: Optional[int] = Field(
        None,
        example=2,
        ge=0,
        description="Minimum number of CPU cores required by this deployment. The system will make sure that atleast this amount is available to the deployment.",
    )
    max_cpus: Optional[int] = Field(
        None,
        example=4,
        ge=1,
        description="Maximum number of CPU cores. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more.",
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
        ge=1,
        description="Maximum amount of memory in Megabyte. Even so the system will try to provide the specified amount, it's only guaranteed that the deployment cannot use more.",
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
    # TODO: allowed_gpu_types: Optional[List[str]] = None
    volume_path: Optional[Path] = Field(
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


class DeploymentInput(BaseEntity):
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
    tags: Optional[List[str]] = Field(
        None,
        description="Tags associated with this deployment.",
    )
    parameters: Optional[Dict[str, str]] = Field(
        None,
        example={"TEST_PARAM": "param-value"},
        description="Parmeters (enviornment variables) for this deployment.",
    )
    # TODO: v2
    # input_files: Optional[List[dict]] = Field(
    #    None,
    #    description="A list of files that should be added to the deployment.",
    # )
    compute: Optional[DeploymentCompute] = Field(
        None,
        description="Compute instructions and limitations for this deployment.",
    )
    command: Optional[str] = Field(
        None,
        description="Command to run within the deployment. This overwrites the existing entrypoint.",
    )
    # TODO: v2
    # command_args: Optional[List[str]] = Field(
    #    None,
    #    description="Arguments to use for the command of the deployment. This overwrites the existing arguments.",
    # )
    requirements: Optional[List[Union[DeploymentRequirement, str]]] = Field(
        None,
        description="Additional deployment manager specific requirements for deployment.",
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata for this deployment.",
    )
    endpoints: Optional[List[str]] = Field(
        None,
        example=["8080", "9001/webapp/ui", "9002b"],
        description="A list of HTTP endpoints that can be accessed. This should always have an internal port and can include additional instructions, such as the URL path.",
    )


class Deployment(DeploymentInput):
    id: str = Field(...)
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
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Date when the deployment was created.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has created this deployment.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the deployment was updated.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last modified this deployment.",
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


class ServiceInput(DeploymentInput):
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
    pass


class Service(Deployment, ServiceInput):
    health_endpoint: Optional[str] = Field(
        None,
        example="8080/healthz",
        description="The endpoint instruction that can be used for checking the deployment health.",
    )
    # TODO: v2
    # healthy: Optional[bool] = Field(
    #    True,
    #    description="Indicates if the deployment is healthy.",
    # )


class JobInput(DeploymentInput):
    output_files: Optional[List[dict]] = Field(
        None,
        description="A list of container internal files that should be uploaded to the storage once the job has succeeded.",
    )


class Job(Deployment, JobInput):
    pass


class ExtensionInput(ServiceInput):
    capabilities: Optional[List[Union[ExtensibleOperations, str]]] = Field(
        None,
        # TODO: provide example
        description="List of capabilities implemented by this extension.",
    )
    # TODO: do not use ui or api endpoint -> use endpoints list instead and provide metadata there
    api_endpoint: Optional[str] = Field(
        None,
        example="8080/extension/api",
        description="The endpoint base URL that implements the API operation stated in the capabilities property.",
    )
    ui_endpoint: Optional[str] = Field(
        None,
        example="8080/webapp/ui",
        description="The endpoint instruction that provide a Web UI. If this is provided, the extension will be integrated into the UI.",
    )

    # TODO: add again
    # extension_type: ExtensionType = Field(
    #    None,
    #    example=ExtensionType.PROJECT_EXTENSION,
    #    description="The type of the extension.",
    # )


class Extension(Service, ExtensionInput):
    pass


class FileInput(BaseEntity):
    key: str = Field(
        ...,
        example="datasets/customer-table.csv",
        description="The (virtual) path of the file. This path might not correspond to the actual path on the file storage.",
        min_length=1,
        max_length=1024,  # Keys can only be 1024 chars long
        regex=FILE_KEY_REGEX,
    )
    display_name: str = Field(
        None,
        example="customer-table.csv",
        description="The display name of the file. This will be automtically set to the filename.",
    )
    content_type: Optional[str] = Field(
        None,
        example="text/csv",
        description="A standard MIME type describing the format of the contents. If an file is stored without a Content-Type, it is served as application/octet-stream.",
    )
    # TODO: content_encoding: Specifies what content encodings have been applied to the object and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field.
    # TODO: content_disposition: Specifies presentational information for the object.
    # TODO: content_language: The language the content is in.
    external_id: Optional[str] = Field(
        None,
        example="datasets/customer-table.csv",
        description="The ID (or access instruction) of the file on the file storage provider.",
    )
    disabled: Optional[bool] = Field(
        None,
        example=False,
        description="Indicates that file is disabled. Disabling a file will prevent any access to the resource.",
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        example="CSV table that contains insights about our customers.",
        description="Short description of this file.",
    )
    icon: Optional[str] = Field(
        None,
        example="table_chart",
        max_length=1000,
        description="Material Design Icon name or image URL used for displaying this file.",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags associated with this file.",
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        example={"additional-metadata": "value"},
        description="Additional key-value metadata for this file.",
    )


class File(FileInput):
    id: str = Field(
        ...,
        example="f2c9e99a23b7ca50df0d5cb52023c583abf88a57",
        description="File ID. Guaranteed to be unique within the scope of the resource type and extension.",
        regex=RESOURCE_ID_REGEX,
        max_length=63,
    )
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Date when the file was uploaded.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has uploaded this file.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the file was updated.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last modified this file.",
    )
    file_extension: Optional[str] = Field(
        None,
        example="csv",
        description="The full file extension extracted from the key field. May contain multiple concatenated extensions, such as `tar.gz`.",
    )
    file_size: Optional[ByteSize] = Field(
        None,
        example=1073741824,
        description="The file size in bytes.",
    )
    version: Optional[str] = Field(
        None,
        example="1614204512210009",
        description="Version tag of this file. The version order might not be inferable from the version tag/",
    )
    available_versions: Optional[List[str]] = Field(
        None,
        example=["1614204512210009", "23424512210009", "6144204512210009"],
        description="All version tags available for the given file.",
    )
    latest_version: Optional[bool] = Field(
        None,
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


class TokenPurpose(str, Enum):
    USER_GENERATED = "user-generated"
    REFRESH_TOKEN = "refresh-token"  # For user sessions
    DEPLOYMENT_TOKEN = "deployment-token"


class ApiToken(BaseEntity):
    token: str = Field(
        ...,
        example="f4528e540a133dd53ba6809e74e16774ebe4777a",
        description="API Token.",
    )
    permissions: List[str] = Field(
        ...,
        example=["pm-my-awesome-project"],
        description="List of permissions associated with the token.",
    )
    description: Optional[str] = Field(
        None,
        example="Token used for accesing project resources on my local machine.",
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Short description about the context and usage of the token.",
    )
    created_at: Optional[datetime] = Field(
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
        example="my-awesome-project",
        description="Project ID associated with this token.",
    )
    expires_at: Optional[datetime] = Field(
        None,
        example="2021-04-25T10:20:30.400+02:30",
        description="Date at which the token expires and, thereby, gets revoked.",
    )
    token_purpose: Optional[TokenPurpose] = Field(
        None,
        example=TokenPurpose.REFRESH_TOKEN,
        description="The purpose of the token.",
    )


class ResourceAction(BaseEntity):
    action_id: Optional[str] = Field(
        ...,
        example="access-8080",
        description="ID used to identify this action.",
        regex=RESOURCE_ID_REGEX,
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
    extension_id: Optional[str] = Field(
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


class ConfigurationType(str, Enum):
    MONGO_DB_CONNECTION = "mongo-db-connection"
    SSH_CONNECTION = "ssh-connection"
    POSTGRES_DB_CONNECTION = "postgres-connection"


class ConfigurationInput(BaseEntity):
    id: str = Field(
        ...,
        example="customer-mongo-db",
        description="ID of the configuration.",
    )
    configuration_type: Optional[ConfigurationType] = Field(
        None,
        example=ConfigurationType.MONGO_DB_CONNECTION,
        description="Predefined type of this configuration.",
    )
    parameters: Optional[Dict[str, str]] = Field(
        None,
        example={
            "MONGO_DB_URI": "mongodb://mongodb0.example.com:27017",
            "MONGO_DB_USER": "admin",
            "MONGO_DB_PASSWORD": "f4528e540a133dd53ba6809e74e16774ebe4777a",
        },
        description="Parmeters (enviornment variables) shared with this configuration.",
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        example="Mongo DB connection to customer database.",
        description="Short description about this configuration.",
    )
    icon: Optional[str] = Field(
        None,
        example="table_chart",
        max_length=1000,
        description="Material Design Icon name or image URL used for displaying this configuration.",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags associated with this configuration.",
    )


class Configuration(ConfigurationInput):
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Date when the configuration was created.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this configuration.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the configuration was updated.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last modified this configuration.",
    )


class SecretInput(BaseEntity):
    # TODO: Use value encryption like in Github API, but Vault is not encrypting
    value: str = Field(
        ...,
        example="f4528e540a133dd53ba6809e74e16774ebe4777a",
        description="Value of the secret.",
    )
    # TODO: group_name -> group secrets together (e.g. all details for a db conenction)


class Secret(SecretInput):
    key: str = Field(
        ...,
        example="MY_API_TOKEN",
        description="Name of the secret.",
    )
    # == Shared Parameters
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the secret.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this secret.",
    )


class JsonDocument(BaseEntity):
    key: str = Field(
        ...,
        example="my-json-document",
        description="Unique key of the document.",
    )
    json_value: str = Field(
        ...,
        example="{'foo': 'bar'}",
        description="JSON value of the document.",
    )
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the document.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this document.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the document was updated.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last updated this document.",
    )


class SystemStatistics(BaseEntity):
    # TODO: finish model
    project_count: int
    user_count: int
    job_count: int
    service_count: int
    file_count: int
