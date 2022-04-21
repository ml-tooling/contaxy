from typing import Dict, List, Optional, Tuple

from fastapi import Security
from fastapi.security import (
    APIKeyCookie,
    APIKeyHeader,
    APIKeyQuery,
    OAuth2PasswordBearer,
)

from contaxy import config
from contaxy.operations import AuthOperations
from contaxy.operations.project import ProjectOperations
from contaxy.schema import Project, UnauthenticatedError, User
from contaxy.schema.auth import USER_ROLE, USERS_KIND, AccessLevel, UserRegistration
from contaxy.schema.exceptions import ClientValueError
from contaxy.schema.project import ProjectCreation

PERMISSION_SEPERATOR = "#"
RESOURCE_WILDCARD = "*"  # Allows access to all resources

ACCESS_LEVEL_MAPPING: Dict[AccessLevel, List[AccessLevel]] = {
    AccessLevel.ADMIN: [AccessLevel.WRITE, AccessLevel.READ],
    AccessLevel.WRITE: [AccessLevel.READ],
    AccessLevel.READ: [],
}

ACCESS_LEVEL_REVERSE_MAPPING: Dict[AccessLevel, List[AccessLevel]] = {}
for key, value in ACCESS_LEVEL_MAPPING.items():
    for string in value:
        ACCESS_LEVEL_REVERSE_MAPPING.setdefault(string, []).append(key)


def is_valid_permission(permission_str: str) -> bool:
    """Returns `True` if the `permission_str` is valid permission."""
    # TODO: do some basic checks on the permission string
    return PERMISSION_SEPERATOR in permission_str


def is_jwt_token(token: str) -> bool:
    """Returns `True` if the provided token is an JWT token."""
    # TODO: Improve this detection
    return len(token) != config.settings.API_TOKEN_LENGTH and not token.islower()


def construct_permission(resource_name: str, access_level: AccessLevel) -> str:
    """Constructs a permission based on the provided `resource_name`  and `access_level`."""
    return resource_name + PERMISSION_SEPERATOR + access_level.value


def parse_permission(permission: str) -> Tuple[str, AccessLevel]:
    """Extracts the resource name and access level from a permission.

    Args:
        permission: The permission to parse.

    Raises:
        ClientValueError: If the permission cannot be parsed.

    Returns:
        Tuple[str, AccessLevel]: The extracted resource name and access level.
    """

    if not is_valid_permission(permission):
        raise ClientValueError(f"{permission} is not a valid permission.")

    resource, level_str = permission.split(PERMISSION_SEPERATOR)
    # The resource name should not start or end with a slash or colon
    resource = resource.lstrip("/").lstrip(":").rstrip("/").rstrip(":")
    return resource, AccessLevel.load(level_str)


def is_access_level_granted(
    granted_access_level: AccessLevel, requested_access_level: AccessLevel
) -> bool:
    """Checks if the requested access level is allowed by the granted access level.

    Args:
        granted_access_level: The access level that is already granted.
        requested_access_level: The access level to check against the granted level.

    Returns:
        bool: `True` if the access level is granted.
    """
    if granted_access_level is requested_access_level:
        # Same access level
        return True

    return requested_access_level in ACCESS_LEVEL_MAPPING[granted_access_level]


def is_permission_granted(granted_permission: str, requested_permission: str) -> bool:
    """Checks if the requested permission is allowed by the granted permission.

    Args:
        granted_permission: The permission that is already granted.
        requested_permission: The permission to check against the granted permission

    Raises:
        ClientValueError: If one of the permissions cannot be parsed.

    Returns:
        bool: `True` if the permission is granted.
    """

    granted_perm_resource, granted_perm_level = parse_permission(granted_permission)
    requested_perm_resource, requested_perm_level = parse_permission(
        requested_permission
    )

    # the * is a special -> it allows access to all resources
    # Add path divider (/ and :) since it should only grant access if it matches a full path
    if (
        granted_perm_resource != RESOURCE_WILDCARD
        and not f"{requested_perm_resource}/".startswith(f"{granted_perm_resource}/")
        and not f"{requested_perm_resource}:".startswith(f"{granted_perm_resource}:")
    ):
        # The requested permission does not start with the granted permission
        return False

    if not is_access_level_granted(granted_perm_level, requested_perm_level):
        # The requested permission needs atleast the same level as the granted permission
        return False

    return True


