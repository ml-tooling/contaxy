<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.user`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_users`

```python
list_users(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all users that are visible to the authenticated user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_user`

```python
create_user(
    user: UserRegistration,
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Creates a user. 

If the `password` is not provided, the user can only login by using other methods (social login). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_my_user`

```python
get_my_user(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the user metadata from the authenticated user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_user`

```python
get_user(
    user_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the user metadata for a single user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `update_user`

```python
update_user(
    user: UserInput,
    user_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Updates the user metadata. 

This will update only the properties that are explicitly set in the patch request. The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/user.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_user`

```python
delete_user(
    user_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes a user and all resources which are only accesible by this user. 

Shared project resources will not be deleted. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
