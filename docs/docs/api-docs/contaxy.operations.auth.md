<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.auth`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

Returns a session or API token with access to the speicfied scopes. 

The token is created on behalfe of the authorized user. 



**Args:**
 
 - <b>`scopes`</b>:  Scopes requested for this token. If none specified, the token will be generated with same set of scopes as the authorized token. 
 - <b>`token_type`</b>:  The type of the token. 
 - <b>`description`</b> (optional):  A short description about the generated token. 
 - <b>`token_purpose`</b>:  Purpose of the newly created token 
 - <b>`token_subject`</b>:  Subject that the token belongs to 



**Returns:**
 
 - <b>`str`</b>:  The created session or API token. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L258"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_user`

```python
create_user(user_input: UserRegistration, technical_user: bool = False) → User
```

Creates a user. 



**Args:**
 
 - <b>`user_input`</b>:  The user data to create the new user. 
 - <b>`technical_user`</b>:  If `True`, the created user will be marked as technical user. Defaults to `False`. 



**Raises:**
 
 - <b>`ResourceAlreadyExistsError`</b>:  If a user with the same username or email already exists. 



**Returns:**
 
 - <b>`User`</b>:  The created user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L310"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L276"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `introspect_token`

```python
introspect_token(token: str) → OAuthTokenIntrospection
```

Introspects a given token. 

Returns a status (`active`) that indicates whether it is active or not. If the token is active, additional data about the token is also returned. If the token is invalid, expired, or revoked, it is considered inactive. 

This operation implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)). 



**Args:**
 
 - <b>`token`</b>:  The token that should be instrospected. 



**Returns:**
 
 - <b>`OAuthTokenIntrospection`</b>:  The token state and additional metadata. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_api_tokens`

```python
list_api_tokens() → List[ApiToken]
```

Lists all API tokens associated from the authorized user. 



**Returns:**
 
 - <b>`List[ApiToken]`</b>:  A list of API tokens. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L247"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_users`

```python
list_users() → List[User]
```

Lists all users. 

TODO: Filter based on authenticated user? 



**Returns:**
 
 - <b>`List[User]`</b>:  List of users. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `request_token`

```python
request_token(token_request_form: OAuth2TokenRequestFormNew) → OAuthToken
```

Returns an access tokens, ID tokens, or refresh tokens depending on the request parameters. 

The token endpoint is used by the client to obtain an access token by presenting its authorization grant or refresh token. 

The token endpoint supports the following grant types: 
- [Password Grant](https://tools.ietf.org/html/rfc6749#section-4.3.2): Used when the application exchanges the user’s username and password for an access token. 
    - `grant_type` must be set to `password` 
    - `username` (required): The user’s username. 
    - `password` (required): The user’s password. 
    - `scope` (optional): Optional requested scope values for the access token. 
- [Refresh Token Grant](https://tools.ietf.org/html/rfc6749#section-6): Allows to use refresh tokens to obtain new access tokens. 
    - `grant_type` must be set to `refresh_token` 
    - `refresh_token` (required): The refresh token previously issued to the client. 
    - `scope` (optional): Requested scope values for the new access token. Must not include any scope values not originally granted by the resource owner, and if omitted is treated as equal to the originally granted scope. 
- [Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4.2): Request an access token using only its client credentials. 
    - `grant_type` must be set to `client_credentials` 
    - `scope` (optional): Optional requested scope values for the access token. 
    - Client Authentication required (e.g. via client_id and client_secret or auth header) 
- [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1): Used to obtain both access tokens and refresh tokens based on an authorization code from the `/authorize` endpoint. 
    - `grant_type` must be set to `authorization_code` 
    - `code` (required): The authorization code that the client previously received from the authorization server. 
    - `redirect_uri` (required): The redirect_uri parameter included in the original authorization request. 
    - Client Authentication required (e.g. via client_id and client_secret or auth header) 

For password, client credentials, and refresh token flows, calling this endpoint is the only step of the flow. For the authorization code flow, calling this endpoint is the second step of the flow. 

This endpoint implements the [OAuth2 Token Endpoint](https://tools.ietf.org/html/rfc6749#section-3.2). 



**Args:**
 
 - <b>`token_request_form`</b>:  The request instructions. 



**Raises:**
 
 - <b>`OAuth2Error`</b>:  If an error occures. Conforms the RFC6749 spec. 



**Returns:**
 
 - <b>`OAuthToken`</b>:  The access token and additonal metadata (depending on the grant type). 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L201"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `revoke_token`

```python
revoke_token(token: str) → None
```

Revokes a given token. 

This will delete the API token, preventing further requests with the given token. Because of caching, the API token might still be usable under certain conditions for some operations for a maximum of 15 minutes after deletion. 

This operation implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)). 



**Args:**
 
 - <b>`token`</b>:  The token that should be revoked. 



**Raises:**
 
 - <b>`OAuth2Error`</b>:  If an error occures. Conforms the RFC6749 spec. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L291"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/auth.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_access`

```python
verify_access(
    token: str,
    permission: Optional[str] = None,
    disable_cache: bool = False
) → AuthorizedAccess
```

Verifies if the authorized token is valid and grants a certain permission. 

The token is verfied for its validity and - if provided - if it has the specified permission. 



**Args:**
 
 - <b>`token`</b>:  Token (session or API) to verify. 
 - <b>`permission`</b> (optional):  The token is checked if it is granted this permission. If none specified, only the existence or validity of the token itself is checked. 
 - <b>`disable_cache`</b> (optional):  If `True`, no cache will be used for verifying the token. Defaults to `False`. 



**Raises:**
 
 - <b>`PermissionDeniedError`</b>:  If the requested permission is denied. 
 - <b>`UnauthenticatedError`</b>:  If the token is invalid or expired. 



**Returns:**
 
 - <b>`AuthorizedAccess`</b>:  Information about the granted permission and authenticated user. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
