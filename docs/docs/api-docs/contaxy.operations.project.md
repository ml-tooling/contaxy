<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.project`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ProjectOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_project_member`

```python
add_project_member(
    project_id: str,
    user_id: str,
    access_level: AccessLevel
) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_project`

```python
create_project(
    project_input: ProjectCreation,
    technical_project: bool = False
) → Project
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_project`

```python
delete_project(project_id: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_project`

```python
get_project(project_id: str) → Project
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_project_members`

```python
list_project_members(project_id: str) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_projects`

```python
list_projects() → List[Project]
```

Returns all projects visible to the authenticated user. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_project_member`

```python
remove_project_member(project_id: str, user_id: str) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_project_id`

```python
suggest_project_id(display_name: str) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/project.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_project`

```python
update_project(project_id: str, project_input: ProjectInput) → Project
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
