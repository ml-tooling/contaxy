<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/minio_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.utils.minio_utils`




**Global Variables**
---------------
- **ENABLED**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/minio_utils.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_bucket_name`

```python
get_bucket_name(project_id: str, prefix: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/minio_utils.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_minio_client`

```python
create_minio_client(settings: Settings) → Minio
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/minio_utils.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `purge_bucket`

```python
purge_bucket(client: Minio, bucket_name: str) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/minio_utils.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_bucket`

```python
delete_bucket(client: Minio, bucket_name: str, force: bool = False) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/utils/minio_utils.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_bucket`

```python
create_bucket(
    client: Minio,
    bucket_name: str,
    versioning_enabled: bool = True
) → None
```

Create a bucket in the object storage configured by the client. 



**Args:**
 
 - <b>`client`</b> (Minio):  The initilaized Minio client. 
 - <b>`bucket_name`</b> (str):  Bucket name. 
 - <b>`versioning_enabled`</b> (bool, optional):  Controls bucket versioning. Defaults to True. 



**Raises:**
 
 - <b>`ServerBaseError`</b>:  If the desired action could not be performed. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
