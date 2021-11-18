<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.components`




**Global Variables**
---------------
- **CORE_EXTENSION_ID**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L278"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `install_components`

```python
install_components() → None
```

Currently only a mock implementation. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ComponentManager`
Initializes and manages all platform components. 

The component manager is created for every request and will initialize all platform components based on the platform settings. It is the central point to access any other platform component. 

Individual components can store a global state via the `global_state` variable. This allows initializing certain objects (DB connections, HTTP clients, ...) only once per app instance (process) and share it with other components. 

There is also a `request_state` that can be used to share objects for a single request. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close() → None
```

Closes the component manager. 

This is called once the request is finished and will close the `request_state` and all its registered close callbacks. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_auth_manager`

```python
get_auth_manager() → AuthManager
```

Returns an Auth Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L168"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_manager`

```python
get_extension_manager() → ExtensionManager
```

Returns an Extension Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file_manager`

```python
get_file_manager(extension_id: Optional[str] = 'core') → FileOperations
```

Returns a File Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_manager`

```python
get_job_manager(extension_id: Optional[str] = 'core') → JobOperations
```

Returns a Job Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_json_db_manager`

```python
get_json_db_manager() → JsonDocumentOperations
```

Returns a JSON DB Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_project_manager`

```python
get_project_manager() → ProjectManager
```

Returns a Project Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L266"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_seed_manager`

```python
get_seed_manager() → SeedOperations
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_service_manager`

```python
get_service_manager(extension_id: Optional[str] = 'core') → ServiceOperations
```

Returns a Service Manager instance. 

Depending on the provided `extenion_id`, this is either the configured core component or an initialized extension client. 



**Args:**
 
 - <b>`extension_id`</b>:  ID of the requested extension. Use `core` for the platform components. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_system_manager`

```python
get_system_manager() → SystemManager
```

Returns a System Manager instance. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/components.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_access`

```python
verify_access(
    token: str,
    resource_name: Optional[str] = None,
    access_level: Optional[AccessLevel] = None
) → AuthorizedAccess
```

Verifies if the authorized token is valid and grants access to the specified resource. 

The token is verfied for its validity and - if provided - if it has the specified permission. 



**Args:**
 
 - <b>`token`</b>:  Token (session or API) to verify. 
 - <b>`resource_name`</b> (optional):  The access verification will check if the authroized subject is granted access to this resource.  If `None`, only the token will be checked for validity. 
 - <b>`access_level`</b> (optional):  The access verification will check if the authroized subject is allowed to access the resource at this level.  The access level has to be provided if the resource_name is used. 



**Raises:**
 
 - <b>`PermissionDeniedError`</b>:  If the requested permission is denied. 
 - <b>`UnauthenticatedError`</b>:  If the token is invalid or expired. 



**Returns:**
 
 - <b>`AuthorizedAccess`</b>:  Information about the granted permission, authenticated user, and the token. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
