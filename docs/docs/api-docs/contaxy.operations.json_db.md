<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.json_db`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `JsonDocumentOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

Creates a JSON document for a given key. 

If a document already exists for the given key, the document will be overwritten if `upsert` is True, otherwise an error is raised. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the collection. 
 - <b>`collection_id`</b>:  ID of the collection (database) to use to store this JSON document. 
 - <b>`key`</b>:  Key of the JSON document. 
 - <b>`json_document`</b>:  The actual JSON document value. 
 - <b>`upsert`</b>:  If `True`, the document will be updated/overwritten if it already exists. 



**Raises:**
 
 - <b>`ClientValueError`</b>:  If the given json_document does not contain valid json. 
 - <b>`ResourceAlreadyExistsError`</b>:  If a document already exists for the given key and `upsert` is False. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The created JSON document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L142"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_collection`

```python
delete_json_collection(project_id: str, collection_id: str) → None
```

Deletes all documents of a single JSON collection. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the collection. 
 - <b>`collection_id`</b>:  ID of the JSON collection (database). 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_collections`

```python
delete_json_collections(project_id: str) → None
```

Deletes all JSON collections for a project. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the collections. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_json_document`

```python
delete_json_document(project_id: str, collection_id: str, key: str) → None
```

Deletes a single JSON document. 

If no other document exists in the project collection, the collection will be deleted. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the JSON document. 
 - <b>`collection_id`</b>:  ID of the collection (database) that the JSON document is stored in. 
 - <b>`key`</b>:  Key of the JSON document. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no JSON document is found with the given `key`. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_json_document`

```python
get_json_document(project_id: str, collection_id: str, key: str) → JsonDocument
```

Returns a single JSON document. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the JSON document. 
 - <b>`collection_id`</b>:  ID of the collection (database) that the JSON document is stored in. 
 - <b>`key`</b>:  Key of the JSON document. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no JSON document is found with the given `key`. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  A JSON document. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_json_documents`

```python
list_json_documents(
    project_id: str,
    collection_id: str,
    filter: Optional[str] = None,
    keys: Optional[List[str]] = None
) → List[JsonDocument]
```

Lists all JSON documents for the given project collection. 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the collection. 
 - <b>`collection_id`</b>:  ID of the collection (database) that the JSON document is stored in. 
 - <b>`filter`</b> (optional):  Allows to filter the result documents based on a JSONPath expression ([JSON Path Specification](https://goessner.net/articles/JsonPath/)). The filter is only applied to filter documents in the list. It is not usable to extract specific properties. 
 - <b>`keys`</b> (Optional[List[str]], optional):  Json Document Ids, i.e. DB row keys. Defaults to None. 



**Raises:**
 
 - <b>`ClientValueError`</b>:  If filter is provided and does not contain a valid Json Path filter. 



**Returns:**
 
 - <b>`List[JsonDocument]`</b>:  List of JSON documents. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/json_db.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_json_document`

```python
update_json_document(
    project_id: str,
    collection_id: str,
    key: str,
    json_document: str
) → JsonDocument
```

Updates a JSON document. 

The update is applied on the existing document based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396). 



**Args:**
 
 - <b>`project_id`</b>:  Project ID associated with the collection. 
 - <b>`collection_id`</b>:  ID of the collection (database) that the JSON document is stored in. 
 - <b>`key`</b>:  Key of the JSON document. 
 - <b>`json_document`</b>:  The actual JSON document value. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no JSON document is found with the given `key`. 



**Returns:**
 
 - <b>`JsonDocument`</b>:  The updated JSON document. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
