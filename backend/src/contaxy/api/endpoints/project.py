from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query, status

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.schema import AccessLevel, CoreOperations, Project, ProjectInput, User
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.schema.shared import MAX_DISPLAY_NAME_LENGTH, MIN_DISPLAY_NAME_LENGTH
from contaxy.schema.user import USER_ID_PARAM

router = APIRouter(
    tags=["projects"],
    responses={
        401: {"detail": "No API token was provided"},
        403: {"detail": "Forbidden - the user is not authorized to use this resource"},
    },
)


@router.post(
    "/projects",
    operation_id=CoreOperations.CREATE_PROJECT.value,
    response_model=Project,
    summary="Create a new project.",
    status_code=status.HTTP_200_OK,
)
def create_project(
    project: ProjectInput,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Creates a new project.

    We suggest to use the `suggest_project_id` endpoint to get a valid and available ID.
    The project ID might also be set manually, however, an error will be returned if it does not comply with the ID requirements or is already used.
    TODO: put method?
    """
    pass


@router.patch(
    "/projects/{project_id}",
    operation_id=CoreOperations.UPDATE_PROJECT.value,
    response_model=Project,
    summary="Update project metadata.",
    status_code=status.HTTP_200_OK,
)
def update_project(
    project: ProjectInput,
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates the metadata of the given project.

    This will update only the properties that are explicitly set in the patch request.
    The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    pass


@router.get(
    "/projects",
    operation_id=CoreOperations.LIST_PROJECTS.value,
    response_model=List[Project],
    summary="List all projects.",
    status_code=status.HTTP_200_OK,
)
def list_projects(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all projects visible to the authenticated user.

    A project is visible to a user, if the user has the atleast a `read` permission for the project.
    System adminstrators will also see technical projects, such as `system-internal` and `system-global`.
    """
    pass


@router.get(
    "/projects/{project_id}",
    operation_id=CoreOperations.GET_PROJECT.value,
    response_model=Project,
    summary="Get details for a project.",
    status_code=status.HTTP_200_OK,
)
def get_project(
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the metadata of a single project."""
    pass


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
    pass


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
    pass


@router.get(
    "/projects/{project_id}/users",
    operation_id=CoreOperations.LIST_PROJECT_MEMBERS.value,
    summary="List project members.",
    response_model=List[User],
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
    pass


@router.put(
    "/projects/{project_id}/users/{user_id}",
    operation_id=CoreOperations.ADD_PROJECT_MEMBER.value,
    summary="Add user to project.",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
)
def add_project_member(
    project_id: str = PROJECT_ID_PARAM,
    user_id: str = USER_ID_PARAM,
    permission_level: Optional[AccessLevel] = Query(
        AccessLevel.WRITE,
        description="The permission level.",
        type="string",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Adds a user to the project.

    This will add the permission for this project to the user item.
    The `permission_level` defines what the user can do:

    - The `read` permission level allows read-only access on all resources.
    - The `write` permission level allows to create and delete project resources.
    - The `admin` permission level allows to delete the project or add/remove other users.
    """
    pass


@router.delete(
    "/projects/{project_id}/users/{user_id}",
    operation_id=CoreOperations.REMOVE_PROJECT_MEMBER.value,
    summary="Remove user from project.",
    response_model=List[User],
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
    pass
