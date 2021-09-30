<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.system`




**Global Variables**
---------------
- **ADMIN_ROLE**
- **USERS_KIND**


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SystemManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    global_state: GlobalState,
    request_state: RequestState,
    json_db_manager: JsonDocumentOperations,
    auth_manager: AuthManager,
    project_manager: ProjectOperations
)
```

Initializes the system manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 
 - <b>`json_db_manager`</b>:  Json document manager instance. 
 - <b>`auth_manager`</b>:  Auth manager instance. 
 - <b>`project_manager`</b>:  Project manager instance. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_system_info`

```python
get_system_info() → SystemInfo
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_system_statistics`

```python
get_system_statistics() → SystemStatistics
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `initialize_system`

```python
initialize_system(password: Optional[str] = None) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/system.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_healthy`

```python
is_healthy() → bool
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
