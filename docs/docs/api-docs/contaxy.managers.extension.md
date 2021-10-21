<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.extension`




**Global Variables**
---------------
- **CORE_EXTENSION_ID**
- **GLOBAL_EXTENSION_PROJECT**
- **COMPOSITE_ID_SEPERATOR**
- **CAPABILITIES_METADATA_SEPARATOR**
- **METADATA_UI_EXTENSION_ENDPOINT**
- **METADATA_API_EXTENSION_ENDPOINT**
- **METADATA_CAPABILITIES**
- **METADATA_EXTENSION_TYPE**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_service_to_extension`

```python
map_service_to_extension(service: Service, user_id: str) → Extension
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionClient`
Handels the request forwarding to the installed extensions. 

The extension client implements all extensible manager interfaces and uses the generated HTTP client to forward requests to the respective extension. 

Extension clients are initialized and managed by the `ExtensionManager`. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(endpoint_url: str, access_token: Optional[str] = None)
```

Initializes the extension client. 



**Args:**
 
 - <b>`endpoint_url`</b>:  The endpoint base URL of the extension. 
 - <b>`access_token`</b>:  An access token that is attached to all requests. 


---

#### <kbd>property</kbd> client








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionManager`
Installs and manages extensions. 

The extension manager implements all methods for the full extension lifecycle. It is the central entry point for all interactions with extensions. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    global_state: GlobalState,
    request_state: RequestState,
    deployment_manager: DeploymentManager
)
```

Initializes the extension manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 
 - <b>`deployment_manager`</b>:  The current deployment manager instance. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_extension`

```python
delete_extension(project_id: str, extension_id: Optional[str] = None) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_default_extension`

```python
get_default_extension(operation: ExtensibleOperations) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_client`

```python
get_extension_client(extension_id: str) → ExtensionClient
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L192"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_metadata`

```python
get_extension_metadata(project_id: str, extension_id: str) → Extension
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L195"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `install_extension`

```python
install_extension(extension: ExtensionInput, project_id: str) → Extension
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_extensions`

```python
list_extensions(project_id: str) → List[Extension]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L226"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_extension_config`

```python
suggest_extension_config(container_image: str, project_id: str) → ExtensionInput
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
