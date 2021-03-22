from typing import Dict, List, Tuple

from contaxy import config
from contaxy.schema.auth import AccessLevel
from contaxy.schema.exceptions import ClientValueError

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
    """Returns `true` if the `permission_str` is valid permission."""
    # TODO: do some basic checks on the permission string
    return PERMISSION_SEPERATOR in permission_str


def is_jwt_token(token: str) -> bool:
    # TODO: Improve this detection
    return len(token) != config.settings.API_TOKEN_LENGTH and not token.islower()


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
