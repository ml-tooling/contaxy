<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.auth`




**Global Variables**
---------------
- **USERS_KIND**


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserPassword`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LoginIdMapping`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ResourcePermissions`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    global_state: GlobalState,
    request_state: RequestState,
    json_db_manager: JsonDocumentOperations
)
```

Initializes the Auth Manager. 



**Args:**
 
 - <b>`global_state`</b>:  The global state of the app instance. 
 - <b>`request_state`</b>:  The state for the current request. 
 - <b>`json_db_manager`</b>:  JSON DB Manager instance to store structured data. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L426"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_permission`

```python
add_permission(resource_name: str, permission: str) → None
```

Grants a permission to the specified resource. 



**Args:**
 
 - <b>`resource_name`</b>:  The resource name that the permission is granted to. 
 - <b>`permission`</b>:  The permission to grant to the specified resource. 



**Raises:**
 
 - <b>`ResourceUpdateFailedError`</b>:  If the resource update could not be applied successfully. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L374"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `change_password`

```python
change_password(user_id: str, password: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_token`

```python
create_token(
    scopes: List[str],
    token_type: TokenType,
    description: Optional[str] = None,
    token_purpose: Optional[TokenPurpose] = None,
    token_subject: Optional[str] = None
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L849"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_user`

```python
create_user(user_input: UserRegistration, technical_user: bool = False) → User
```

Creates a user. 

If only the email is given then a username will be derived based on the email address. 



**Args:**
 
 - <b>`user_input`</b>:  The user data to create the new user. 
 - <b>`technical_user`</b>:  If `True`, the created user will be marked as technical user. Defaults to `False`. 



**Raises:**
 
 - <b>`ResourceAlreadyExistsError`</b>:  If a user with the same username or email already exists. 



**Returns:**
 
 - <b>`User`</b>:  The created user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L971"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_user`

```python
delete_user(user_id: str) → None
```

Deletes a user. 



**Args:**
 
 - <b>`user_id`</b> (str):  The ID of the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L928"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user`

```python
get_user(user_id: str) → User
```

Returns the user metadata for a single user. 



**Args:**
 
 - <b>`user_id`</b>:  The ID of the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 



**Returns:**
 
 - <b>`User`</b>:  The user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L720"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `introspect_token`

```python
introspect_token(token: str) → OAuthTokenIntrospection
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_api_tokens`

```python
list_api_tokens(token_subject: Optional[str] = None) → List[ApiToken]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L593"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_permissions`

```python
list_permissions(
    resource_name: str,
    resolve_roles: bool = True,
    use_cache: bool = False
) → List[str]
```

Returns all permissions granted to the specified resource. 



**Args:**
 
 - <b>`resource_name`</b>:  The name of the resource (relative URI). 
 - <b>`resolve_roles`</b>:  If `True`, all roles of the resource will be resolved to the associated permissions. Defaults to `True`. 



**Returns:**
 
 - <b>`List[str]`</b>:  List of permissions granted to the given resource. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L623"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_resources_with_permission`

```python
list_resources_with_permission(
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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L800"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_users`

```python
list_users() → List[User]
```

Lists all users. 

TODO: Filter based on authenticated user? 



**Returns:**
 
 - <b>`List[User]`</b>:  List of users. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L747"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `login_callback`

```python
login_callback(
    code: str,
    redirect_uri: str,
    state: Optional[str] = None
) → Tuple[OAuthToken, Union[User, NoneType]]
```

Implements the OAuth2 / OICD callback to finish the login process. 

The authorization `code` is exchanged for an access and ID token. The ID token contains all relevant user information and is used to login the user. If the user does not exist, a new user will be created with the information from the ID token. 

This operation implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749. 



**Args:**
 
 - <b>`code`</b>:  The authorization code generated by the authorization server. 
 - <b>`redirect_uri`</b>:  The redirect uri used for the OICD authorization flow. 
 - <b>`state`</b> (optional):  An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery. 



**Raises:**
 
 - <b>`UnauthenticatedError`</b>:  If the `code` could not be used to get an ID token. 



**Returns:**
 
 - <b>`RedirectResponse`</b>:  A redirect to the webapp that has valid access tokens attached. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L127"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `login_page`

```python
login_page() → RedirectResponse
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `logout_session`

```python
logout_session() → RedirectResponse
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L479"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_permission`

```python
remove_permission(
    resource_name: str,
    permission: str,
    remove_sub_permissions: bool = False
) → None
```

Revokes a permission from the specified resource. 



**Args:**
 
 - <b>`resource_name`</b>:  The resource name that the permission should be revoked from. 
 - <b>`permission`</b>:  The permission to revoke from the specified resource. 
 - <b>`remove_sub_permissions`</b>:  If `True`, the permission is used as prefix, and all permissions that start with this prefix will be revoked. Defaults to `False`. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L660"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `request_token`

```python
request_token(token_request_form: OAuth2TokenRequestFormNew) → OAuthToken
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L700"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `revoke_token`

```python
revoke_token(token: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L947"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_user`

```python
update_user(user_id: str, user_input: UserInput) → User
```

Updates the user metadata. 

This will update only the properties that are explicitly set in the `user_input`. The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396). 



**Args:**
 
 - <b>`user_id`</b> (str):  The ID of the user. 
 - <b>`user_input`</b> (UserInput):  The user data used to update the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 



**Returns:**
 
 - <b>`User`</b>:  The updated user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L344"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_access`

```python
verify_access(
    token: str,
    permission: Optional[str] = None,
    use_cache: bool = True
) → AuthorizedAccess
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L391"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
