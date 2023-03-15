<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.deployment.utils`




**Global Variables**
---------------
- **DEFAULT_DEPLOYMENT_ACTION_ID**
- **NO_LOGS_MESSAGE**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `stop_idle_services`

```python
stop_idle_services(component_manager: ComponentOperations) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_service_collection_id`

```python
get_service_collection_id(project_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_job_collection_id`

```python
get_job_collection_id(project_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_deployment_config`

```python
create_deployment_config(
    project_id: str,
    deployment_input: DeploymentInput,
    deployment_type: DeploymentType,
    authorized_subject: str,
    system_manager: SystemOperations,
    auth_manager: AuthOperations,
    deployment_class: Type[~DeploymentClass]
) → ~DeploymentClass
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L180"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_labels`

```python
map_labels(labels: Dict[str, Any]) → MappedLabels
```

Transform label dict to a MappedLabels object. 

Special labels have their own field and additional, non-special labels are added to the MappedLabels.metadata field. 



**Args:**
 
 - <b>`labels`</b> (dict):  A dictionary containing key-value pairs that, for example, are used as container labels. 



**Returns:**
 
 - <b>`MappedLabels`</b>:  The labels object transformed to a MappedLabels object. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `clean_metadata`

```python
clean_metadata(labels: Optional[dict] = None) → dict
```

Remove system labels that should not be settable by the user. 



**Args:**
 
 - <b>`labels`</b> (Optional[dict]):  The labels dict from which system labels should be removed. 



**Returns:**
 
 - <b>`dict`</b>:  The new labels dict that does not contain any system labels or an empty dict. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L273"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L309"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_volume_name`

```python
get_volume_name(project_id: str, service_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L314"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_network_name`

```python
get_network_name(project_id: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L318"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_label_string`

```python
get_label_string(key: str, value: str) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L322"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_gpu_info`

```python
get_gpu_info() → int
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L338"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_project_selection_labels`

```python
get_project_selection_labels(
    project_id: str,
    deployment_type: DeploymentType = <DeploymentType.SERVICE: 'service'>
) → List
```

Return a list of labels identifying project resources (system namespace, project id, deployment type). 



**Args:**
 
 - <b>`project_id`</b> (str):  The project id included in the label list. 
 - <b>`deployment_type`</b> (DeploymentType, optional):  The deployment type included in the label list. Defaults to DeploymentType.SERVICE. 



**Returns:**
 
 - <b>`List`</b>:  Contains the labels identifying project resources. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L357"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_list_to_string`

```python
map_list_to_string(endpoints: Optional[List[str]]) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L361"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_string_to_list`

```python
map_string_to_list(string_to_split: Optional[str]) → List[str]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L367"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_default_environment_variables`

```python
get_default_environment_variables(
    project_id: str,
    deployment_id: str,
    auth_manager: AuthOperations,
    endpoints: Optional[List[str]] = None,
    compute_resources: Optional[DeploymentCompute] = None
) → Dict[str, str]
```

Sets default environment variables that should be set for each container. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project id included in the label list deployment_id (str) 
 - <b>`auth_manager`</b> (AuthOperations):  Auth manager used for creating an access token for the service 
 - <b>`endpoints`</b> (List[str]):  List of endpoints 
 - <b>`compute_resources`</b>:  (Optional[DeploymentCompute]): DeploymentCompute information 



**Returns:**
 
 - <b>`Dict[str, str]`</b>:  Dict with default environment variables or empty dict. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L435"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `replace_template_string`

```python
replace_template_string(
    input: str = '',
    templates_mapping: Dict[str, str] = {}
) → str
```

Return the input with replaced value according to the templates mapping. 

For example, if `template = "{env.CONTAXY_BASE_URL}"` and `values = { "{env.CONTAXY_BASE_URL}": "some-value" } }`, the result will be `"some-value"` 



**Args:**
 
 - <b>`input`</b> (str):  The string that should be checked against the values dict and probably replaced by a match. 
 - <b>`templates_mapping`</b> (Dict[str, str]):  The dict that contains template-strings with corresponding values. 



**Returns:**
 
 - <b>`str`</b>:  The string with the replaced value or the unmodified string in case of no match. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L461"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `replace_templates`

```python
replace_templates(
    input: Dict[str, str] = {},
    template_mapping: Dict[str, str] = {}
) → Dict[str, str]
```

Returns the input dict where those values that are matching template strings are replaced. 



**Args:**
 
 - <b>`input`</b> (Dict[str, str]):  The input dict for which the values should be checked for matching template replacements. 
 - <b>`templates_mapping`</b> (Dict[str, str]):  The dict that contains template-strings with corresponding values. 



**Returns:**
 
 - <b>`Dict[str, str]`</b>:  A copy of the modified input dict where the template literals are replaced. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L484"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_template_mapping`

```python
get_template_mapping(
    project_id: Optional[str] = None,
    user_id: Optional[str] = None,
    environment: Optional[Dict[str, str]] = None
) → Dict[str, str]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L514"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `split_image_name_and_tag`

```python
split_image_name_and_tag(full_image_name: str) → Tuple[str, str]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L528"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `enrich_deployment_with_runtime_info`

```python
enrich_deployment_with_runtime_info(
    deployment_from_db: Deployment,
    deployment_with_runtime_info: Deployment
) → None
```

Transfers runtime information from one deployment object to another. 

If a deployment is loaded from the DB certain fields are not set (e.g. the internal id) because they are received at runtime from the running container. This function takes a deployment retrieved from the DB and adds these missing runtime field from another deployment object that was created directly from the running container. 



**Args:**
 
 - <b>`deployment_from_db`</b>:  The deployment object retrieved from the DB without runtime info.  This object is edited in place to add the missing runtime fields. 
 - <b>`deployment_with_runtime_info`</b>:  The deployment object created directly from the container with runtime info 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Labels`
An enumeration. 





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/utils.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MappedLabels`










---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
