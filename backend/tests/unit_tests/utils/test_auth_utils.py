from typing import Tuple

import pytest

from contaxy.schema.auth import AccessLevel
from contaxy.schema.exceptions import ClientValueError
from contaxy.utils import auth_utils


@pytest.mark.unit
@pytest.mark.parametrize(
    "permission,expected_result",
    [
        ("projects#read", ("projects", AccessLevel.READ)),
        (
            "projects/98n12398m1x12/#write",
            ("projects/98n12398m1x12", AccessLevel.WRITE),
        ),
        (
            "/projects#admin",
            ("projects", AccessLevel.ADMIN),
        ),
        (
            "/projects#WRITE",
            ("projects", AccessLevel.WRITE),
        ),
        (
            "projects#foo",
            ("projects", AccessLevel.UNKNOWN),
        ),
        (
            "*#read",
            ("*", AccessLevel.READ),
        ),
    ],
)
def test_parse_permission(
    permission: str, expected_result: Tuple[str, AccessLevel]
) -> None:
    assert auth_utils.parse_permission(permission) == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(
    "permission",
    [
        ("projects/foo"),
        ("/projects/foo:read"),
        ("apsdfjaponasd90j2f09"),
    ],
)
def test_parse_permission_exception(permission: str) -> None:
    with pytest.raises(ClientValueError):
        auth_utils.parse_permission(permission)


@pytest.mark.unit
@pytest.mark.parametrize(
    "granted_access_level, requested_access_level, granted",
    [
        (AccessLevel.ADMIN, AccessLevel.READ, True),
        (AccessLevel.READ, AccessLevel.ADMIN, False),
        (AccessLevel.WRITE, AccessLevel.WRITE, True),
        (AccessLevel.WRITE, AccessLevel.READ, True),
        (AccessLevel.READ, AccessLevel.WRITE, False),
        (AccessLevel.ADMIN, AccessLevel.ADMIN, True),
    ],
)
def test_is_access_level_granted(
    granted_access_level: AccessLevel,
    requested_access_level: AccessLevel,
    granted: bool,
) -> None:
    assert (
        auth_utils.is_access_level_granted(granted_access_level, requested_access_level)
        == granted
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "granted_permission, requested_permission, granted",
    [
        (
            "projects/awesome-project#read",
            "projects/awesome-project/services/foo-bar-service#read",
            True,
        ),
        (
            "projects/awesome-project#write",
            "projects/awesome-project/services/foo-bar-service#read",
            True,
        ),
        (
            "projects/awesome-project#read",
            "projects/awesome-project/services/foo-bar-service#admin",
            False,
        ),
        (
            "projects/my-awesome#read",
            "projects/awesome-project/services/foo-bar-service#read",
            False,
        ),
        (
            "projects/awesome-project/services#write",
            "projects/awesome-project/services/foo-bar-service#read",
            True,
        ),
        (
            "projects/awesome-project/services#write",
            "projects/awesome-project/files#read",
            False,
        ),
        (
            "projects/awesome-project/services:access#write",
            "projects/awesome-project/services#read",
            False,
        ),
        (
            "projects/awesome-project/services#read",
            "projects/awesome-project/services:access#read",
            True,
        ),
        (
            "*#read",
            "projects/awesome-project/services:access#read",
            True,
        ),
        (
            "projects#admin",
            "*#read",
            False,
        ),
    ],
)
def test_is_permission_granted(
    granted_permission: str,
    requested_permission: str,
    granted: bool,
) -> None:
    assert (
        auth_utils.is_permission_granted(granted_permission, requested_permission)
        == granted
    )
