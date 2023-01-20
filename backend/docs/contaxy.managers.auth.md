<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.auth`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserPassword`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LoginIdMapping`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ResourcePermissions`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L73"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(component_manager: ComponentOperations)
```

Initializes the Auth Manager. 



**Args:**
 
 - <b>`component_manager`</b>:  Instance of the component manager that grants access to the other managers. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L459"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_permission`

```python
add_permission(resource_name: str, permission: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L407"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `change_password`

```python
change_password(user_id: str, password: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_token`

```python
create_token(
    scopes: List[str],
    token_type: TokenType,
    description: Optional[str] = None,
    token_purpose: Optional[str] = None,
    token_subject: Optional[str] = None
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L870"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L1017"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L944"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L1106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user_token`

```python
get_user_token(
    user_id: str,
    access_level: AccessLevel = <AccessLevel.WRITE: 'write'>
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L963"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user_with_permission`

```python
get_user_with_permission(user_id: str) → UserPermission
```

Returns the user metadata for a single user. 



**Args:**
 
 - <b>`user_id`</b>:  The ID of the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 



**Returns:**
 
 - <b>`User`</b>:  The user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L724"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `introspect_token`

```python
introspect_token(token: str) → OAuthTokenIntrospection
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L238"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_api_tokens`

```python
list_api_tokens(token_subject: Optional[str] = None) → List[ApiToken]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L613"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_permissions`

```python
list_permissions(
    resource_name: str,
    resolve_roles: bool = True,
    use_cache: bool = False
) → List[str]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L634"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_resources_with_permission`

```python
list_resources_with_permission(
    permission: str,
    resource_name_prefix: Optional[str] = None
) → List[str]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L815"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_users`

```python
list_users(
    access_level: Optional[AccessLevel] = None
) → List[Union[User, UserRead]]
```

Lists all users. 

TODO: Filter based on authenticated user? 



**Returns:**
 
 - <b>`List[User]`</b>:  List of users. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L751"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `login_callback`

```python
login_callback(
    code: str,
    redirect_uri: str,
    project_manager: ProjectOperations,
    state: Optional[str] = None
) → OAuthToken
```

Implements the OAuth2 / OICD callback to finish the login process. 

The authorization `code` is exchanged for an access and ID token. The ID token contains all relevant user information and is used to login the user. If the user does not exist, a new user will be created with the information from the ID token. 

This operation implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749. 



**Args:**
 
 - <b>`code`</b>:  The authorization code generated by the authorization server. 
 - <b>`redirect_uri`</b>:  The redirect uri used for the OICD authorization flow. 
 - <b>`project_manager`</b>:  Project manager required for creating new users 
 - <b>`state`</b> (optional):  An opaque value used by the client to maintain state between the request and callback. The parameter SHOULD be used for preventing cross-site request forgery. 



**Raises:**
 
 - <b>`UnauthenticatedError`</b>:  If the `code` could not be used to get an ID token. 



**Returns:**
 
 - <b>`RedirectResponse`</b>:  A redirect to the webapp that has valid access tokens attached. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L138"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `login_page`

```python
login_page() → Union[RedirectResponse, NoneType]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L141"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `logout_session`

```python
logout_session() → RedirectResponse
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L506"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_permission`

```python
remove_permission(
    resource_name: str,
    permission: str,
    remove_sub_permissions: bool = False
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L663"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `request_token`

```python
request_token(token_request_form: OAuth2TokenRequestFormNew) → OAuthToken
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L704"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `revoke_token`

```python
revoke_token(token: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L982"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L1007"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_user_last_activity_time`

```python
update_user_last_activity_time(user_id: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L376"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_access`

```python
verify_access(
    token: str,
    permission: Optional[str] = None,
    use_cache: bool = True
) → AuthorizedAccess
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/auth.py#L424"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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
