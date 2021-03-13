<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.deployment`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ServiceOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `access_service`

```python
access_service(project_id: str, service_id: str, endpoint: str) → Response
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service_id`</b> (str):  [description] 
 - <b>`endpoint`</b> (str):  [description] 



**Returns:**
 
 - <b>`Response`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_service`

```python
delete_service(
    project_id: str,
    service_id: str,
    delete_volumes: bool = False
) → None
```

Deletes a service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`delete_volumes`</b> (bool, optional):  If `True`, all attached volumes will be deleted. Defaults to `False`. 



**Raises:**
 
 - <b>`RuntimeError`</b>:  If an error occurs during the deletion of the service. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_service`

```python
deploy_service(
    project_id: str,
    service: ServiceInput,
    action_id: Optional[str] = None
) → Service
```

Deploys a service for the specified project. 

If no `action_id` is provided, the system will automatically select the best deployment option. 

Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions). 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service`</b> (ServiceInput):  [description] 
 - <b>`action_id`</b> (Optional[str], optional):  [description]. Defaults to None. 



**Returns:**
 
 - <b>`Service`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_service_action`

```python
execute_service_action(
    project_id: str,
    service_id: str,
    action_id: str
) → Response
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service_id`</b> (str):  [description] 
 - <b>`action_id`</b> (str):  [description] 



**Returns:**
 
 - <b>`Response`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_service_logs`

```python
get_service_logs(
    project_id: str,
    service_id: str,
    lines: Optional[int],
    since: Optional[datetime]
) → str
```

Returns the logs of a service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The ID of the project into which the service is deployed in. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`lines`</b> (Optional[int]):  If provided, just the last `n` lines are returned from the log. Defaults to `None`. 
 - <b>`since`</b> (Optional[datetime]):  If provided, just the logs since the given timestamp are returned. Defaults to `None`. 



**Raises:**
 
 - <b>`NotImplementedError`</b>:  [description] 
 - <b>`RuntimeError`</b>:  If reading the logs of the given service fails. 



**Returns:**
 
 - <b>`str`</b>:  The logs of the service. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_service_metadata`

```python
get_service_metadata(project_id: str, service_id: str) → Service
```

Returns the metadata of a single service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 



**Returns:**
 
 - <b>`Service`</b>:  The service metadata. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_deploy_service_actions`

```python
list_deploy_service_actions(
    project_id: str,
    service: ServiceInput
) → List[ResourceAction]
```

Lists all available service deployment options (actions). 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 



**Returns:**
 
 - <b>`List[ResourceAction]`</b>:  Available deployment actions. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_service_actions`

```python
list_service_actions(
    project_id: str,
    service_id: str,
    extension_id: Optional[str]
) → ResourceAction
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service_id`</b> (str):  [description] 
 - <b>`extension_id`</b> (Optional[str]):  [description] 



**Returns:**
 
 - <b>`ResourceAction`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_services`

```python
list_services(project_id: str) → List[Service]
```

Lists all services associated with the given project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID to filter the services. 



**Returns:**
 
 - <b>`List[Service]`</b>:  The list of services associated with the project. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_service_config`

```python
suggest_service_config(project_id: str, container_image: str) → ServiceInput
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`container_image`</b> (str):  [description] 



**Returns:**
 
 - <b>`ServiceInput`</b>:  [description] 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L205"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `JobOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_job`

```python
delete_job(project_id: str, job_id: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L210"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_job`

```python
deploy_job(
    project_id: str,
    job: JobInput,
    action_id: Optional[str] = None
) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_job_action`

```python
execute_job_action(project_id: str, job_id: str, action_id: str) → Response
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_logs`

```python
get_job_logs(
    project_id: str,
    job_id: str,
    lines: Optional[int] = None,
    since: Optional[datetime] = None
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_metadata`

```python
get_job_metadata(project_id: str, job_id: str) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L219"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_deploy_job_actions`

```python
list_deploy_job_actions(project_id: str, job: JobInput) → ResourceAction
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_job_actions`

```python
list_job_actions(project_id: str, job_id: str) → ResourceAction
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_jobs`

```python
list_jobs(project_id: str) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L227"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_job_config`

