from typing import Any, List

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.param_functions import Body

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
    get_optional_api_token,
)
from contaxy.schema import CoreOperations, User, UserInput, UserRegistration
from contaxy.schema.auth import USER_ID_PARAM, AccessLevel, TokenPurpose, TokenType
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    CREATE_RESOURCE_RESPONSES,
    GET_RESOURCE_RESPONSES,
    UPDATE_RESOURCE_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
    ClientBaseError,
    PermissionDeniedError,
)
from contaxy.schema.system import SystemState
from contaxy.utils import auth_utils, id_utils

router = APIRouter(
    tags=["users"],
    responses={**AUTH_ERROR_RESPONSES, **VALIDATION_ERROR_RESPONSE},
)


@router.get(
    "/users",
    operation_id=CoreOperations.LIST_USERS.value,
    response_model=List[User],
    response_model_exclude_unset=True,
    summary="List all users.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def list_users(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all users that are visible to the authenticated user."""
    component_manager.verify_access(
        token, "users", AccessLevel.READ
    )  # TODO: the right permission?
    return component_manager.get_auth_manager().list_users()


@router.post(
    "/users",
    operation_id=CoreOperations.CREATE_USER.value,
    response_model=User,
    response_model_exclude_unset=True,
    summary="Create a user.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def create_user(
    user_input: UserRegistration,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_optional_api_token),
) -> Any:
    """Creates a user. For the user also a technical project is created.

    If the `password` is not provided, the user can only login by using other methods (social login).
    """
    system_info = component_manager.get_system_manager().get_system_info()
    if system_info.system_state != SystemState.RUNNING:
        raise ClientBaseError(
            status.HTTP_400_BAD_REQUEST,
            "User registration is not possible before system has been initialized!",
        )

    if not component_manager.global_state.settings.USER_REGISTRATION_ENABLED:
        if token is not None:
            # An admin can create users even if registration is disabled
            component_manager.verify_access(token, "users", AccessLevel.ADMIN)
        else:
            raise PermissionDeniedError(
                "User self-registration is deactivated. Please contact an administrator."
            )

    # If self registration is enabled, everyone can create users
    user = auth_utils.create_and_setup_user(
        user_input=user_input,
        auth_manager=component_manager.get_auth_manager(),
        project_manager=component_manager.get_project_manager(),
    )

    # TODO: return also user_project?
    return user


@router.get(
    "/users/me",
    operation_id=CoreOperations.GET_MY_USER.value,
    response_model=User,
    response_model_exclude_unset=True,
    summary="Get my user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_my_user(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the user metadata from the authenticated user."""
    authorized_access = component_manager.verify_access(token)

    # Check if read access to user object is allowed
    component_manager.verify_access(
        token, authorized_access.authorized_subject, AccessLevel.READ
    )
    user_id = id_utils.extract_user_id_from_resource_name(
        authorized_access.authorized_subject
    )
    # Update the last activity time of the user only in this endpoint as it is always called when the UI is loaded
    component_manager.get_auth_manager().update_user_last_activity_time(user_id)

    return component_manager.get_auth_manager().get_user(user_id)


@router.get(
    "/users/{user_id}",
    operation_id=CoreOperations.GET_USER.value,
    response_model=User,
    response_model_exclude_unset=True,
    summary="Get user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_user(
    user_id: str = USER_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the user metadata for a single user."""
    component_manager.verify_access(token, f"users/{user_id}", AccessLevel.READ)
    return component_manager.get_auth_manager().get_user(user_id)


@router.patch(
    "/users/{user_id}",
    operation_id=CoreOperations.UPDATE_USER.value,
    response_model=User,
    response_model_exclude_unset=True,
    summary="Update user metadata.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    responses={**UPDATE_RESOURCE_RESPONSES},
)
def update_user(
    user_id: str = USER_ID_PARAM,
    user_input: UserInput = Body(...),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates the user metadata.

    This will update only the properties that are explicitly set in the patch request.
    The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    # TODO: should only be called by an admin with access to all users, not by users itself
    component_manager.verify_access(token, "users", AccessLevel.ADMIN)
    return component_manager.get_auth_manager().update_user(user_id, user_input)


@router.put(
    "/users/{user_id}:change-password",
    operation_id=CoreOperations.CHANGE_PASSWORD.value,
    summary="Change the user password",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**GET_RESOURCE_RESPONSES},
)
def change_password(
    user_id: str = USER_ID_PARAM,
    password: str = Body(...),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Changes the password of a given user.

    The password can be changed by the given user or a system admin.

    The password is stored as a hash.
    """
    # TODO: check existing password as well for normal users
    if not component_manager.global_state.settings.PASSWORD_AUTH_ENABLED:
        # Admins still can set and change password
        component_manager.verify_access(token, "users", AccessLevel.ADMIN)
    else:
        # Only check if token allows admin access on user object
        component_manager.verify_access(token, f"users/{user_id}", AccessLevel.ADMIN)

    component_manager.get_auth_manager().change_password(user_id, password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    component_manager.verify_access(token, "users/{user_id}", AccessLevel.ADMIN)
    component_manager.get_auth_manager().delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/users/{user_id}/token",
    operation_id=CoreOperations.GET_USER_TOKEN.value,
    response_model=str,
    summary="Get a user token.",
    tags=["users"],
    status_code=status.HTTP_200_OK,
)
def get_user_token(
    user_id: str = USER_ID_PARAM,
    access_level: AccessLevel = Query(
        AccessLevel.WRITE,
        description="Access level of the token.",
        type="string",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns an API token with permission to access all resources accesible by the given user.

    The `read` access level allows read-only access on all resources.
    The `write` access level allows to create and delete user resources.
    The `admin` access level allows additional user actions such as deletion of the user itself.
    """
    # Only allow creating tokens if user has admin access to the user object
    user_resource = f"users/{user_id}"
    component_manager.verify_access(token, user_resource, AccessLevel.ADMIN)
    # Provide access to all resources from the user
    user_token_scope = auth_utils.construct_permission("*", access_level)

    # Check if a user token for this user was already created
    tokens = component_manager.get_auth_manager().list_api_tokens(
        token_subject=user_resource
    )
    try:
        return next(
            (
                token
                for token in tokens
                if token.token_purpose == TokenPurpose.USER_API_TOKEN
                if token.scopes == [user_token_scope]
            )
        ).token
    except StopIteration:
        return component_manager.get_auth_manager().create_token(
            scopes=[user_token_scope],
            token_type=TokenType.API_TOKEN,
            token_subject=user_resource,
            token_purpose=TokenPurpose.USER_API_TOKEN,
            description=f"{access_level} token for user {user_id}.",
        )
