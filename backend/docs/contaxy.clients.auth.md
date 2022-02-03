<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.clients.auth`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `handle_oauth_error`

```python
handle_oauth_error(response: Response) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthClient`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Session)
```








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_permission`

```python
add_permission(
    resource_name: str,
    permission: str,
    request_kwargs: Dict = {}
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `change_password`

```python
change_password(user_id: str, password: str, request_kwargs: Dict = {}) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_token`

```python
create_token(
    scopes: List[str],
    token_type: TokenType,
    description: Optional[str] = None,
    token_purpose: Optional[TokenPurpose] = None,
    token_subject: Optional[str] = None,
    request_kwargs: Dict = {}
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_user`

```python
create_user(
    user_input: UserRegistration,
    technical_user: bool = False,
    request_kwargs: Dict = {}
) → User
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L190"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_user`

```python
delete_user(user_id: str, request_kwargs: Dict = {}) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user`

```python
get_user(user_id: str, request_kwargs: Dict = {}) → User
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `introspect_token`

```python
introspect_token(
    token: str,
    request_kwargs: Dict = {}
) → OAuthTokenIntrospection
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_api_tokens`

```python
list_api_tokens(request_kwargs: Dict = {}) → List[ApiToken]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_permissions`

```python
list_permissions(
    resource_name: str,
    resolve_roles: bool = True,
    use_cache: bool = False,
    request_kwargs: Dict = {}
) → List[str]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_resources_with_permission`

```python
list_resources_with_permission(
    permission: str,
    resource_name_prefix: Optional[str] = None,
    request_kwargs: Dict = {}
) → List[str]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_users`

```python
list_users(request_kwargs: Dict = {}) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_permission`

```python
remove_permission(
    resource_name: str,
    permission: str,
    remove_sub_permissions: bool = False,
    request_kwargs: Dict = {}
) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L112"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `request_token`

```python
request_token(
    token_request_form: OAuth2TokenRequestFormNew,
    request_kwargs: Dict = {}
) → OAuthToken
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `revoke_token`

```python
revoke_token(token: str, request_kwargs: Dict = {}) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L179"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_user`

```python
update_user(
    user_id: str,
    user_input: UserInput,
    request_kwargs: Dict = {}
) → User
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/clients/auth.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `verify_access`

```python
verify_access(
    token: str,
    permission: Optional[str] = None,
    disable_cache: bool = False,
    request_kwargs: Dict = {}
) → AuthorizedAccess
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
