<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.file`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FileStream`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `read`

```python
read(size: int = -1) → bytes
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FileOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_file`

```python
delete_file(
    project_id: str,
    file_key: str,
    version: Optional[str] = None,
    keep_latest_version: bool = False
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `download_file`

```python
download_file(
    project_id: str,
    file_key: str,
    version: Optional[str] = None
) → Iterator[bytes]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_file_action`

```python
execute_file_action(
    project_id: str,
    file_key: str,
    action_id: str,
    version: Optional[str] = None
) → Response
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file_metadata`

```python
get_file_metadata(
    project_id: str,
    file_key: str,
    version: Optional[str] = None
) → File
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_file_actions`

```python
list_file_actions(
    project_id: str,
    file_key: str,
    version: Optional[str] = None
) → ResourceAction
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_files`

```python
list_files(
    project_id: str,
    recursive: bool = True,
    include_versions: bool = False,
    prefix: Optional[str] = None
) → List[File]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_file_metadata`

```python
update_file_metadata(
    file: FileInput,
    project_id: str,
    file_key: str,
    version: Optional[str] = None
) → File
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/file.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upload_file`

```python
upload_file(
    project_id: str,
    file_key: str,
    file_stream: FileStream,
    content_type: str = 'application/octet-stream'
) → File
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
