from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Path, Query, Response, status

from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.managers.extension import parse_composite_id
from contaxy.schema import (
    ExtensibleOperations,
    Job,
    JobInput,
    ResourceAction,
    Service,
    ServiceInput,
)
from contaxy.schema.auth import AccessLevel, TokenPurpose, TokenType
from contaxy.schema.deployment import JOB_ID_PARAM, SERVICE_ID_PARAM, ServiceUpdate
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    CREATE_RESOURCE_RESPONSES,
    GET_RESOURCE_RESPONSES,
    UPDATE_RESOURCE_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
)
from contaxy.schema.extension import EXTENSION_ID_PARAM
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.schema.shared import (
    OPEN_URL_REDIRECT,
    RESOURCE_ID_REGEX,
    CoreOperations,
    ResourceActionExecution,
)
from contaxy.utils import auth_utils
from contaxy.utils.auth_utils import get_api_token

service_router = APIRouter(
    tags=["services"],
    responses={**AUTH_ERROR_RESPONSES, **VALIDATION_ERROR_RESPONSE},
)
job_router = APIRouter(
    tags=["jobs"],
    responses={**AUTH_ERROR_RESPONSES, **VALIDATION_ERROR_RESPONSE},
)


@service_router.get(
    "/projects/{project_id}/services",
    operation_id=ExtensibleOperations.LIST_SERVICES.value,
    response_model=List[Service],
    summary="List project services.",
    status_code=status.HTTP_200_OK,
)
def list_services(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all services associated with the given project."""
    component_manager.verify_access(
        token, f"projects/{project_id}/services", AccessLevel.READ
    )

    # TODO: List all services from all extensions
    return component_manager.get_service_manager(extension_id).list_services(project_id)


@service_router.get(
    "/projects/{project_id}/services:suggest-config",
    operation_id=ExtensibleOperations.SUGGEST_SERVICE_CONFIG.value,
    response_model=ServiceInput,
    summary="Suggest service configuration.",
    status_code=status.HTTP_200_OK,
)
def suggest_service_config(
    project_id: str = PROJECT_ID_PARAM,
    container_image: str = Query(
        ..., description="Container image to use for suggestion."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services:suggest-config", AccessLevel.WRITE
    )

    return component_manager.get_service_manager(extension_id).suggest_service_config(
        project_id, container_image
    )


@service_router.get(
    "/projects/{project_id}/services/{service_id}",
    operation_id=ExtensibleOperations.GET_SERVICE_METADATA.value,
    response_model=Service,
    summary="Get service metadata.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_service_metadata(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the metadata of a single service.

    The returned metadata might be filtered based on the permission level of the authenticated user.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services/{service_id}", AccessLevel.READ
    )

    service_id, extension_id = parse_composite_id(service_id)
    return component_manager.get_service_manager(extension_id).get_service_metadata(
        project_id, service_id
    )


@service_router.post(
    "/projects/{project_id}/services:deploy-actions",
    operation_id=ExtensibleOperations.LIST_DEPLOY_SERVICE_ACTIONS.value,
    response_model=List[ResourceAction],
    summary="List deploy service actions.",
    status_code=status.HTTP_200_OK,
)
def list_deploy_service_actions(
    service: ServiceInput,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all available service deployment options (actions).

    The returned action IDs should be used when calling the [deploy_service](#services/deploy_service) operation.

    The action mechanism allows extensions to provide additional deployment options for a service based on the provided configuration. It works the following way:

    1. The user requests all available deployment options via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
    3. Extensions can run arbitrary code based on the provided service configuration and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [deploy_service](#services/deploy_service) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to deploy the service based on the provided configuration.
    6. The return value of the operation should be a `Service` object.

    The same action mechanism is also used for other type of actions on resources.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services:deploy-actions", AccessLevel.WRITE
    )

    # TODO: List alldeploy  actions from all extensions
    return component_manager.get_service_manager(
        extension_id
    ).list_deploy_service_actions(project_id, service)


@service_router.post(
    "/projects/{project_id}/services",
    operation_id=ExtensibleOperations.DEPLOY_SERVICE.value,
    response_model=Service,
    summary="Deploy a service.",
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def deploy_service(
    service: ServiceInput,
    project_id: str = PROJECT_ID_PARAM,
    action_id: Optional[str] = Query(
        None,
        description="The action ID from the service deploy options.",
        regex=RESOURCE_ID_REGEX,
    ),
    wait: bool = Query(
        False,
        description="If true, the server waits for the service to be ready before sending a response.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deploy a service for the specified project.

    If no `action_id` is provided, the system will automatically select the best deployment option.

    Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions).
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services", AccessLevel.WRITE
    )

    extension_id = None
    if action_id:
        action_id, extension_id = parse_composite_id(action_id)
    return component_manager.get_service_manager(extension_id).deploy_service(
        project_id, service, action_id, wait=wait
    )


@service_router.delete(
    "/projects/{project_id}/services/{service_id}",
    operation_id=ExtensibleOperations.DELETE_SERVICE.value,
    summary="Delete a service.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    delete_volumes: Optional[bool] = Query(
        False, description="Delete all volumes associated with the deployment."
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes a service.

    This will kill and remove the container and all associated deployment artifacts.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services/{service_id}", AccessLevel.WRITE
    )

    if not delete_volumes:
        delete_volumes = False

    service_id, extension_id = parse_composite_id(service_id)
    component_manager.get_service_manager(extension_id).delete_service(
        project_id, service_id, delete_volumes
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@service_router.patch(
    "/projects/{project_id}/services/{service_id}",
    operation_id=ExtensibleOperations.UPDATE_SERVICE.value,
    summary="Update a service.",
    status_code=status.HTTP_200_OK,
    response_model=Service,
    responses={**UPDATE_RESOURCE_RESPONSES},
)
def update_service(
    service: ServiceUpdate,
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates a service.

    This might force a recreation of the underlying container.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services/{service_id}", AccessLevel.WRITE
    )
    service_id, extension_id = parse_composite_id(service_id)
    return component_manager.get_service_manager(extension_id).update_service(
        project_id, service_id, service
    )


@service_router.post(
    "/projects/{project_id}/services/{service_id}:update-service-access",
    operation_id=ExtensibleOperations.UPDATE_SERVICE_ACCESS.value,
    summary="Update a service.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**UPDATE_RESOURCE_RESPONSES},
)
def update_service_access(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Update the last access information of the service to the current time and calling user."""
    component_manager.verify_access(
        token, f"projects/{project_id}/services/{service_id}", AccessLevel.WRITE
    )
    service_id, extension_id = parse_composite_id(service_id)
    component_manager.get_service_manager(extension_id).update_service_access(
        project_id, service_id
    )


@service_router.delete(
    "/projects/{project_id}/services",
    operation_id=ExtensibleOperations.DELETE_SERVICES.value,
    summary="Delete all services.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_services(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes all services associated with a project."""
    component_manager.verify_access(
        token, f"projects/{project_id}/services", AccessLevel.WRITE
    )

    component_manager.get_service_manager(extension_id).delete_services(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@service_router.get(
    "/projects/{project_id}/services/{service_id}/logs",
    operation_id=ExtensibleOperations.GET_SERVICE_LOGS.value,
    response_model=str,
    summary="Get service logs.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_service_logs(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    lines: Optional[int] = Query(None, description="Only show the last n lines."),
    since: Optional[datetime] = Query(
        None, description="Only show the logs generated after a given date."
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the stdout/stderr logs of the service."""
    component_manager.verify_access(
        token, f"projects/{project_id}/services/{service_id}/logs", AccessLevel.WRITE
    )

    service_id, extension_id = parse_composite_id(service_id)
    return component_manager.get_service_manager(extension_id).get_service_logs(
        project_id, service_id, lines, since
    )


@service_router.get(
    "/projects/{project_id}/services/{service_id}/actions",
    operation_id=ExtensibleOperations.LIST_SERVICE_ACTIONS.value,
    response_model=List[ResourceAction],
    summary="List service actions.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def list_service_actions(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all actions available for the specified service.

    The returned action IDs should be used when calling the [execute_service_action](#services/execute_service_action) operation.

    The action mechanism allows extensions to provide additional functionality on services. It works the following way:

    1. The user requests all available actions via the [list_service_actions](#services/list_service_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_service_actions](#services/list_service_actions) operation.
    3. Extensions can run arbitrary code - e.g., request and check the service metadata for compatibility - and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [execute_service_action](#services/execute_service_action) operation by providing the selected action ID.  The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action.
    6. The return value of the operation can be either a simple message (shown to the user) or a redirect to another URL (e.g., to show a web UI).

    The same action mechanism is also used for other resources (e.g., files, jobs).
    It can support a very broad set of use-cases, for example: Access to service endpoints, dashboards for monitoring, administration tools, and more...
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/services/{service_id}/actions", AccessLevel.WRITE
    )

    # TODO: List all actions from all extensions
    return component_manager.get_service_manager(extension_id).list_service_actions(
        project_id, service_id
    )


@service_router.post(
    "/projects/{project_id}/services/{service_id}/actions/{action_id}",
    operation_id=ExtensibleOperations.EXECUTE_SERVICE_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a service action.",
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT, **GET_RESOURCE_RESPONSES},
)
def execute_service_action(
    action_execution: Optional[ResourceActionExecution] = None,
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    action_id: str = Path(
        ...,
        description="The action ID from the list_service_actions operation.",
        regex=RESOURCE_ID_REGEX,
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Executes the selected service action.

    The actions need to be first requested from the [list_service_actions](#services/list_service_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_service_actions](#services/list_service_actions).
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/services/{service_id}/actions/{action_id}",
        AccessLevel.WRITE,
    )

    action_id, extension_id = parse_composite_id(action_id)
    return component_manager.get_service_manager(extension_id).execute_service_action(
        project_id, service_id, action_id, action_execution or ResourceActionExecution()
    )


# Job Endpoints


@job_router.get(
    "/projects/{project_id}/jobs",
    operation_id=ExtensibleOperations.LIST_JOBS.value,
    response_model=List[Job],
    summary="List project jobs.",
    status_code=status.HTTP_200_OK,
)
def list_jobs(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all jobs associated with the given project."""
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs",
        AccessLevel.READ,
    )

    # TODO: List all jobs from all extensions
    return component_manager.get_job_manager(extension_id).list_jobs(project_id)


@job_router.delete(
    "/projects/{project_id}/jobs",
    operation_id=ExtensibleOperations.DELETE_JOBS.value,
    summary="Delete all jobs.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_jobs(
    project_id: str = PROJECT_ID_PARAM,
    date_from: Optional[datetime] = Query(
        None,
        description="The start date to delete the jobs. If not specified, all jobs will be deleted.",
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="The end date to delete the jobs. If not specified, all jobs will be deleted.",
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes all jobs associated with a project."""
    component_manager.verify_access(
        token, f"projects/{project_id}/jobs", AccessLevel.WRITE
    )
    component_manager.get_job_manager(extension_id).delete_jobs(
        project_id, date_from, date_to
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@job_router.get(
    "/projects/{project_id}/jobs/{job_id}",
    operation_id=ExtensibleOperations.GET_JOB_METADATA.value,
    response_model=Job,
    summary="Get job metadata.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_job_metadata(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the metadata of a single job.

    The returned metadata might be filtered based on the permission level of the authenticated user.
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs/{job_id}",
        AccessLevel.READ,
    )

    job_id, extension_id = parse_composite_id(job_id)
    return component_manager.get_job_manager(extension_id).get_job_metadata(
        project_id, job_id
    )


@job_router.get(
    "/projects/{project_id}/jobs:suggest-config",
    operation_id=ExtensibleOperations.SUGGEST_JOB_CONFIG.value,
    response_model=JobInput,
    summary="Suggest job configuration.",
    status_code=status.HTTP_200_OK,
)
def suggest_job_config(
    project_id: str = PROJECT_ID_PARAM,
    container_image: str = Query(
        ..., description="Container image to use for suggestion."
    ),
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs:suggest-config",
        AccessLevel.WRITE,
    )

    return component_manager.get_job_manager(extension_id).suggest_job_config(
        project_id, container_image
    )


@job_router.post(
    "/projects/{project_id}/jobs:deploy-actions",
    operation_id=ExtensibleOperations.LIST_DEPLOY_JOB_ACTIONS.value,
    response_model=List[ResourceAction],
    summary="List deploy job actions.",
    status_code=status.HTTP_200_OK,
)
def list_deploy_job_actions(
    job: JobInput,
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all available job deployment options (actions).

    The returned action IDs should be used when calling the [deploy_job](#job/deploy_job) operation.

    The action mechanism allows extensions to provide additional deployment options for a job based on the provided configuration. It works the following way:

    1. The user requests all available deployment options via the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation.
    3. Extensions can run arbitrary code based on the provided job configuration and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [deploy_job](#jobs/deploy_job) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to deploy the job based on the provided configuration.
    6. The return value of the operation should be a `Job` object.

    The same action mechanism is also used for other type of actions on resources.
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs:deploy-actions",
        AccessLevel.WRITE,
    )
    # TODO: List all deploy job actions from all extensions
    return component_manager.get_job_manager(extension_id).list_deploy_job_actions(
        project_id, job
    )


@job_router.post(
    "/projects/{project_id}/jobs",
    operation_id=ExtensibleOperations.DEPLOY_JOB.value,
    response_model=Job,
    summary="Deploy a job.",
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT, **CREATE_RESOURCE_RESPONSES},
)
def deploy_job(
    job: JobInput,
    project_id: str = PROJECT_ID_PARAM,
    action_id: Optional[str] = Query(
        None,
        description="The action ID from the job deploy options.",
        regex=RESOURCE_ID_REGEX,
    ),
    wait: bool = Query(
        False,
        description="If true, the server waits for the job to be ready before sending a response.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deploy a job for the specified project.

    If no `action_id` is provided, the system will automatically select the best deployment option.

    Available actions can be requested via the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_deploy_job_actions](#jobs/list_deploy_job_actions).
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs",
        AccessLevel.WRITE,
    )

    extension_id = None
    if action_id:
        action_id, extension_id = parse_composite_id(action_id)

    return component_manager.get_job_manager(extension_id).deploy_job(
        project_id, job, action_id, wait=wait
    )


@job_router.delete(
    "/projects/{project_id}/jobs/{job_id}",
    operation_id=ExtensibleOperations.DELETE_JOB.value,
    summary="Delete a job.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes a job.

    This will kill and remove the container and all associated deployment artifacts.
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs/{job_id}",
        AccessLevel.WRITE,
    )

    job_id, extension_id = parse_composite_id(job_id)
    component_manager.get_job_manager(extension_id).delete_job(project_id, job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@job_router.get(
    "/projects/{project_id}/jobs/{job_id}/logs",
    operation_id=ExtensibleOperations.GET_JOB_LOGS.value,
    response_model=str,
    summary="Get job logs.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_job_logs(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    lines: Optional[int] = Query(None, description="Only show the last n lines."),
    since: Optional[datetime] = Query(
        None, description="Only show the logs generated after a given date."
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the stdout/stderr logs of the job."""
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs/{job_id}/logs",
        AccessLevel.WRITE,
    )

    job_id, extension_id = parse_composite_id(job_id)
    return component_manager.get_job_manager(extension_id).get_job_logs(
        project_id, job_id, lines, since
    )


@job_router.get(
    "/projects/{project_id}/jobs/{job_id}/actions",
    operation_id=ExtensibleOperations.LIST_JOB_ACTIONS.value,
    response_model=List[ResourceAction],
    summary="List job actions.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def list_job_actions(
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    extension_id: Optional[str] = EXTENSION_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all actions available for the specified job.

    The returned action IDs should be used when calling the [execute_job_action](#jobs/execute_job_action) operation.

    The action mechanism allows extensions to provide additional functionality on jobs. It works the following way:

    1. The user requests all available actions via the [list_job_actions](#jobs/list_job_actions) operation.
    2. The operation will be forwarded to all installed extensions that have implemented the [list_job_actions](#jobs/list_job_actions) operation.
    3. Extensions can run arbitrary code - e.g., request and check the job metadata for compatibility - and return a list of actions with self-defined action IDs.
    4. The user selects one of those actions and triggers the [execute_job_action](#jobs/execute_job_action) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID.
    5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action.
    6. The return value of the operation can be either a simple message (shown to the user) or a redirect to another URL (e.g., to show a web UI).

    The same action mechanism is also used for other resources (e.g., files, services).
    It can support a very broad set of use-cases, for example: Access to dashboards for monitoring, adminsitration tools, and more...
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs/{job_id}/actions",
        AccessLevel.WRITE,
    )

    # TODO: List all job actions from all extensions

    return component_manager.get_job_manager(extension_id).list_job_actions(
        project_id, job_id
    )


@job_router.post(
    "/projects/{project_id}/jobs/{job_id}/actions/{action_id}",
    operation_id=ExtensibleOperations.EXECUTE_JOB_ACTION.value,
    # TODO: what is the response model? add additional status codes?
    summary="Execute a job action.",
    status_code=status.HTTP_200_OK,
    responses={**OPEN_URL_REDIRECT, **GET_RESOURCE_RESPONSES},
)
def execute_job_action(
    action_execution: Optional[ResourceActionExecution] = None,
    project_id: str = PROJECT_ID_PARAM,
    job_id: str = JOB_ID_PARAM,
    action_id: str = Path(
        ...,
        description="The action ID from the list_job_actions operation.",
        regex=RESOURCE_ID_REGEX,
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Executes the selected job action.

    The actions need to be first requested from the [list_job_actions](#jobs/list_job_actions) operation.
    If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`.

    The action mechanism is further explained in the description of the [list_job_actions](#jobs/list_job_actions).
    """
    component_manager.verify_access(
        token,
        f"projects/{project_id}/jobs/{job_id}/actions/{action_id}",
        AccessLevel.WRITE,
    )

    action_id, extension_id = parse_composite_id(action_id)
    return component_manager.get_job_manager(extension_id).execute_job_action(
        project_id, job_id, action_id, action_execution or ResourceActionExecution()
    )


@service_router.get(
    "/projects/{project_id}/services/{service_id}/token",
    operation_id=CoreOperations.GET_SERVICE_ACCESS_TOKEN.value,
    response_model=str,
    summary="Get service access token.",
    tags=["services"],
    status_code=status.HTTP_200_OK,
)
def get_service_access_token(
    project_id: str = PROJECT_ID_PARAM,
    service_id: str = SERVICE_ID_PARAM,
    endpoint: Optional[str] = Query(
        None, description="If specified, the token only allows access to this endpoint."
    ),
    description: Optional[str] = Query(
        None, description="Attach a short description to the generated token."
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns an API token with permission to access the service endpoints.

    This token is read-only (permission level read) and does not allow any other permission such as deleting or updating the service.
    The token can be deleted (revoked) at any time.
    """
    authorized_access = component_manager.verify_access(
        token,
        f"projects/{project_id}/services/{service_id}/token",
        AccessLevel.WRITE,
    )

    if not endpoint:
        endpoint = ""

    access_service_scope = auth_utils.construct_permission(
        f"projects/{project_id}/services/{service_id}/access/{endpoint}",
        AccessLevel.READ,
    )

    component_manager.get_auth_manager().create_token(
        token_subject=authorized_access.authorized_subject,
        scopes=[access_service_scope],
        token_type=TokenType.API_TOKEN,
        description=description,
        token_purpose=TokenPurpose.SERVICE_ACCESS_TOKEN,
    )
