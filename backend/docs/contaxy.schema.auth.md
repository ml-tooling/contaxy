<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.schema.auth`




**Global Variables**
---------------
- **MAX_DESCRIPTION_LENGTH**


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AccessLevel`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TokenPurpose`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TokenType`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ApiToken`





---

#### <kbd>property</kbd> fields








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `GrantedPermission`





---

#### <kbd>property</kbd> fields








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2TokenGrantTypes`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2TokenRequestForm`
OAuth2 Token Endpoint Request Form. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    grant_type: OAuth2TokenGrantTypes = Form(Ellipsis),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    set_as_cookie: Optional[bool] = Form(False)
)
```









---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L145"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuthToken`





---

#### <kbd>property</kbd> fields








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OpenIDUserInfo`





---

#### <kbd>property</kbd> fields








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L190"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuthTokenIntrospection`





---

#### <kbd>property</kbd> fields








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L245"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthorizeResponseType`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L250"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2AuthorizeRequestForm`
OAuth2 Authorize Endpoint Request Form. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L253"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    response_type: AuthorizeResponseType = Form(Ellipsis),
    client_id: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    nonce: Optional[str] = Form(None)
)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
