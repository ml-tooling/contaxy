<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.schema.auth`




**Global Variables**
---------------
- **MAX_DESCRIPTION_LENGTH**
- **USERS_KIND**
- **ADMIN_ROLE**
- **USER_ROLE**
- **contaxy_token_purposes**


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AccessLevel`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TokenPurpose`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TokenType`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AccessToken`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ApiToken`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthorizedAccess`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2TokenGrantTypes`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2TokenRequestFormNew`
OAuth2 Token Endpoint Request Form. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L229"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuthToken`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L250"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuthTokenIntrospection`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L305"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthorizeResponseType`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L310"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2ErrorDetails`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L314"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OAuth2Error`
Basic exception for OAuth errors. 

Implements the [RFC6749 error response](https://tools.ietf.org/html/rfc6749#section-5.2). 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L320"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(error: str) → None
```

Initializes the exception. 



**Args:**
 
 - <b>`error`</b>:  A single ASCII error code from the ones defined in RFC6749. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L377"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserBase`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L392"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserInput`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L396"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserRegistration`








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/auth.py#L406"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `User`










---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
