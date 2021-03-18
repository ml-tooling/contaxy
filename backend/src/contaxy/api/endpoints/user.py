from typing import Any, List

from fastapi import APIRouter, Depends, Security, status
from fastapi.param_functions import Body
from fastapi.security import OAuth2PasswordBearer

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.schema import CoreOperations, User, UserInput, UserRegistration
from contaxy.schema.exceptions import ServerBaseError
from contaxy.schema.user import USER_ID_PARAM

router = APIRouter(
    tags=["users"],
    responses={
        401: {"detail": "No API token was provided"},
        403: {"detail": "Forbidden - the user is not authorized to use this resource"},
    },
)


@router.get(
    "/users",
    operation_id=CoreOperations.LIST_USERS.value,
    response_model=List[User],
    summary="List all users.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def list_users(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all users that are visible to the authenticated user."""
    return component_manager.get_user_manager().list_users()


@router.post(
    "/users",
    operation_id=CoreOperations.CREATE_USER.value,
    response_model=User,
    summary="Create a user.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def create_user(
    user: UserRegistration,
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Creates a user.

    If the `password` is not provided, the user can only login by using other methods (social login).
    """
    if user.password:
        # TODO create password for the user
        del user.password
    return component_manager.get_user_manager().create_user(user, technical_user=False)


@router.get(
    "/users/me",
    operation_id=CoreOperations.GET_MY_USER.value,
    response_model=User,
    summary="Get my user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def get_my_user(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the user metadata from the authenticated user."""
    # TODO: not a manager operation -> just forward to the get_user operation
    raise NotImplementedError


@router.get(
    "/users/{user_id}",
    operation_id=CoreOperations.GET_USER.value,
    response_model=User,
    summary="Get user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: str = USER_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the user metadata for a single user."""
    raise NotImplementedError


@router.patch(
    "/users/{user_id}",
    operation_id=CoreOperations.UPDATE_USER.value,
    response_model=User,
    summary="Update user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def update_user(
    user: UserInput,
    user_id: str = USER_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates the user metadata.

    This will update only the properties that are explicitly set in the patch request.
    The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    # TODO: should only be called by an admin
    raise NotImplementedError


@router.put(
    "/users/{user_id}:change-password",
    operation_id=CoreOperations.CHANGE_PASSWORD.value,
    summary="Change the user password",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_user_password(
    user_id: str = USER_ID_PARAM,
    password: str = Body(...),
    bearer_token: str = Security(
        OAuth2PasswordBearer(tokenUrl="auth/oauth/token", auto_error=False)
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Changes the password of a given user.

    The endpoint MUST be called with basic auth credentials (user-id and password).
    The password can be changed by the given user or a system admin.

    The password is stored as a hash.
    """
    raise NotImplementedError


@router.delete(
    "/users/{user_id}",
    operation_id=CoreOperations.DELETE_USER.value,
    summary="Delete a user.",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: str = USER_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes a user and all resources which are only accesible by this user.

    Shared project resources will not be deleted.
    """
    raise NotImplementedError
