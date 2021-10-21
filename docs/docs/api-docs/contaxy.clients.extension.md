<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.clients.extension`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionClient`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Session)
```






---

#### <kbd>property</kbd> client







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_extension`

```python
delete_extension(project_id: str, extension_id: Optional[str] = None) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_extension_metadata`

```python
get_extension_metadata(project_id: str, extension_id: str) → Extension
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `install_extension`

```python
install_extension(
    extension: ExtensionInput,
    project_id: str,
    request_kwargs: Dict = {}
) → Extension
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_extensions`

```python
list_extensions(project_id: str, request_kwargs: Dict = {}) → List[Extension]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/extension.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_extension_config`

```python
suggest_extension_config(container_image: str, project_id: str) → ExtensionInput
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
