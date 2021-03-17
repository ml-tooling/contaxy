<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.deployment.utils`




**Global Variables**
---------------
- **DEFAULT_DEPLOYMENT_ACTION_ID**
- **NO_LOGS_MESSAGE**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_labels`

```python
map_labels(labels: dict) → MappedLabels
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `clean_labels`

```python
clean_labels(labels: Optional[dict] = None) → dict
```

Remove system labels that should not be settable by the user. 



**Args:**
 
 - <b>`labels`</b> (Optional[dict]):  The labels dict from which system labels should be removed. 



**Returns:**
 
 - <b>`dict`</b>:  The new labels dict that does not contain any system labels or an empty dict. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_deployment_id`

```python
get_deployment_id(
    project_id: str,
    deployment_name: str,
    deployment_type: DeploymentType
) → str
```

Returns a valid deployment ID based on some specified metadata. 



**Args:**
 
 - <b>`project_id`</b> (str):  The ID of the project associated with the deployment. 
 - <b>`deployment_name`</b> (str):  The name of the deployment. This can be an arbitrary text. 
 - <b>`deployment_type`</b> (DeploymentType):  The type of the deployment. 



**Returns:**
 
 - <b>`str`</b>:  A valid deployment ID. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_volume_name`

```python
get_volume_name(project_id: str, service_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_network_name`

```python
get_network_name(project_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L156"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_label_string`

```python
get_label_string(key: str, value: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_gpu_info`

```python
get_gpu_info()
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `log`

```python
log(input: str) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Labels`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MappedLabels`










---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
