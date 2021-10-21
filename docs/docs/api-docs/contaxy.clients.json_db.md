<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.clients.json_db`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `JsonDocumentClient`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Session)
```








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_json_document`

```python
create_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: str,
    upsert: bool = True,
    request_kwargs: Dict = {}
) → JsonDocument
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_collection`

```python
delete_json_collection(
    project_id: str,
    collection_id: str,
    request_kwargs: Dict = {}
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_collections`

```python
delete_json_collections(project_id: str, request_kwargs: Dict = {}) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_document`

```python
delete_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    request_kwargs: Dict = {}
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_json_document`

```python
get_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    request_kwargs: Dict = {}
) → JsonDocument
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_json_documents`

```python
list_json_documents(
    project_id: str,
    collection_id: str,
    filter: Optional[str] = None,
    keys: Optional[List[str]] = None,
    request_kwargs: Dict = {}
) → List[JsonDocument]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/json_db.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_json_document`

```python
update_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: str,
    request_kwargs: Dict = {}
) → JsonDocument
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