```python
suggest_job_config(project_id: str, container_image: str) → JobInput
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DeploymentOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `access_service`

```python
access_service(project_id: str, service_id: str, endpoint: str) → Response
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service_id`</b> (str):  [description] 
 - <b>`endpoint`</b> (str):  [description] 



**Returns:**
 
 - <b>`Response`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_job`

```python
delete_job(project_id: str, job_id: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_service`

```python
delete_service(
    project_id: str,
    service_id: str,
    delete_volumes: bool = False
) → None
```

Deletes a service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`delete_volumes`</b> (bool, optional):  If `True`, all attached volumes will be deleted. Defaults to `False`. 



**Raises:**
 
 - <b>`RuntimeError`</b>:  If an error occurs during the deletion of the service. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L210"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_job`

```python
deploy_job(
    project_id: str,
    job: JobInput,
    action_id: Optional[str] = None
) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_service`

```python
deploy_service(
    project_id: str,
    service: ServiceInput,
    action_id: Optional[str] = None
) → Service
```

Deploys a service for the specified project. 

If no `action_id` is provided, the system will automatically select the best deployment option. 

Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions). 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service`</b> (ServiceInput):  [description] 
 - <b>`action_id`</b> (Optional[str], optional):  [description]. Defaults to None. 



**Returns:**
 
 - <b>`Service`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_job_action`

```python
execute_job_action(project_id: str, job_id: str, action_id: str) → Response
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_service_action`

```python
execute_service_action(
    project_id: str,
    service_id: str,
    action_id: str
) → Response
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service_id`</b> (str):  [description] 
 - <b>`action_id`</b> (str):  [description] 



**Returns:**
 
 - <b>`Response`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_logs`

```python
get_job_logs(
    project_id: str,
    job_id: str,
    lines: Optional[int] = None,
    since: Optional[datetime] = None
) → str
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_metadata`

```python
get_job_metadata(project_id: str, job_id: str) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_service_logs`

```python
get_service_logs(
    project_id: str,
    service_id: str,
    lines: Optional[int],
    since: Optional[datetime]
) → str
```

Returns the logs of a service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The ID of the project into which the service is deployed in. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`lines`</b> (Optional[int]):  If provided, just the last `n` lines are returned from the log. Defaults to `None`. 
 - <b>`since`</b> (Optional[datetime]):  If provided, just the logs since the given timestamp are returned. Defaults to `None`. 



**Raises:**
 
 - <b>`NotImplementedError`</b>:  [description] 
 - <b>`RuntimeError`</b>:  If reading the logs of the given service fails. 



**Returns:**
 
 - <b>`str`</b>:  The logs of the service. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_service_metadata`

```python
get_service_metadata(project_id: str, service_id: str) → Service
```

Returns the metadata of a single service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 



**Returns:**
 
 - <b>`Service`</b>:  The service metadata. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L219"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_deploy_job_actions`

```python
list_deploy_job_actions(project_id: str, job: JobInput) → ResourceAction
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_deploy_service_actions`

```python
list_deploy_service_actions(
    project_id: str,
    service: ServiceInput
) → List[ResourceAction]
```

Lists all available service deployment options (actions). 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 



**Returns:**
 
 - <b>`List[ResourceAction]`</b>:  Available deployment actions. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_job_actions`

```python
list_job_actions(project_id: str, job_id: str) → ResourceAction
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_jobs`

```python
list_jobs(project_id: str) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_service_actions`

```python
list_service_actions(
    project_id: str,
    service_id: str,
    extension_id: Optional[str]
) → ResourceAction
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`service_id`</b> (str):  [description] 
 - <b>`extension_id`</b> (Optional[str]):  [description] 



**Returns:**
 
 - <b>`ResourceAction`</b>:  [description] 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_services`

```python
list_services(project_id: str) → List[Service]
```

Lists all services associated with the given project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID to filter the services. 



**Returns:**
 
 - <b>`List[Service]`</b>:  The list of services associated with the project. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L227"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_job_config`

```python
suggest_job_config(project_id: str, container_image: str) → JobInput
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_service_config`

```python
suggest_service_config(project_id: str, container_image: str) → ServiceInput
```

[summary] 



**Args:**
 
 - <b>`project_id`</b> (str):  [description] 
 - <b>`container_image`</b> (str):  [description] 



**Returns:**
 
 - <b>`ServiceInput`</b>:  [description] 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
