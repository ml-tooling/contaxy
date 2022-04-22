<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.utils.file_utils`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L171"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_file_id`

```python
generate_file_id(file_name: str, version_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MultipartStreamTarget`
StreamTarget stores one chunk at a time in-memory and deletes it upon read. 

This is useful in case you'd like to have a parsed stream. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    validator: Optional[Callable] = None,
    hash_algo: Optional[str] = 'md5'
) → None
```






---

#### <kbd>property</kbd> hash





---

#### <kbd>property</kbd> value







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `on_data_received`

```python
on_data_received(chunk: bytes) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FormMultipartStream`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    stream: Generator,
    headers: Mapping[str, str],
    form_field: str = 'file',
    pre_read_size: int = 1024,
    hash_algo: Optional[str] = 'md5'
) → None
```

Currently, it is a requirement that the multipart/form-data stream embodies only one form field, i.e. the form_field parameter. 



**Args:**
 
 - <b>`stream`</b> (Generator):  The multipart/form-data byte stream. 
 - <b>`headers`</b> (Mapping[str, str]):  Http header of the reuqest. 
 - <b>`form_field`</b> (str, optional):  The name of the form field used to upload the file. Defaults to "file". 
 - <b>`pre_read_size`</b> (int):  The pre_read_size controls the byte size which will be used to determine some metadata in advance e.g. a filename based on the content-disposition. Defaults to 1024. 
 - <b>`hash_algo`</b> (Optional[str]):  Name of the hash algorithm supported by python's hashlib. If not set, now file hash will be calculated. 


---

#### <kbd>property</kbd> content_type





---

#### <kbd>property</kbd> filename





---

#### <kbd>property</kbd> hash







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `read`

```python
read(size: int = -1) → bytes
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SyncFromAsyncGenerator`
This genrator implementation wraps an async generator to make it compatible for sync implementations. 

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(async_generator: AsyncGenerator, event_loop: AbstractEventLoop) → None
```








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L164"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close() → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send`

```python
send(value) → Any
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/file_utils.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `throw`

```python
throw(typ, val=None, tb=None) → None
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
