<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.json_db.postgres`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PostgresJsonDocumentManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(global_state: GlobalState, request_state: RequestState)
```

Initializes the Postgres Json Document Manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_json_document`

```python
create_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: Dict
) → JsonDocument
```

Creates a json document for a given key. 

An upsert strategy is used, i.e. if a document already exists for the given key it will be overwritten. The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`key`</b> (str):  Json Document Id, i.e. DB row key. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The created Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L230"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_documents`

```python
delete_documents(project_id: str, collection_id: str, keys: List[str])
```

Delete Json documents by key. 

The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`keys`</b> (List[str]):  Json Document Ids, i.e. DB row keys. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_document`

```python
delete_json_document(project_id: str, collection_id: str, key: str) → None
```

Delete a Json document by key. 

The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`key`</b> (str):  Json Document Id, i.e. DB row key. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 



**Raises:**
 
 - <b>`ValueError`</b>:  No document found for the given key. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_json_document`

```python
get_json_document(project_id: str, collection_id: str, key: str) → JsonDocument
```

Get a Json document by key. 

The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`key`</b> (str):  Json Document Id, i.e. DB row key. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 



**Raises:**
 
 - <b>`ValueError`</b>:  No document found for the given key. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The requested Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_json_documents`

```python
get_json_documents(
    project_id: str,
    collection_id: str,
    keys: List[str]
) → List[JsonDocument]
```

Get multiple Json documents by key. 

The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`keys`</b> (List[str]):  Json Document Ids, i.e. DB row keys. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The requested Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_json_documents`

```python
list_json_documents(
    project_id: str,
    collection_id: str,
    filter: Optional[str] = None
) → List[JsonDocument]
```

List all existing Json documents and optionally filter via Json Path syntax. 

 The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`filter`</b> (Optional[str], optional):  Json Path filter. Defaults to None. 



**Raises:**
 
 - <b>`ValueError`</b>:  If filter is provided and does not contain a valid Json Path filter. 



**Returns:**
 
 - <b>`List[JsonDocument]`</b>:  List of Json documents. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_json_document`

```python
update_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: dict
) → JsonDocument
```

Updates a Json document via Json Merge Patch strategy. 

The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`key`</b> (str):  Json Document Id, i.e. DB row key. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 



**Raises:**
 
 - <b>`ValueError`</b>:  No document found for the given key. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The updated document. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
