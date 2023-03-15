from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Union

from fastapi import status
from pydantic import BaseModel, Field

RESOURCE_ID_REGEX = r"^(?!.*--)[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
QUALIFIED_RESOURCE_ID_REGEX = (
    r"^(?!.*--)[a-z0-9\-]{1,61}[a-z0-9]$"  # TODO: start with [a-z]
)
MAX_DESCRIPTION_LENGTH = 240
MIN_DISPLAY_NAME_LENGTH = 4
MAX_DISPLAY_NAME_LENGTH = 128


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
    CHANGE_PASSWORD = "change_password"
    # Auth Endpoints
    REFRESH_TOKEN = "refresh_token"
    VERIFY_ACCESS = "verify_access"
    LIST_API_TOKENS = "list_api_tokens"
    CREATE_TOKEN = "create_token"
    LOGOUT_USER_SESSION = "logout_user_session"
    LOGIN_USER_SESSION = "login_user_session"
    LIST_RESOURCE_PERMISSIONS = "list_resource_permissions"
    SET_RESOURCE_PERMISSIONS = "set_resource_permissions"
    DELETE_RESOURCE_PERMISSIONS = "delete_resource_permissions"
    GET_RESOURCES_WITH_PERMISSION = "get_resources_with_permission"
    # OAuth2 Endpoints
    AUTHORIZE_CLIENT = "authorize_client"
    REQUEST_TOKEN = "request_token"
    REVOKE_TOKEN = "revoke_token"
    INTROSPECT_TOKEN = "introspect_token"
    LOGIN_CALLBACK = "login_callback"
    OAUTH_ENABLED = "oauth_enabled"
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
    INITIALIZE_SYSTEM = "initialize_system"
    CLEANUP_SYSTEM = "cleanup_system"
    ADD_ALLOWED_IMAGE = "add_allowed_image"
    LIST_ALLOWED_IMAGES = "list_allowed_images"
    GET_ALLOWED_IMAGE = "get_allowed_image"
    DELETE_ALLOWED_IMAGE = "delete_allowed_image"
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
    DELETE_JSON_COLLECTION = "delete_json_collection"
    DELETE_JSON_COLLECTIONS = "delete_json_collections"
    GET_JSON_DOCUMENT = "get_json_document"
    # Service Endpoints
    GET_SERVICE_ACCESS_TOKEN = "get_service_access_token"


class ExtensibleOperations(str, Enum):
    # Service Endpoints
    LIST_SERVICES = "list_services"
    GET_SERVICE_METADATA = "get_service_metadata"
    LIST_DEPLOY_SERVICE_ACTIONS = "list_deploy_service_actions"
    DEPLOY_SERVICE = "deploy_service"
    DELETE_SERVICE = "delete_service"
    DELETE_SERVICES = "delete_services"
    UPDATE_SERVICE = "update_service"
    UPDATE_SERVICE_ACCESS = "update_service_access"
    GET_SERVICE_LOGS = "get_service_logs"
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
    DELETE_JOBS = "delete_jobs"
    GET_JOB_LOGS = "get_job_logs"
    # File Endpoints
    LIST_FILES = "list_files"
    GET_FILE_METADATA = "get_file_metadata"
    UPLOAD_FILE = "upload_file"
    UPLOAD_FILE_NO_KEY = "upload_file_no_key"
    DOWNLOAD_FILE = "download_file"
    LIST_FILE_ACTIONS = "list_file_actions"
    EXECUTE_FILE_ACTION = "execute_file_action"
    DELETE_FILE = "delete_file"
    DELETE_FILES = "delete_files"
    GET_FILE_ACCESS_TOKEN = "get_file_access_token"
    UPDATE_FILE_METADATA = "update_file_metadata"
    # Auth Endpoints
    OPEN_LOGIN_PAGE = "open_login_page"


# TODO: https://fastapi.tiangolo.com/advanced/additional-responses/#combine-predefined-responses-and-custom-ones
# DEFAULT_RESPONSES = {
#    404: {"description": "Item not found"},
#    307: {"description": "Redirecting to another URL"},
#    403: {"description": "Not enough privileges"},
# }
# TODO: evaluate status codes: 302,303,...
OPEN_URL_REDIRECT: Mapping[Union[int, str], Dict[str, Any]] = {
    status.HTTP_307_TEMPORARY_REDIRECT: {"description": "Redirecting to another URL"}
}


class ResourceMetadata(BaseModel):
    id: str = Field(
        "default-id",
        example="ac9ldprwdi68oihk34jli3kdp",
        description="Resource ID. Identifies a resource in a given context and time, for example, in combination with its type. Used in API operations and/or configuration files.",
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


class ResourceInput(BaseModel):
    display_name: Optional[str] = Field(
        None,
        min_length=MIN_DISPLAY_NAME_LENGTH,
        max_length=MAX_DISPLAY_NAME_LENGTH,
        description="A user-defined human-readable name of the resource. The name can be up to 128 characters long and can consist of any UTF-8 character.",
    )
    description: str = Field(
        "",
        max_length=MAX_DESCRIPTION_LENGTH,
        description="A user-defined short description about the resource. Can consist of any UTF-8 character.",
    )
    icon: Optional[str] = Field(
        None,
        description="Identifier or image URL used for displaying this resource.",
    )
    metadata: Dict[str, str] = Field(
        {},
        example={"additional-metadata": "value"},
        description="A collection of arbitrary key-value pairs associated with this resource that does not need predefined structure. Enable third-party integrations to decorate objects with additional metadata for their own use.",
    )
    disabled: bool = Field(
        False,
        description="Allows to disable a resource without requiring deletion. A disabled resource is not shown and not accessible.",
    )
    # TODO: v2
    # tags: Optional[List[str]] = Field(
    #    None,
    #    description="List of tags associated with this resource.",
    # )


class Resource(ResourceInput, ResourceMetadata):
    pass


class ActionInstruction(str, Enum):
    NEW_TAB = "new-tab"


class ResourceAction(BaseModel):
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
    instructions: Optional[List[Any]] = Field(
        None,
        example=["new-tab"],
        description="A list of instructions for the frontend application.",
    )


class ResourceActionExecution(BaseModel):
    parameters: Dict[str, str] = Field(
        {},
        description="Parameters that are passed to the resource action.",
        example={"action-parameter": "parameter-value"},
    )


# TODO: use?
# class BaseEntity(BaseModel):
#     class Config:
#        anystr_strip_whitespace = True
#        underscore_attrs_are_private = True
# TODO: should we set a max length for string to prevent to big requests?
#        max_anystr_length = 20000
