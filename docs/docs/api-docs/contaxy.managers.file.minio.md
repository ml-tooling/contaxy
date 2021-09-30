<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/file/minio.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.file.minio`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/file/minio.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MinioFileManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/file/minio.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    global_state: GlobalState,
    request_state: RequestState,
    json_db_manager: JsonDocumentOperations
)
```

Initializes the Minio File Manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 
 - <b>`json_db_manager`</b>:  JSON DB Manager instance to store structured data. 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
