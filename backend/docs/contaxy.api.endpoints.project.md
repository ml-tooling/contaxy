<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.project`




**Global Variables**
---------------
- **MAX_DISPLAY_NAME_LENGTH**
- **MIN_DISPLAY_NAME_LENGTH**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_project`

```python
create_project(
    project: ProjectInput,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Creates a new project. 

We suggest to use the `suggest_project_id` endpoint to get a valid and available ID. The project ID might also be set manually, however, an error will be returned if it does not comply with the ID requirements or is already used. TODO: put method? 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `update_project`

```python
update_project(
    project: ProjectInput,
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Updates the metadata of the given project. 

This will update only the properties that are explicitly set in the patch request. The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_projects`

```python
list_projects(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all projects visible to the authenticated user. 

A project is visible to a user, if the user has the atleast a `read` permission for the project. System adminstrators will also see technical projects, such as `system-internal` and `system-global`. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_project`

```python
get_project(
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the metadata of a single project. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `suggest_project_id`

```python
suggest_project_id(
    display_name: str = Query(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Suggests a valid and unique project ID for the given display name. 

The project ID will be human-readable and resemble the provided display name, but might be cut off or have an attached counter prefix. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L125"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_project`

```python
delete_project(
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes a project and all its associated resources including deployments and files. 

A project can only be delete by a user with `admin` permission on the project. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_project_members`

```python
list_project_members(
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all project members. 

This include all users that have atlease a `read` permission on the given project. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L162"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `add_project_member`

```python
add_project_member(
    project_id: str = Path(Ellipsis),
    user_id: str = Path(Ellipsis),
    permission_level: Optional[AccessLevel] = Query(write),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Adds a user to the project. 

This will add the permission for this project to the user item. The `permission_level` defines what the user can do: 

- The `read` permission level allows read-only access on all resources. - The `write` permission level allows to create and delete project resources. - The `admin` permission level allows to delete the project or add/remove other users. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/project.py#L192"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `remove_project_member`

```python
remove_project_member(
    project_id: str = Path(Ellipsis),
    user_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Removes a user from a project. 

This will remove the permission for this project from the user item. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
