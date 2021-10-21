<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.json_db.postgres`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PostgresJsonDocumentManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(global_state: GlobalState, request_state: RequestState)
```

Initializes the Postgres Json Document Manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_json_document`

```python
create_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: str,
    upsert: bool = True
) → JsonDocument
```

Creates a json document for a given key. 

An upsert strategy is used, i.e. if a document already exists for the given key it will be overwritten. The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`key`</b> (str):  Json Document Id, i.e. DB row key. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 
 - <b>`upsert`</b> (bool):  Indicates, wheter upsert strategy is used. 



**Raises:**
 
 - <b>`ClientValueError`</b>:  If the given json_document does not contain valid json. 
 - <b>`ResourceAlreadyExistsError`</b>:  If a document already exists for the given key and `upsert` is False. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The created Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_documents`

```python
delete_documents(project_id: str, collection_id: str, keys: List[str]) → int
```

Delete Json documents by key. 

The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`keys`</b> (List[str]):  Json Document Ids, i.e. DB row keys. 
 - <b>`json_document`</b> (Dict):  The actual Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L299"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_collection`

```python
delete_json_collection(project_id: str, collection_id: str) → None
```

Delete a JSON collection. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project ID associated with the collection. 
 - <b>`collection_id`</b> (str):  The collection to be deleted. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L282"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_collections`

```python
delete_json_collections(project_id: str) → None
```

Deletes all JSON collections for a project. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the collections. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
 
 - <b>`ResourceNotFoundError`</b>:  If no JSON document is found with the given `key`. 
 - <b>`ServerBaseError`</b>:  Document not deleted for an unknown reason. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
 
 - <b>`ResourceNotFoundError`</b>:  If no JSON document is found with the given `key`. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The requested Json document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_json_documents`

```python
list_json_documents(
    project_id: str,
    collection_id: str,
    filter: Optional[str] = None,
    keys: Optional[List[str]] = None
) → List[JsonDocument]
```

List all existing Json documents and optionally filter via Json Path syntax. 

 The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created. 



**Args:**
 
 - <b>`project_id`</b> (str):  Project Id, i.e. DB schema. 
 - <b>`collection_id`</b> (str):  Json document collection Id, i.e. DB table. 
 - <b>`filter`</b> (Optional[str], optional):  Json Path filter. Defaults to None. 
 - <b>`keys`</b> (Optional[List[str]], optional):  Json Document Ids, i.e. DB row keys. Defaults to None. 



**Raises:**
 
 - <b>`ClientValueError`</b>:  If filter is provided and does not contain a valid Json Path filter. 



**Returns:**
 
 - <b>`List[JsonDocument]`</b>:  List of Json documents. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/json_db/postgres.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_json_document`

```python
update_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: str
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
 
 - <b>`ResourceNotFoundError`</b>:  If no JSON document is found with the given `key`. 
 - <b>`ServerBaseError`</b>:  Document not updatded for an unknown reason. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The updated document. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
