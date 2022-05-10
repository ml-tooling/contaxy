from typing import Any, List

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.param_functions import Body

from contaxy import config
from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.schema import AccessLevel, CoreOperations, Project, ProjectInput, User
from contaxy.schema.auth import USER_ID_PARAM, UserPermission
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    CREATE_RESOURCE_RESPONSES,
    GET_RESOURCE_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
    PermissionDeniedError,
)
from contaxy.schema.project import PROJECT_ID_PARAM, ProjectCreation
from contaxy.schema.shared import MAX_DISPLAY_NAME_LENGTH, MIN_DISPLAY_NAME_LENGTH
from contaxy.utils.auth_utils import get_api_token

router = APIRouter(
    tags=["projects"],
    responses={**AUTH_ERROR_RESPONSES, **VALIDATION_ERROR_RESPONSE},
)


@router.post(
    "/projects",
    operation_id=CoreOperations.CREATE_PROJECT.value,
    response_model=Project,
    response_model_exclude_unset=True,
    summary="Create a new project.",
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def create_project(
    project: ProjectCreation,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Creates a new project.

    We suggest to use the `suggest_project_id` endpoint to get a valid and available ID.
    The project ID might also be set manually, however, an error will be returned if it does not comply with the ID requirements or is already used.
    """
    # TODO: put method?

    # Check the token and get the authorized user
    authorized_access = component_manager.verify_access(token)
    # TODO: Check for permission in "project resource"
    # Check if the token has write access on the user
    component_manager.verify_access(
        token, authorized_access.authorized_subject, AccessLevel.WRITE
    )
    # Make sure the system project cannot be created via the API
    if project.id == config.SYSTEM_INTERNAL_PROJECT:
        raise PermissionDeniedError(f"The project id {project.id} is reserved.")
    return component_manager.get_project_manager().create_project(project)


@router.get(
    "/projects",
    operation_id=CoreOperations.LIST_PROJECTS.value,
    response_model=List[Project],
    response_model_exclude_unset=True,
    summary="List all projects.",
    status_code=status.HTTP_200_OK,
)
def list_projects(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all projects visible to the authenticated user.

    A project is visible to a user, if the user has the at least a `read` permission for the project.
    System administrators will also see technical projects, such as `system-internal` and `system-global`.
    """
    # Check the token and get the authorized user
    authorized_access = component_manager.verify_access(token)
    # TODO: Check for permission in "project resource"
    # Check if the token has read access on the user resource
    component_manager.verify_access(
        token, authorized_access.authorized_subject, AccessLevel.READ
    )
    return component_manager.get_project_manager().list_projects()


@router.patch(
    "/projects/{project_id}",
    operation_id=CoreOperations.UPDATE_PROJECT.value,
    response_model=Project,
    response_model_exclude_unset=True,
    summary="Update project metadata.",
    status_code=status.HTTP_200_OK,
)
def update_project(
    project_id: str = PROJECT_ID_PARAM,
    project: ProjectInput = Body(...),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates the metadata of the given project.

    This will update only the properties that are explicitly set in the patch request.
    The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    component_manager.verify_access(token, f"projects/{project_id}", AccessLevel.WRITE)
    return component_manager.get_project_manager().update_project(project_id, project)


@router.get(
    "/projects/{project_id}",
    operation_id=CoreOperations.GET_PROJECT.value,
    response_model=Project,
    response_model_exclude_unset=True,
    summary="Get details for a project.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_project(
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the metadata of a single project."""
    component_manager.verify_access(token, f"projects/{project_id}", AccessLevel.READ)
    return component_manager.get_project_manager().get_project(project_id)


@router.get(
    "/projects:suggest-id",
    operation_id=CoreOperations.SUGGEST_PROJECT_ID.value,
    response_model=str,
    summary="Suggest project ID.",
    status_code=status.HTTP_200_OK,
)
def suggest_project_id(
    display_name: str = Query(
        ...,
        min_length=MIN_DISPLAY_NAME_LENGTH,
        max_length=MAX_DISPLAY_NAME_LENGTH,
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Suggests a valid and unique project ID for the given display name.

    The project ID will be human-readable and resemble the provided display name,
    but might be cut off or have an attached counter prefix.
    """
    # Only check the token for validity
    component_manager.verify_access(token)
    return component_manager.get_project_manager().suggest_project_id(display_name)


@router.delete(
    "/projects/{project_id}",
    operation_id=CoreOperations.DELETE_PROJECT.value,
    summary="Delete a project.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes a project and all its associated resources including deployments and files.

    A project can only be delete by a user with `admin` permission on the project.
    """
    component_manager.verify_access(token, f"projects/{project_id}", AccessLevel.ADMIN)
    component_manager.get_project_manager().delete_project(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/projects/{project_id}/users",
    operation_id=CoreOperations.LIST_PROJECT_MEMBERS.value,
    summary="List project members.",
    response_model=List[UserPermission],
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def list_project_members(
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all project members.

    This include all users that have atlease a `read` permission on the given project.
    """
    component_manager.verify_access(token, f"projects/{project_id}", AccessLevel.WRITE)
    return component_manager.get_project_manager().list_project_members(project_id)


@router.put(
    "/projects/{project_id}/users/{user_id}",
    operation_id=CoreOperations.ADD_PROJECT_MEMBER.value,
    summary="Add user to project.",
    response_model=List[User],
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def add_project_member(
    project_id: str = PROJECT_ID_PARAM,
    user_id: str = USER_ID_PARAM,
    access_level: AccessLevel = Query(
        AccessLevel.WRITE,
        description="The permission level.",
        type="string",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Adds a user to the project.

    This will add the permission for this project to the user item.
    The `access_level` defines what the user can do:

    - The `read` permission level allows read-only access on all resources.
    - The `write` permission level allows to create and delete project resources.
    - The `admin` permission level allows to delete the project or add/remove other users.
    """
    component_manager.verify_access(token, f"projects/{project_id}", AccessLevel.ADMIN)
    return component_manager.get_project_manager().add_project_member(
        project_id, user_id, access_level
    )


@router.delete(
    "/projects/{project_id}/users/{user_id}",
    operation_id=CoreOperations.REMOVE_PROJECT_MEMBER.value,
    summary="Remove user from project.",
    response_model=List[User],
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
)
def remove_project_member(
    project_id: str = PROJECT_ID_PARAM,
    user_id: str = USER_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Removes a user from a project.

    This will remove the permission for this project from the user item.
    """
    component_manager.verify_access(token, f"projects/{project_id}", AccessLevel.ADMIN)
    return component_manager.get_project_manager().remove_project_member(
        project_id, user_id
    )


@router.get(
    "/projects/{project_id}/token",
    operation_id=CoreOperations.GET_PROJECT_TOKEN.value,
    response_model=str,
    summary="Get project token.",
    tags=["projects"],
    status_code=status.HTTP_200_OK,
)
def get_project_token(
    project_id: str = PROJECT_ID_PARAM,
    access_level: AccessLevel = Query(
        AccessLevel.WRITE,
        description="Access level of the token.",
        type="string",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns an API token with permission (`read`, `write`, or `admin`) to access all project resources.

    The `read` access level allows read-only access on all resources.
    The `write` access level allows to create and delete project resources.
    The `admin` access level allows to delete the project or add/remove other users.
    """
    access_level_to_check = access_level
    if access_level_to_check not in [AccessLevel.ADMIN, AccessLevel.WRITE]:
        # WRITE Access minimum should be the minimum to create tokens
        access_level_to_check = AccessLevel.WRITE
    component_manager.verify_access(
        token, f"projects/{project_id}", access_level_to_check
    )

    return component_manager.get_project_manager().get_project_token(
        project_id, access_level
    )
