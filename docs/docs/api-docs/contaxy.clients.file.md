<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.clients.file`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FileClient`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Session)
```








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_file`

```python
delete_file(
    project_id: str,
    file_key: str,
    version: Optional[str] = None,
    keep_latest_version: bool = False,
    request_kwargs: Dict = {}
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_files`

```python
delete_files(project_id: str, request_kwargs: Dict = {}) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `download_file`

```python
download_file(
    project_id: str,
    file_key: str,
    version: Optional[str] = None,
    request_kwargs: Dict = {}
) → Iterator[bytes]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_file_action`

```python
execute_file_action(
    project_id: str,
    file_key: str,
    action_id: str,
    version: Optional[str] = None,
    request_kwargs: Dict = {}
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file_metadata`

```python
get_file_metadata(
    project_id: str,
    file_key: str,
    version: Optional[str] = None,
    request_kwargs: Dict = {}
) → File
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L151"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_file_actions`

```python
list_file_actions(
    project_id: str,
    file_key: str,
    version: Optional[str] = None,
    request_kwargs: Dict = {}
) → List[ResourceAction]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_files`

```python
list_files(
    project_id: str,
    recursive: bool = True,
    include_versions: bool = False,
    prefix: Optional[str] = None,
    request_kwargs: Dict = {}
) → List[File]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_file_metadata`

```python
update_file_metadata(
    file: FileInput,
    project_id: str,
    file_key: str,
    version: Optional[str] = None,
    request_kwargs: Dict = {}
) → File
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/file.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upload_file`

```python
upload_file(
    project_id: str,
    file_key: str,
    file_stream: FileStream,
    content_type: str = 'application/octet-stream',
    request_kwargs: Dict = {}
) → File
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
