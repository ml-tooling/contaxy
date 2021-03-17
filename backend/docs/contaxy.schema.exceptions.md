<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.schema.exceptions`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ClientBaseError`
Basic exception class for all errors that should be shown to the client/user. 

The error details will be shown to the client (user) if it is not handled otherwise. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    status_code: int,
    message: str,
    explanation: Optional[str] = None,
    metadata: Optional[Dict] = None
) → None
```

Initializes the exception. 



**Args:**
 
 - <b>`status_code`</b>:  The HTTP status code associated with the error. 
 - <b>`message`</b>:  A short summary of the error. 
 - <b>`explanation`</b> (optional):  A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed. 
 - <b>`metadata`</b> (optional):  Additional problem details/metadata. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ServerBaseError`
Basic exception class for all server internal errors that should not be shown with details to the user. 

If the error is not handled, an `Internal Server Error` (Status Code 500) will be shown to the client (user) without any additional details. In this case, the execption will be automatically logged. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args: object) → None
```

Initializes the exception. 



**Args:**
 
 - <b>`args`</b>:  A collection of 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UnauthenticatedError`
Client error that indicates invalid, expired, or missing authentication credentials. 

The error message should contain specific details about the problem, e.g.: 


- No access token was provided. 

The error details will be shown to the client (user) if it is not handled otherwise. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message: Optional[str] = None,
    explanation: Optional[str] = None,
    metadata: Optional[Dict] = None
) → None
```

Initializes the error. 



**Args:**
 
 - <b>`message`</b> (optional):  A message shown to the user that overwrites the default message. 
 - <b>`explanation`</b> (optional):  A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed. 
 - <b>`metadata`</b> (optional):  Additional problem details/metadata. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PermissionDeniedError`
Client error that indicates that a client does not have sufficient permission for the request. 

The error message should contain specific details about the resource, e.g.: 


- Permission 'xxx' denied on resource 'yyy'. 

The error details will be shown to the client (user) if it is not handled otherwise. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message: Optional[str] = None,
    explanation: Optional[str] = None,
    metadata: Optional[Dict] = None
) → None
```

Initializes the error. 



**Args:**
 
 - <b>`message`</b> (optional):  A message shown to the user that overwrites the default message. 
 - <b>`explanation`</b> (optional):  A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed. 
 - <b>`metadata`</b> (optional):  Additional problem details/metadata. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ResourceNotFoundError`
Client error that indicates that a specified resource is not found. 

The error message should contain specific details about the resource, e.g.: 


- Resource 'xxx' not found. 

The error details will be shown to the client (user) if it is not handled otherwise. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message: Optional[str] = None,
    explanation: Optional[str] = None,
    metadata: Optional[Dict] = None
) → None
```

Initializes the error. 

This error should be raised if 



**Args:**
 
 - <b>`message`</b> (optional):  A message shown to the user that overwrites the default message. 
 - <b>`explanation`</b> (optional):  A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed. 
 - <b>`metadata`</b> (optional):  Additional problem details/metadata. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ResourceAlreadyExistsError`
Client error that indicates that a resource that a client tried to create already exists. 

The error message should contain specific details about the problem and resource, e.g.: 


- Resource 'xxx' already exists. 
- Couldn’t acquire lock on resource ‘xxx’. 

The error details will be shown to the client (user) if it is not handled otherwise. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message: Optional[str] = None,
    explanation: Optional[str] = None,
    metadata: Optional[Dict] = None
) → None
```

Initializes the error. 



**Args:**
 
 - <b>`message`</b> (optional):  A message shown to the user that overwrites the default message. 
 - <b>`explanation`</b> (optional):  A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed. 
 - <b>`metadata`</b> (optional):  Additional problem details/metadata. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L195"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ClientValueError`
Client error that indicates that the client input is invalid. 

The error message should contain specific details about the problem, e.g.: 


- Request field x.y.z is xxx, expected one of [yyy, zzz]. 
- Parameter 'age' is out of range [0, 125]. 

The error details will be shown to the client (user) if it is not handled otherwise. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/schema/exceptions.py#L209"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message: Optional[str] = None,
    explanation: Optional[str] = None,
    metadata: Optional[Dict] = None
) → None
```

Initializes the error. 



**Args:**
 
 - <b>`message`</b> (optional):  A message shown to the user that overwrites the default message. 
 - <b>`explanation`</b> (optional):  A human readable explanation specific to this error that is helpful to locate the problem and give advice on how to proceed. 
 - <b>`metadata`</b> (optional):  Additional problem details/metadata. 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
