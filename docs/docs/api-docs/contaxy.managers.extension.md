<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.extension`




**Global Variables**
---------------
- **CORE_EXTENSION_ID**
- **COMPOSITE_ID_SEPERATOR**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `parse_composite_id`

```python
parse_composite_id(composite_id: str) → Tuple[str, Union[str, NoneType]]
```

Extracts the resource and extension ID from an composite ID. 

If the provided ID does not contain an composite ID seperator (`~`) the ID will be returned as resource ID and the extension ID will be `None`. 



**Args:**
 
 - <b>`composite_id`</b> (str):  The ID to parse. 



**Returns:**
 
 - <b>`Tuple[str, str]`</b>:  Resource ID, Extension ID 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionClient`
Handels the request forwarding to the installed extensions. 

The extension client implements all extensible manager interfaces and uses the generated HTTP client to forward requests to the respective extension. 

Extension clients are initialized and managed by the `ExtensionManager`. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(global_state: GlobalState, request_state: RequestState)
```

Initializes the extension client. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionManager`
Installs and manages extensions. 

The extension manager implements all methods for the full extension lifecycle. It is the central entry point for all interactions with extensions. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(global_state: GlobalState, request_state: RequestState)
```

Initializes the extension manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_default_extension`

```python
get_default_extension(operation: ExtensibleOperations) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_client`

```python
get_extension_client(extension_id: str) → ExtensionClient
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
