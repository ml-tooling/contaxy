from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.schema import CoreOperations, SystemInfo, SystemStatistics
from contaxy.schema.exceptions import PermissionDeniedException

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
    # TODO: this call can also be made without authentication
    raise PermissionDeniedException()


@router.get(
    "/system/health",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Check server health status.",
)
def check_health(
    component_manager: ComponentManager = Depends(get_component_manager),
) -> Any:
    """Returns a successful return code if the instance is healthy."""
    # TODO: this call can also be made without authentication
    raise NotImplementedError


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
    raise NotImplementedError
