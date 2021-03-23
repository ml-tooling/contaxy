from typing import Any

from fastapi import APIRouter, Depends, Response, status

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.schema import CoreOperations, SystemInfo, SystemStatistics

router = APIRouter(tags=["system"])


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
)
def get_system_statistics(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns statistics about this instance."""
    component_manager.get_auth_manager().verify_access(token, "system#admin")
    return component_manager.get_system_manager().get_system_statistics()
