from typing import Any

from fastapi import APIRouter, Depends

from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.schema import AccessLevel
from contaxy.schema.exceptions import VALIDATION_ERROR_RESPONSE, ClientBaseError

router = APIRouter(tags=["seed"], responses={**VALIDATION_ERROR_RESPONSE})


@router.get("/seed/default")
def create_seed_default(
    component_manager: ComponentManager = Depends(get_component_manager),
    # token: str = Depends(get_api_token),
) -> Any:
    # Don't use `verify_token` because that function wants to query the database and right now we don't have a user in the database on startup
    # access_token = component_manager.get_auth_manager()._resolve_token(
    #     token, use_cache=True
    # )
    # if "system#admin" not in access_token.scopes:
    #     raise ClientBaseError(
    #         403,
    #         message="No permission to create seed.",
    #         explanation="Only tokens with `system#admin` scope are permitted.",
    #     )

    seed_manager = component_manager.get_seed_manager()
    user = seed_manager.create_user()
    project = seed_manager.create_project()
    if not project or not project.id:
        raise ClientBaseError(status_code=500, message="Could not create seed data")
    component_manager.get_project_manager().add_project_member(
        project_id=project.id, user_id=user.id, access_level=AccessLevel.ADMIN
    )
    seed_manager.create_file(project_id=project.id)
