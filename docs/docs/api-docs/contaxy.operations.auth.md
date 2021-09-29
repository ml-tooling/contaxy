<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.auth`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_permission`

```python
add_permission(resource_name: str, permission: str) → None
```

Grants a permission to the specified resource. 



**Args:**
 
 - <b>`resource_name`</b>:  The resource name that the permission is granted to. 
 - <b>`permission`</b>:  The permission to grant to the specified resource. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `change_password`

```python
change_password(user_id: str, password: str) → None
```

Changes the password of a given user. 

The password is stored as a hash. 



**Args:**
 
 - <b>`user_id`</b>:  The ID of the user. 
 - <b>`password`</b>:  The new password to apply for the user. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_token`

```python
create_token(
    authorized_token: str,
    scopes: Optional[List[str]] = None,
    token_type: TokenType = <SESSION_TOKEN: 'session-token'>,
    description: Optional[str] = None
) → str
```

Returns a session or API token with access to the speicfied scopes. 



**Args:**
 
 - <b>`authorized_token`</b>:  The authorized token used to create the new token. 
 - <b>`scopes`</b> (optional):  Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token. 
 - <b>`token_type`</b> (optional):  The type of the token. Defaults to `TokenType.SESSION_TOKEN`. 
 - <b>`description`</b> (optional):  A short description about the generated token. 



**Raises:**
 PermissionDeniedError: 
 - <b>`UnauthenticatedError`</b>:  If the token is invalid or expired. 



**Returns:**
 
 - <b>`str`</b>:  The created session or API token. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_permissions`

```python
list_permissions(resource_name: str, resolve_groups: bool = True) → List[str]
```

Returns all permissions associated with the specified resource. 



**Args:**
 
 - <b>`resource_name`</b>:  The name of the resource (relative URI). 
 - <b>`resolve_groups`</b>:  If `True`, all permission will be resolved to basic permissions. Defaults to `True`. 



**Returns:**
 
 - <b>`List[str]`</b>:  List of permissions associated with the given resource. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L151"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_resources_with_permissions`

```python
list_resources_with_permissions(
    permission: str,
    resource_name_prefix: Optional[str] = None
) → List[str]
```

Returns all resources that are granted for the specified permission. 



**Args:**
 
 - <b>`permission`</b>:  The permission to use. If the permission is specified without the access level, it will filter for all access levels. 
 - <b>`resource_name_prefix`</b>:  Only return resources that match with this prefix. 



**Returns:**
 
 - <b>`List[str]`</b>:  List of resources names (relative URIs). 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `login_page`

```python
login_page() → RedirectResponse
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `logout_session`

```python
logout_session() → RedirectResponse
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_permission`

```python
remove_permission(
    resource_name: str,
    permission: str,
    apply_as_prefix: bool = False
) → None
```

Revokes a permission from the specified resource. 



**Args:**
 
 - <b>`resource_name`</b>:  The resource name that the permission should be revoked from. 
 - <b>`permission`</b>:  The permission to revoke from the specified resource. 
 - <b>`apply_as_prefix`</b>:  If `True`, the permission is used as prefix, and all permissions that start with this prefix will be revoked. Defaults to `False`. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_password`

```python
verify_password(user_id: str, password: str) → bool
```

Verifies a password of a specified user. 

The password is stored as a hash 



**Args:**
 
 - <b>`user_id`</b>:  The ID of the user. 
 - <b>`password`</b>:  The password to check. This can also be specified as a hash. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the password matches the stored password. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_token`

```python
verify_token(token: str, permission: Optional[str] = None) → GrantedPermission
```

Verifies a session or API token. 

The token is verfied for its validity and - if provided - if it has the specified permission. 



**Args:**
 
 - <b>`token`</b>:  Token to verify. 
 - <b>`permission`</b> (optional):  The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked. 



**Raises:**
 
 - <b>`PermissionDeniedError`</b>:  If the requested permission is denied. 
 - <b>`UnauthenticatedError`</b>:  If the token is invalid or expired. 



**Returns:**
 
 - <b>`GrantedPermission`</b>:  Information about the granted permission and authenticated user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuthOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L194"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_userinfo`

```python
get_userinfo(
    token: str,
    token_type_hint: Optional[str] = None
) → OAuthTokenIntrospection
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L186"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `introspect_token`

```python
introspect_token(
    token: str,
    token_type_hint: Optional[str] = None
) → OAuthTokenIntrospection
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L202"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `login_callback`

```python
login_callback(code: str, state: Optional[str] = None) → RedirectResponse
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `request_token`

```python
request_token(form_data: OAuth2TokenRequestForm) → OAuthToken
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `revoke_token`

```python
revoke_token(token: str, token_type_hint: Optional[str] = None) → None
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