def create_and_setup_user(
    user_input: UserRegistration,
    auth_manager: AuthOperations,
    project_manager: ProjectOperations,
    technical_user: bool = False,
) -> User:
    """Create a new user and setup default project and permissions.

    Args:
        user_input (UserRegistration): Information required for creating a new user.
        auth_manager (AuthOperations): The auth manager used to setup default permissions.
        project_manager (ProjectOperations): The project manager used to create the default user project.
        technical_user (bool): Flag to indicate if this is an account not connected to a human user

    Raises:
        ResourceAlreadyExistsError: If the user already exists

    Returns:
        User: The newly created and setup user
    """
    user = auth_manager.create_user(user_input, technical_user)
    _setup_user_default_permissions(user, auth_manager)
    _setup_user_home_project(user, project_manager)
    return user


def _setup_user_default_permissions(user: User, auth_manager: AuthOperations) -> None:
    """Assign the permissions/roles that every user should have by default.

    Args:
        user (User): The user for whom the home project shall be created.
        auth_manager (AuthOperations): The auth manager used to setup the permissions/roles

    Raises:
        ResourceAlreadyExistsError: if a project with the id of the user already exists.

    Returns:
        Project: The created technical project of which the user is a member.
    """
    # TODO: get resource name from object
    user_resource_name = USERS_KIND + "/" + user.id
    # Give user admin permission to itself
    auth_manager.add_permission(
        user_resource_name,
        construct_permission(user_resource_name, AccessLevel.ADMIN),
    )
    # Add user to the default user role
    auth_manager.add_permission(user_resource_name, USER_ROLE)


def _setup_user_home_project(user: User, project_manager: ProjectOperations) -> Project:
    """Create the user's default home project that he has full access to.

    Args:
        user (User): The user for whom the home project shall be created.
        project_manager (ProjectOperations): The project manager used to create the project.

    Raises:
        ResourceAlreadyExistsError: if a project with the id of the user already exists.

    Returns:
        Project: The created technical project of which the user is a member.
    """
    if user.username is not None:
        # Split name by space and dot
        user_first_name = user.username.split()[0].split(".")[0]
        user_project_name = f"{user_first_name.capitalize()}'s Home"
    else:
        user_project_name = "Home"
    user_project = project_manager.create_project(
        project_input=ProjectCreation(
            id=user.id,
            display_name=user_project_name,
            description="My personal project nobody else has access to.",
            # TODO: Maybe state that only the admin has access to the project
        ),
        technical_project=True,
    )

    if user_project.id:
        project_manager.add_project_member(user_project.id, user.id, AccessLevel.ADMIN)

    return user_project


def parse_userid_from_resource_name(user_resource_name: str) -> str:
    """Returns the user id from a user-resource name.

    For example, 'users/abcd' returns 'abcd' as 'users' is the prefix.

    Args:
        user_resource_name (str): The resource name, e.g. 'users/abcd'.

    Returns:
        str: The user id in the user-resource name or an empty string.
    """

    if not user_resource_name or not user_resource_name.startswith("users/"):
        return ""

    return user_resource_name.split("/")[1]


class APITokenExtractor:
    def __init__(self, *, auto_error: bool = True):
        self.auto_error = auto_error

    async def __call__(
        self,
        api_token_query: str = Security(
            APIKeyQuery(name=config.API_TOKEN_NAME, auto_error=False)
        ),
        api_token_header: str = Security(
            APIKeyHeader(name=config.API_TOKEN_NAME, auto_error=False)
        ),
        bearer_token: str = Security(
            OAuth2PasswordBearer(tokenUrl="auth/oauth/token", auto_error=False)
        ),
        api_token_cookie: str = Security(
            APIKeyCookie(name=config.API_TOKEN_NAME, auto_error=False)
        ),
    ) -> Optional[str]:
        # TODO: already check token validity here?
        if api_token_query:
            return api_token_query
        elif api_token_header:
            return api_token_header
        elif bearer_token:
            # TODO: move the bearer token under the cookie?
            return bearer_token
        elif api_token_cookie:
            return api_token_cookie
        else:
            if self.auto_error:
                raise UnauthenticatedError("No API token was provided.")
            else:
                return None


get_api_token = APITokenExtractor(auto_error=True)
get_optional_api_token = APITokenExtractor(auto_error=False)
