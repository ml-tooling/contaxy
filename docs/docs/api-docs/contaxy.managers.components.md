<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.components`




**Global Variables**
---------------
- **CORE_EXTENSION_ID**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L230"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `install_components`

```python
install_components() → None
```

Currently only a mock implementation. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ComponentManager`
Initializes and manages all platform components. 

The component manager is created for every request and will initialize all platform components based on the platform settings. It is the central point to access any other platform component. 

Individual components can store a global state via the `global_state` variable. This allows initializing certain objects (DB connections, HTTP clients, ...) only once per app instance (process) and share it with other components. 

There is also a `request_state` that can be used to share objects for a single request. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(request: Request)
```

Initializes the component manager. 



**Args:**
 
 - <b>`request`</b>:  Current request. 


---

#### <kbd>property</kbd> global_state





---

#### <kbd>property</kbd> request_state







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close() → None
```

Closes the component manager. 

This is called once the request is finished and will close the `request_state` and all its registered close callbacks. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_auth_manager`

```python
get_auth_manager() → AuthManager
```

Returns an Auth Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_manager`

```python
get_extension_manager() → ExtensionManager
```

Returns an Extension Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file_manager`

```python
get_file_manager(extension_id: Optional[str] = 'core') → FileOperations
```

Returns a File Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L195"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_manager`

```python
get_job_manager(extension_id: Optional[str] = 'core') → JobOperations
```

Returns a Job Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_json_db_manager`

```python
get_json_db_manager(
    extension_id: Optional[str] = 'core'
) → JsonDocumentOperations
```

Returns a JSON DB Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_project_manager`

```python
get_project_manager() → ProjectManager
```

Returns a Project Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L212"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_service_manager`

```python
get_service_manager(extension_id: Optional[str] = 'core') → ServiceOperations
```

Returns a Service Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_system_manager`

```python
get_system_manager() → SystemManager
```

Returns a System Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user_manager`

```python
get_user_manager() → UserManager
```

Returns a User Manager instance. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
