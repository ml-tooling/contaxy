<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/system.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.system`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/system.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_system_info`

```python
get_system_info(
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Returns information about this instance. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/system.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_health`

```python
check_health(
    component_manager: ComponentManager = Depends(get_component_manager)
) → Any
```

Returns a successful return code if the instance is healthy. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/system.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_system_statistics`

```python
get_system_statistics(
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns statistics about this instance. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
