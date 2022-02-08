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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_service_to_extension`

```python
map_service_to_extension(service: Service, user_id: str) → Extension
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionClient`
Handels the request forwarding to the installed extensions. 

The extension client implements all extensible manager interfaces and uses the generated HTTP client to forward requests to the respective extension. 

Extension clients are initialized and managed by the `ExtensionManager`. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionManager`
Installs and manages extensions. 

The extension manager implements all methods for the full extension lifecycle. It is the central entry point for all interactions with extensions. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(component_manager: ComponentOperations)
```

Initializes the extension manager. 



**Args:**
 
 - <b>`component_manager`</b>:  Instance of the component manager that grants access to the other managers. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L189"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_extension`

```python
delete_extension(project_id: str, extension_id: Optional[str] = None) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L186"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_default_extension`

```python
get_default_extension(operation: ExtensibleOperations) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_client`

```python
get_extension_client(extension_id: str) → ExtensionClient
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L194"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_metadata`

```python
get_extension_metadata(project_id: str, extension_id: str) → Extension
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `install_extension`

```python
install_extension(extension: ExtensionInput, project_id: str) → Extension
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_extensions`

```python
list_extensions(project_id: str) → List[Extension]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/extension.py#L228"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_extension_config`

```python
suggest_extension_config(container_image: str, project_id: str) → ExtensionInput
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
