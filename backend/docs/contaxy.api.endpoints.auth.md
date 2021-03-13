<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.auth`




**Global Variables**
---------------
- **MAX_PROJECT_ID_LENGTH**
- **MIN_PROJECT_ID_LENGTH**
- **OPEN_URL_REDIRECT**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `open_login_page`

```python
open_login_page(
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Returns or redirect to the login-page. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `logout_session`

```python
logout_session(
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Removes all session token cookies and redirects to the login page. 

When making requests to the this endpoint, the browser should be redirected to this endpoint. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_api_token`

```python
list_api_token(
    user_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns list of created API tokens for the specified user or project. 

If a user ID and a project ID is provided, a combined list will be returned. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L93"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_token`

```python
create_token(
    scopes: Optional[List[str]] = Query(None),
    token_type: TokenType = Query(session-token),
    description: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns a session or API token with access on the specified resource. 

A permission is a single string that combines a global ID of a resource with a permission level: 

`{global_id}.{permission_level}` 

Permission levels are a hierarchical system that determines the kind of access that is granted on the resource. Permission levels are interpreted and applied inside resource operations. There are three permission levels: 

1. `admin` permission level allows read, write, and administrative access to the resource. 2. `write` permission level allows read and write (edit) access to the resource. 3. `read` permission level allows read-only (view) access to the resource. 

The permission level can also be suffixed with an optional restriction defined by the resource: `{global_id}.{permission_level}.{custom_restriction}` 

If no permissions are specified, the token will be generated with the same permissions as the authorized token. 

The API token can be deleted (revoked) at any time. In comparison, the session token cannot be revoked but expires after a short time (a few minutes). 

This operation can only be called with API tokens (or refresh tokens) due to security aspects. Session tokens are not allowed to create other tokens. Furthermore, tokens can only be created if the API token used for authorization is granted at least the same permission level on the given resource. For example, a token with `write` permission level on a given resource allows to create new tokens with `write` or `read` permission on that resource. If a restriction is attached to the permission, created tokens on the same permission level require the same restriction. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `verify_token`

```python
verify_token(
    token: Optional[str] = Body(None),
    permission: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Verifies a session or API token for its validity and - if provided - if it has the specified permission. 

Returns an successful HTTP Status code if verification was successful, otherwise an error is returned. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `request_token`

```python
request_token(form_data: OAuth2TokenRequestForm = Depends(NoneType)) → Any
```

Returns an access tokens, ID tokens, or refresh tokens depending on the request parameters. 

The token endpoint is used by the client to obtain an access token by presenting its authorization grant or refresh token. 

The token endpoint supports the following grant types: - [Password Grant](https://tools.ietf.org/html/rfc6749#section-4.3.2): Used when the application exchanges the user’s username and password for an access token.  - `grant_type` must be set to `password`  - `username` (required): The user’s username.  - `password` (required): The user’s password.  - `scope` (optional): Optional requested scope values for the access token. - [Refresh Token Grant](https://tools.ietf.org/html/rfc6749#section-6): Allows to use refresh tokens to obtain new access tokens.  - `grant_type` must be set to `refresh_token`  - `refresh_token` (required): The refresh token previously issued to the client.  - `scope` (optional): Requested scope values for the new access token. Must not include any scope values not originally granted by the resource owner, and if omitted is treated as equal to the originally granted scope. - [Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4.2): Request an access token using only its client credentials.  - `grant_type` must be set to `client_credentials`  - `scope` (optional): Optional requested scope values for the access token.  - Client Authentication required (e.g. via client_id and client_secret or auth header) - [Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1): Used to obtain both access tokens and refresh tokens based on an authorization code from the `/authorize` endpoint.  - `grant_type` must be set to `authorization_code`  - `code` (required): The authorization code that the client previously received from the authorization server.  - `redirect_uri` (required): The redirect_uri parameter included in the original authorization request.  - Client Authentication required (e.g. via client_id and client_secret or auth header) 

For password, client credentials, and refresh token flows, calling this endpoint is the only step of the flow. For the authorization code flow, calling this endpoint is the second step of the flow. 

This endpoint implements the [OAuth2 Token Endpoint](https://tools.ietf.org/html/rfc6749#section-3.2). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L220"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `revoke_token`

```python
revoke_token(
    token: str = Form(Ellipsis),
    token_type_hint: Optional[str] = Form(None),
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Revokes a given token. 

This will delete the API token, preventing further requests with the given token. Because of caching, the API token might still be usable under certain conditions for some operations for a maximum of 15 minutes after deletion. 

This endpoint implements the OAuth2 Revocation Flow ([RFC7009](https://tools.ietf.org/html/rfc7009)). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `introspect_token`

```python
introspect_token(
    token: str = Form(Ellipsis),
    token_type_hint: Optional[str] = Form(None),
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Introspects a given token. 

Returns a boolean that indicates whether it is active or not. If the token is active, additional data about the token is also returned. If the token is invalid, expired, or revoked, it is considered inactive. 

This endpoint implements the [OAuth2 Introspection Flow](https://www.oauth.com/oauth2-servers/token-introspection-endpoint/) ([RFC7662](https://tools.ietf.org/html/rfc7662)). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L274"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_userinfo`

```python
get_userinfo(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns information about the authenticated user. 

The access token obtained must be sent as a bearer token in the `Authorization` header. 

This endpoint implements the [OpenID UserInfo Endpoint](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/auth.py#L294"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `login_callback`

```python
login_callback(
    code: str = Query(Ellipsis),
    state: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Callback to finish the login process (OAuth2 Client Endpoint). 

The authorization `code` is exchanged for an access and ID token. The ID token contains all relevant user information and is used to login the user. If the user does not exist, a new user will be created with the information from the ID token. 

Finally, the user is redirected to the webapp and a session/refresh token is set in the cookies. 

This method implements the [Authorization Response](https://tools.ietf.org/html/rfc6749#section-4.1.2) from RFC6749. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
