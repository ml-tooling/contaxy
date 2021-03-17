<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/id_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.utils.id_utils`
Utilities for generating IDs, tokens, and hashes. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/id_utils.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_project_resource_prefix`

```python
get_project_resource_prefix(project_id: str) → str
```

Creates a prefix usable to construct IDs for project resources. 

The resource prefix is based on the system namespace and project ID. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/id_utils.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `hash_str`

```python
hash_str(input_str: str, length: Optional[int] = None) → str
```

Generates a hash with a variable lenght from an abritary text. 



**Args:**
 
 - <b>`input_str`</b> (str):  Text to hash. 
 - <b>`length`</b> (Optional[int], optional):  The length of the generated hash. A shorter hash will result in more possible collusions. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/id_utils.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_token`

```python
generate_token(length: int) → str
```

Generates a random token with the specified length. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/id_utils.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_short_uuid`

```python
generate_short_uuid() → str
```

Generates a short - 25 chars - UUID by using all ascii letters and digits. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/id_utils.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_readable_id`

```python
generate_readable_id(
    input_str: str,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    max_hash_suffix_length: Optional[int] = None,
    separator: str = '-',
    stopwords: Optional[List[str]] = None
) → str
```

Generates a human- and URL-friendly ID from arbritary text. 



**Args:**
 
 - <b>`input_str`</b> (str):  Text to use for ID generation. 
 - <b>`max_length`</b> (Optional[int], optional):  Maximal length of the ID. Defaults to `None`. 
 - <b>`min_length`</b> (Optional[int], optional):  Minimal length of the ID. The generated ID will be filled with a suffix based on its hash. Defaults to `None`. 
 - <b>`suffix`</b> (Optional[str], optional):  Suffix to add to the generated ID. Defaults to `None`. 
 - <b>`prefix`</b> (Optional[str], optional):  Prefix to add the the generated ID. Defaults to `None`. 
 - <b>`max_hash_suffix_length`</b> (Optional[int], optional):  Number of chars to append to the generated ID to allow generating unique IDs with a max lengths. Defaults to `None`. 
 - <b>`separator`</b> (str, optional):  Seperator to use for replacing whitespaces. Defaults to `-`. 
 - <b>`stopwords`</b> (Optional[List[str]], optional):  List of stopwords to ignore in the generated ID. Defaults to `None`. 



**Raises:**
 
 - <b>`ValueError`</b>:  A a function parameter has an inappropriate value. 



**Returns:**
 
 - <b>`str`</b>:  The generated ID human- and URL-friendly ID. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
