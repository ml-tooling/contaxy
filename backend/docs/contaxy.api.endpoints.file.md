<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.file`




**Global Variables**
---------------
- **OPEN_URL_REDIRECT**
- **RESOURCE_ID_REGEX**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_files`

```python
list_files(
    project_id: str = Path(Ellipsis),
    recursive: bool = Query(True),
    include_versions: bool = Query(False),
    prefix: Optional[str] = Query(None),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all available files for the project. 

The files can be filtered by using a `prefix`. The prefix is applied on the full path (directory path + filename). 

All versions of the files can be included by setting `versions` to `true` (default is `false`). 

Set `recursive` to `false` to only show files and folders (prefixes) of the current folder. The current folder is either the root folder (`/`) or the folder selected by the `prefix` parameter (has to end with `/`). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `upload_file`

```python
upload_file(
    body: str = Body(Ellipsis),
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Uploads a file to a file storage. 

The file will be streamed to the selected file storage (core platform or extension). 

This upload operation only supports to attach a limited set of file metadata. Once the upload is finished, you can use the [update_file_metadata operation](#files/update_file_metadata) to add or update the metadata of the files. 

The `file_key` allows to categorize the uploaded file under a virtual file structure managed by the core platform. This allows to create a directory-like structure for files from different extensions and file-storage types. The actual file path on the file storage might not (and doesn't need to) correspond to the provided `file_key`. This allows to move files (via [update_file_metadata operation](#files/update_file_metadata)) into differnt paths without any changes on the file storage (depending on the implementation). 

Additional file metadata (`additional_metadata`) can be set by using the `x-amz-meta-` prefix for HTTP header keys (e.g. `x-amz-meta-my-metadata`). This corresponds to how AWS S3 handles [custom metadata](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L104"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_file_metadata`

```python
get_file_metadata(
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    version: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns metadata about the specified file. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `update_file_metadata`

```python
update_file_metadata(
    file: FileInput,
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    version: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Updates the file metadata. 

This will not change the actual content or the key of the file. 

The update is applied on the existing metadata based on the JSON Merge Patch Standard ([RFC7396](https://tools.ietf.org/html/rfc7396)). Thereby, only the specified properties will be updated. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L162"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `download_file`

```python
download_file(
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    version: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Downloads the selected file. 

If the file storage supports versioning and no `version` is specified, the latest version will be downloaded. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L189"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_file_actions`

```python
list_file_actions(
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    version: Optional[str] = Query(None),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all actions available for the specified file. 

The returned action IDs should be used when calling the [execute_file_action](#files/execute_file_action) operation. 

The action mechanism allows extensions to provide additional functionality on files. It works the following way: 

1. The user requests all available actions via the [list_file_actions](#files/list_file_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_file_actions](#files/list_file_actions) operation. 3. Extensions can run arbitrary code - e.g., request and check the file metadata for compatibility - and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [execute_file_action](#files/execute_file_action) operation by providing the selected action- and extension-ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action. 6. The return value of the operation can be either a simple message  (shown to the user) or a redirect to another URL (e.g., to show a web UI). 

The same action mechanism is also used for other resources (e.g., services, jobs). It can support a very broad set of use-cases, for example: CSV Viewer, Tensorflow Model Deployment, ZIP Archive Explorer ... 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L228"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `execute_file_action`

```python
execute_file_action(
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    action_id: str = Path(Ellipsis),
    version: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Executes the selected action. 

The actions need to be first requested from the [list_file_actions](#files/list_file_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_file_actions](#files/list_file_actions). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/file.py#L265"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_file`

```python
delete_file(
    project_id: str = Path(Ellipsis),
    file_key: str = Path(Ellipsis),
    version: Optional[str] = Query(None),
    keep_latest_version: Optional[bool] = Query(False),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes the specified file. 

If the file storage supports versioning and no `version` is specified, all versions of the file will be deleted. 

The parameter `keep_latest_version` is useful if you want to delete all older versions of a file. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
