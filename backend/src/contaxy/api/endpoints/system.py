import os
from typing import Any, List

from fastapi import APIRouter, Body, Depends, Form, Response, status
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from contaxy import config
from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.schema import CoreOperations, SystemInfo, SystemStatistics
from contaxy.schema.auth import AccessLevel
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
    ClientValueError,
)
from contaxy.schema.system import IMAGE_NAME_PARAM, AllowedImageInfo
from contaxy.utils.auth_utils import get_api_token

HERE = os.path.abspath(os.path.dirname(__file__))

templates = Jinja2Templates(directory=os.path.join(HERE, "templates"))

router = APIRouter(
    tags=["system"],
    responses={**VALIDATION_ERROR_RESPONSE},
)


@router.get(
    "/system/info",
    operation_id=CoreOperations.GET_SYSTEM_INFO.value,
    response_model=SystemInfo,
    summary="Get system info.",
    status_code=status.HTTP_200_OK,
)
def get_system_info(
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Returns information about this instance."""
    return component_manager.get_system_manager().get_system_info()


@router.get(
    "/system/health",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Check server health status.",
)
def check_health(
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Returns a successful return code if the instance is healthy."""
    if component_manager.get_system_manager().is_healthy():
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@router.get(
    "/system/statistics",
    operation_id=CoreOperations.GET_SYSTEM_STATISTICS.value,
    response_model=SystemStatistics,
    summary="Get system statistics.",
    status_code=status.HTTP_200_OK,
    responses={**AUTH_ERROR_RESPONSES},
)
def get_system_statistics(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns statistics about this instance."""
    component_manager.verify_access(token, "system", AccessLevel.READ)
    return component_manager.get_system_manager().get_system_statistics()


@router.post(
    "/system/initialize",
    operation_id=CoreOperations.INITIALIZE_SYSTEM.value,
    summary="Initialize the system.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def initialize_system(
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Initializes the system."""
    component_manager.get_system_manager().initialize_system()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/system/admin-form",
    include_in_schema=False,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def display_register_admin_form(
    request: Request,
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    if component_manager.get_auth_manager().list_users():
        logger.error("Admin user already exsists")
        return Response(status_code=status.HTTP_409_CONFLICT)

    route = os.path.join(
        config.settings.CONTAXY_BASE_URL,
        config.settings.CONTAXY_API_PATH,
        "system/admin",
    )
    if not route.startswith("/"):
        route = f"/{route}"

    # TODO: use request.url_for in template when settings.CONTAXY_API_PATH is set as root path in fastapi app
    return templates.TemplateResponse(
        "register-admin.html.j2",
        {
            "request": request,
            "route": route,
            "username": config.SYSTEM_ADMIN_USERNAME,
        },
    )


@router.post("/system/admin", status_code=status.HTTP_200_OK)
def register_admin_user(
    request: Request,
    password: str = Form(...),
    password_confirm: str = Form(...),
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    if component_manager.get_auth_manager().list_users():
        logger.error("Admin user already exsists")
        return Response(status_code=status.HTTP_409_CONFLICT)
    if password != password_confirm:
        return ClientValueError("The passwords do not match.")

    component_manager.get_system_manager().initialize_system(password)

    return templates.TemplateResponse(
        "register-admin-success.html.j2",
        {
            "request": request,
            "username": config.SYSTEM_ADMIN_USERNAME,
        },
    )


@router.post(
    "/system/allowed-images",
    operation_id=CoreOperations.ADD_ALLOWED_IMAGE.value,
    response_model=AllowedImageInfo,
    summary="Add an image to the list of allowed images or replace one already on the list.",
    status_code=status.HTTP_200_OK,
)
def add_allowed_image(
    allowed_image_input: AllowedImageInfo = Body(...),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    component_manager.verify_access(token, "system/allowed-images", AccessLevel.WRITE)
    return component_manager.get_system_manager().add_allowed_image(allowed_image_input)


@router.get(
    "/system/allowed-images",
    operation_id=CoreOperations.LIST_ALLOWED_IMAGES.value,
    response_model=List[AllowedImageInfo],
    summary="List all allowed images.",
    status_code=status.HTTP_200_OK,
)
def list_allowed_images(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    component_manager.verify_access(token, "system/allowed-images", AccessLevel.READ)
    return component_manager.get_system_manager().list_allowed_images()


@router.delete(
    "/system/allowed-images",
    operation_id=CoreOperations.DELETE_ALLOWED_IMAGE.value,
    summary="Remove an image from the list of allowed images.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_allowed_image(
    image_name: str = IMAGE_NAME_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    component_manager.verify_access(token, "system/allowed-images", AccessLevel.WRITE)
    component_manager.get_system_manager().delete_allowed_image(image_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
