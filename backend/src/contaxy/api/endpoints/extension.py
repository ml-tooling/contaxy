from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from contaxy.api.dependencies import ComponentManager, get_component_manager
from contaxy.schema import CoreOperations, Extension, ExtensionInput
from contaxy.schema.auth import AccessLevel
from contaxy.schema.exceptions import (
    AUTH_ERROR_RESPONSES,
    CREATE_RESOURCE_RESPONSES,
    GET_RESOURCE_RESPONSES,
    VALIDATION_ERROR_RESPONSE,
)
from contaxy.schema.extension import GLOBAL_EXTENSION_PROJECT
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.utils.auth_utils import get_api_token

router = APIRouter(
    tags=["extensions"],
    responses={**AUTH_ERROR_RESPONSES, **VALIDATION_ERROR_RESPONSE},
)


@router.get(
    "/projects/{project_id}/extensions",
    operation_id=CoreOperations.LIST_EXTENSIONS.value,
    response_model=List[Extension],
    summary="List extensions.",
    status_code=status.HTTP_200_OK,
)
def list_extensions(
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns all installed extensions accesible by the specified project.

    This also includes all extensions which are installed globally as well as
    extensions installed by the authorized user.
    """

    component_manager.verify_access(
        token,
        f"/projects/{project_id}/extensions",
        AccessLevel.READ,
    )

    return component_manager.get_extension_manager().list_extensions(
        project_id=project_id
    )


@router.delete(
    "/projects/{project_id}/extensions/{extension_id}",
    operation_id=CoreOperations.DELETE_EXTENSION.value,
    summary="Delete extension.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_extension(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: Optional[str] = Path(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes an extension.

    This will delete the installation metadata as well as the service container.
    """
    raise NotImplementedError


@router.get(
    "/projects/{project_id}/extensions/{extension_id}",
    operation_id=CoreOperations.GET_EXTENSION_METADATA.value,
    response_model=Extension,
    summary="Get extension metadata.",
    status_code=status.HTTP_200_OK,
    responses={**GET_RESOURCE_RESPONSES},
)
def get_extension_metadata(
    project_id: str = PROJECT_ID_PARAM,
    extension_id: str = Path(
        ...,
        title="Extension ID",
        description="A valid extension ID.",
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns the metadata of the given extension."""
    raise NotImplementedError


@router.post(
    "/projects/{project_id}/extensions",
    operation_id=CoreOperations.INSTALL_EXTENSION.value,
    response_model=Extension,
    summary="Install extension.",
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def install_extension(
    extension: ExtensionInput,
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Installs an extension for the given project.

    This will deploy the extension container for the selected project and
    registers the extension for all the specified capabilities.
    """

    # Only admins can install "global" extensions that are shown for every user
    if project_id == GLOBAL_EXTENSION_PROJECT:
        component_manager.verify_access(token, "*", AccessLevel.ADMIN)
    else:
        component_manager.verify_access(
            token,
            f"/projects/{project_id}/extensions",
            AccessLevel.WRITE,
        )

    return component_manager.get_extension_manager().install_extension(
        extension=extension, project_id=project_id
    )


@router.get(
    "/projects/{project_id}/extensions:suggest-config",
    operation_id=CoreOperations.SUGGEST_EXTENSION_CONFIG.value,
    response_model=ExtensionInput,
    summary="Suggest extension configuration.",
    status_code=status.HTTP_200_OK,
)
def suggest_extension_config(
    container_image: str = Query(
        ..., description="Container image to use for suggestion."
    ),
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Suggests an input configuration based on the provided `container_image`.

    The suggestion is based on metadata extracted from the container image (e.g. labels)
    as well as suggestions based on previous project deployments with the same image.
    """
    raise NotImplementedError
