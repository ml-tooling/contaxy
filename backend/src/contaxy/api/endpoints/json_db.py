import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from contaxy.api.dependencies import (
    ComponentManager,
    get_api_token,
    get_component_manager,
)
from contaxy.schema import CoreOperations, JsonDocument
from contaxy.schema.auth import AccessLevel
from contaxy.schema.project import PROJECT_ID_PARAM

router = APIRouter(
    tags=["json"],
    responses={
        401: {"detail": "No API token was provided."},
        403: {"detail": "Forbidden - the user is not authorized to use this resource."},
    },
)


@router.put(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=CoreOperations.CREATE_JSON_DOCUMENT.value,
    summary="Create JSON document.",
    response_model=JsonDocument,
    status_code=status.HTTP_200_OK,
)
def create_json_document(
    json_document: Dict,
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Creates a JSON document. If a document already exists for the given key, the document will be overwritten.

    If no collection exists in the project with the provided `collection_id`, a new collection will be created.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/json/{collection_id}/{key}", AccessLevel.WRITE
    )
    return component_manager.get_json_db_manager().create_json_document(
        project_id, collection_id, key, json.dumps(json_document)
    )


@router.patch(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=CoreOperations.UPDATE_JSON_DOCUMENT.value,
    summary="Update a JSON document.",
    response_model=JsonDocument,
    status_code=status.HTTP_200_OK,
)
def update_json_document(
    json_document: Dict,
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Updates a JSON document.

    The update is applied on the existing document based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396).
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/json/{collection_id}/{key}", AccessLevel.WRITE
    )

    return component_manager.get_json_db_manager().update_json_document(
        project_id, collection_id, key, json.dumps(json_document)
    )


@router.get(
    "/projects/{project_id}/json/{collection_id}",
    operation_id=CoreOperations.LIST_JSON_DOCUMENTS.value,
    response_model=List[JsonDocument],
    summary="List JSON documents.",
    status_code=status.HTTP_200_OK,
)
def list_json_documents(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    filter: Optional[str] = Query(
        None, description="JSON Path query used to filter the results."
    ),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Lists all JSON documents for the given project collection.

    If extensions are registered for this operation and no extension is selected via the `extension_id` parameter, the results from all extensions will be included in the returned list.

    The `filter` parameter allows to filter the result documents based on a JSONPath expression ([JSON Path Specification](https://goessner.net/articles/JsonPath/)). The filter is only applied to filter documents in the list. It is not usable to extract specific properties.

    # TODO: Add filter examples
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/json/{collection_id}", AccessLevel.READ
    )

    return component_manager.get_json_db_manager().list_json_documents(
        project_id, collection_id, filter
    )


@router.get(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=CoreOperations.GET_JSON_DOCUMENT.value,
    response_model=JsonDocument,
    summary="Get JSON document.",
    status_code=status.HTTP_200_OK,
)
def get_json_document(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Returns a single JSON document."""

    component_manager.verify_access(
        token, f"projects/{project_id}/json/{collection_id}/{key}", AccessLevel.READ
    )

    return component_manager.get_json_db_manager().get_json_document(
        project_id, collection_id, key
    )


@router.delete(
    "/projects/{project_id}/json/{collection_id}/{key}",
    operation_id=CoreOperations.DELETE_JSON_DOCUMENT.value,
    summary="Delete JSON document.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_json_document(
    project_id: str = PROJECT_ID_PARAM,
    collection_id: str = Path(..., description="ID of the collection."),
    key: str = Path(..., description="Key of the JSON document."),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Deletes a single JSON document.

    If no other document exists in the project collection, the collection will be deleted.
    """
    component_manager.verify_access(
        token, f"projects/{project_id}/json/{collection_id}/{key}", AccessLevel.WRITE
    )

    return component_manager.get_json_db_manager().delete_json_document(
        project_id, collection_id, key
    )
