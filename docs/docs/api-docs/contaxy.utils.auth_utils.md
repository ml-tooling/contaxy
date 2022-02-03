<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.utils.auth_utils`




**Global Variables**
---------------
- **USER_ROLE**
- **USERS_KIND**
- **PERMISSION_SEPERATOR**
- **RESOURCE_WILDCARD**
- **ACCESS_LEVEL_MAPPING**
- **ACCESS_LEVEL_REVERSE_MAPPING**
- **value**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_valid_permission`

```python
is_valid_permission(permission_str: str) → bool
```

Returns `True` if the `permission_str` is valid permission. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_jwt_token`

```python
is_jwt_token(token: str) → bool
```

Returns `True` if the provided token is an JWT token. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `construct_permission`

```python
construct_permission(resource_name: str, access_level: AccessLevel) → str
```

Constructs a permission based on the provided `resource_name`  and `access_level`. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `parse_permission`

```python
parse_permission(permission: str) → Tuple[str, AccessLevel]
```

Extracts the resource name and access level from a permission. 



**Args:**
 
 - <b>`permission`</b>:  The permission to parse. 



**Raises:**
 
 - <b>`ClientValueError`</b>:  If the permission cannot be parsed. 



**Returns:**
 
 - <b>`Tuple[str, AccessLevel]`</b>:  The extracted resource name and access level. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_access_level_granted`

```python
is_access_level_granted(
    granted_access_level: AccessLevel,
    requested_access_level: AccessLevel
) → bool
```

Checks if the requested access level is allowed by the granted access level. 



**Args:**
 
 - <b>`granted_access_level`</b>:  The access level that is already granted. 
 - <b>`requested_access_level`</b>:  The access level to check against the granted level. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the access level is granted. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_permission_granted`

```python
is_permission_granted(granted_permission: str, requested_permission: str) → bool
```

Checks if the requested permission is allowed by the granted permission. 



**Args:**
 
 - <b>`granted_permission`</b>:  The permission that is already granted. 
 - <b>`requested_permission`</b>:  The permission to check against the granted permission 



**Raises:**
 
 - <b>`ClientValueError`</b>:  If one of the permissions cannot be parsed. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the permission is granted. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_and_setup_user`

```python
create_and_setup_user(
    user_input: UserRegistration,
    auth_manager: AuthOperations,
    project_manager: ProjectOperations,
    technical_user: bool = False
) → User
```

Create a new user and setup default project and permissions. 



**Args:**
 
 - <b>`user_input`</b> (UserRegistration):  Information required for creating a new user. 
 - <b>`auth_manager`</b> (AuthOperations):  The auth manager used to setup default permissions. 
 - <b>`project_manager`</b> (ProjectOperations):  The project manager used to create the default user project. 



**Raises:**
 
 - <b>`ResourceAlreadyExistsError`</b>:  If the user already exists 



**Returns:**
 
 - <b>`User`</b>:  The newly created and setup user 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/auth_utils.py#L204"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `parse_userid_from_resource_name`

```python
parse_userid_from_resource_name(user_resource_name: str) → str
```

Returns the user id from a user-resource name. 

For example, 'users/abcd' returns 'abcd' as 'users' is the prefix. 



**Args:**
 
 - <b>`user_resource_name`</b> (str):  The resource name, e.g. 'users/abcd'. 



**Returns:**
 
 - <b>`str`</b>:  The user id in the user-resource name or an empty string. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
