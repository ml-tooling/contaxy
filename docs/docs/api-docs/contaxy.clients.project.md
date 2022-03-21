<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.clients.project`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ProjectClient`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Session)
```








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_project_member`

```python
add_project_member(
    project_id: str,
    user_id: str,
    access_level: AccessLevel,
    request_kwargs: Dict = {}
) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_project`

```python
create_project(
    project_input: ProjectCreation,
    technical_project: bool = False,
    request_kwargs: Dict = {}
) → Project
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_project`

```python
delete_project(project_id: str, request_kwargs: Dict = {}) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_project`

```python
get_project(project_id: str, request_kwargs: Dict = {}) → Project
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_project_token`

```python
get_project_token(
    project_id: str,
    access_level: AccessLevel = <AccessLevel.WRITE: 'write'>,
    request_kwargs: Dict = {}
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_project_members`

```python
list_project_members(project_id: str, request_kwargs: Dict = {}) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_projects`

```python
list_projects(request_kwargs: Dict = {}) → List[Project]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_project_member`

```python
remove_project_member(
    project_id: str,
    user_id: str,
    request_kwargs: Dict = {}
) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_project_id`

```python
suggest_project_id(display_name: str, request_kwargs: Dict = {}) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/project.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_project`

```python
update_project(
    project_id: str,
    project_input: ProjectInput,
    request_kwargs: Dict = {}
) → Project
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
