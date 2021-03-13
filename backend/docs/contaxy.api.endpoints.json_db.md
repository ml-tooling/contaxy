<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/json_db.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.json_db`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/json_db.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_json_document`

```python
create_json_document(
    json_document: Dict,
    project_id: str = Path(Ellipsis),
    collection_id: str = Path(Ellipsis),
    key: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Creates a JSON document. If a document already exists for the given key, the document will be overwritten. 

If no collection exists in the project with the provided `collection_id`, a new collection will be created. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/json_db.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `update_json_document`

```python
update_json_document(
    json_document: Dict,
    project_id: str = Path(Ellipsis),
    collection_id: str = Path(Ellipsis),
    key: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Updates a JSON document. 

The update is applied on the existing document based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/json_db.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_json_documents`

```python
list_json_documents(
    project_id: str = Path(Ellipsis),
    collection_id: str = Path(Ellipsis),
    filter: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all JSON documents for the given project collection. 

If extensions are registered for this operation and no extension is selected via the `extension_id` parameter, the results from all extensions will be included in the returned list. 

The `filter` parameter allows to filter the result documents based on a JSONPath expression ([JSON Path Specification](https://goessner.net/articles/JsonPath/)). The filter is only applied to filter documents in the list. It is not usable to extract specific properties. 

# TODO: Add filter examples 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/json_db.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_json_document`

```python
get_json_document(
    project_id: str = Path(Ellipsis),
    collection_id: str = Path(Ellipsis),
    key: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns a single JSON document. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/json_db.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_json_document`

```python
delete_json_document(
    project_id: str = Path(Ellipsis),
    collection_id: str = Path(Ellipsis),
    key: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes a single JSON document. 

If no other document exists in the project collection, the collection will be deleted. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
