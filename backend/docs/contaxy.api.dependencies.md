<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/dependencies.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.dependencies`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/dependencies.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_api_token`

```python
get_api_token(
    api_token_query: str = Security(APIKeyQuery),
    api_token_header: str = Security(APIKeyHeader),
    api_token_cookie: str = Security(APIKeyCookie),
    bearer_token: str = Security(OAuth2PasswordBearer)
) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/dependencies.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_component_manager`

```python
get_component_manager(
    request: Request
) → Generator[ComponentManager, NoneType, NoneType]
```

Returns the initialized component manager. 

This is used as FastAPI dependency and called for every request. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
