<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/exceptions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.exceptions`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/exceptions.py#L4"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ContaxyBaseError`
Basic exception class for `contaxy` library errors. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/exceptions.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(msg: str, predecessor_excp: Optional[Exception] = None)
```

Constructor method. 



**Args:**
 
 - <b>`msg`</b>:  The error message. 
 - <b>`predecessor_excp`</b>:  Optionally, a predecessor exception can be passed on. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/exceptions.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AuthenticationError`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/exceptions.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(reason: int, predecessor_excp: Optional[Exception] = None)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
