<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.deployment`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ServiceOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_services`

```python
delete_services(project_id: str) → None
```

Deletes all services associated with a project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_service`

```python
deploy_service(
    project_id: str,
    service_input: ServiceInput,
    action_id: Optional[str] = None,
    deployment_type: Literal[<SERVICE: 'service'>, <EXTENSION: 'extension'>] = <DeploymentType.SERVICE: 'service'>,
    wait: bool = False
) → Service
```

Deploys a service for the specified project. 

If no `action_id` is provided, the system will automatically select the best deployment option. 

Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions). 



**Args:**
 
 - <b>`project_id`</b> (str):  The id of the project that the service should be assigned to. 
 - <b>`service_input`</b> (ServiceInput):  The service input which can be used to configure the deployed service. 
 - <b>`action_id`</b> (Optional[str], optional):  The ID of the selected action. Defaults to `None`. 
 - <b>`deployment_type`</b> (One of [DeploymentType.SERVICE, DeploymentType.JOB]):  The deployment type of either Service or Extension (which is a subtype of Service). 
 - <b>`wait`</b> (bool, optional):  If set to True, the function will wait until the service was successfully created. 



**Returns:**
 
 - <b>`Service`</b>:  The metadata of the deployed service. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L216"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_service_action`

```python
execute_service_action(
    project_id: str,
    service_id: str,
    action_id: str,
    action_execution: ResourceActionExecution = ResourceActionExecution(parameters={})
) → Any
```

Executes the selected service action. 

The actions need to be first requested from the list_service_actions operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`action_id`</b> (str):  The ID of the selected action. 
 - <b>`action_execution`</b> (ResourceActionExecution):  The action execution request which contains the action parameters 



**Returns:**
 `None` or a redirect response to another URL. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L79"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_service_actions`

```python
list_service_actions(project_id: str, service_id: str) → List[ResourceAction]
```

Lists all actions available for the specified service. 

See the endpoint documentation for more information on the action mechanism. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 



**Returns:**
 
 - <b>`List[ResourceAction]`</b>:  Available actions for given services. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_services`

```python
list_services(
    project_id: str,
    deployment_type: Literal[<SERVICE: 'service'>, <EXTENSION: 'extension'>] = <DeploymentType.SERVICE: 'service'>
) → List[Service]
```

Lists all services associated with the given project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID to filter the services. 
 - <b>`deployment_type`</b> (One of [DeploymentType.SERVICE, DeploymentType.JOB]):  The deployment type of either Service or Extension (which is a subtype of Service). 



**Returns:**
 
 - <b>`List[Service]`</b>:  The list of services associated with the project. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_service_config`

```python
suggest_service_config(project_id: str, container_image: str) → ServiceInput
```

Suggests an input configuration based on the provided `container_image`. 

The suggestion is based on metadata extracted from the container image (e.g. labels) as well as suggestions based on previous project deployments with the same image. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`container_image`</b> (str):  The container image to use as context for the suggestion. 



**Returns:**
 
 - <b>`ServiceInput`</b>:  The suggested service configuration. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_service`

```python
update_service(
    project_id: str,
    service_id: str,
    service_update: ServiceUpdate
) → Service
```

Updates the service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`service_update`</b> (ServiceUpdate):  Updates that should be applied to the service 

**Returns:**
 
 - <b>`Service`</b>:  The updated service metadata 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_service_access`

```python
update_service_access(project_id: str, service_id: str) → None
```

Updates the last time the service was accessed and by which user. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `JobOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_job`

```python
delete_job(project_id: str, job_id: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L276"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_jobs`

```python
delete_jobs(project_id: str) → None
```

Deletes all jobs associated with a project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_job`

```python
deploy_job(
    project_id: str,
    job_input: JobInput,
    action_id: Optional[str] = None,
    wait: bool = False
) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L306"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_job_action`

```python
execute_job_action(
    project_id: str,
    job_id: str,
    action_id: str,
    action_execution: ResourceActionExecution = ResourceActionExecution(parameters={})
) → Any
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L288"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L268"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_metadata`

```python
get_job_metadata(project_id: str, job_id: str) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L256"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_deploy_job_actions`

```python
list_deploy_job_actions(project_id: str, job: JobInput) → List[ResourceAction]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L298"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_job_actions`

```python
list_job_actions(project_id: str, job_id: str) → List[ResourceAction]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L242"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_jobs`

```python
list_jobs(project_id: str) → List[Job]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_job_config`

```python
suggest_job_config(project_id: str, container_image: str) → JobInput
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L317"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DeploymentOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_job`

```python
delete_job(project_id: str, job_id: str) → None
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L276"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_jobs`

```python
delete_jobs(project_id: str) → None
```

Deletes all jobs associated with a project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_services`

```python
delete_services(project_id: str) → None
```

Deletes all services associated with a project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_job`

```python
deploy_job(
    project_id: str,
    job_input: JobInput,
    action_id: Optional[str] = None,
    wait: bool = False
) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deploy_service`

```python
deploy_service(
    project_id: str,
    service_input: ServiceInput,
    action_id: Optional[str] = None,
    deployment_type: Literal[<SERVICE: 'service'>, <EXTENSION: 'extension'>] = <DeploymentType.SERVICE: 'service'>,
    wait: bool = False
) → Service
```

Deploys a service for the specified project. 

If no `action_id` is provided, the system will automatically select the best deployment option. 

Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions). 



**Args:**
 
 - <b>`project_id`</b> (str):  The id of the project that the service should be assigned to. 
 - <b>`service_input`</b> (ServiceInput):  The service input which can be used to configure the deployed service. 
 - <b>`action_id`</b> (Optional[str], optional):  The ID of the selected action. Defaults to `None`. 
 - <b>`deployment_type`</b> (One of [DeploymentType.SERVICE, DeploymentType.JOB]):  The deployment type of either Service or Extension (which is a subtype of Service). 
 - <b>`wait`</b> (bool, optional):  If set to True, the function will wait until the service was successfully created. 



**Returns:**
 
 - <b>`Service`</b>:  The metadata of the deployed service. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L306"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_job_action`

```python
execute_job_action(
    project_id: str,
    job_id: str,
    action_id: str,
    action_execution: ResourceActionExecution = ResourceActionExecution(parameters={})
) → Any
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L216"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `execute_service_action`

```python
execute_service_action(
    project_id: str,
    service_id: str,
    action_id: str,
    action_execution: ResourceActionExecution = ResourceActionExecution(parameters={})
) → Any
```

Executes the selected service action. 

The actions need to be first requested from the list_service_actions operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`action_id`</b> (str):  The ID of the selected action. 
 - <b>`action_execution`</b> (ResourceActionExecution):  The action execution request which contains the action parameters 



**Returns:**
 `None` or a redirect response to another URL. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L288"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L268"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_job_metadata`

```python
get_job_metadata(project_id: str, job_id: str) → Job
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L79"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L256"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_deploy_job_actions`

```python
list_deploy_job_actions(project_id: str, job: JobInput) → List[ResourceAction]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L298"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_job_actions`

```python
list_job_actions(project_id: str, job_id: str) → List[ResourceAction]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L242"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_jobs`

```python
list_jobs(project_id: str) → List[Job]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_service_actions`

```python
list_service_actions(project_id: str, service_id: str) → List[ResourceAction]
```

Lists all actions available for the specified service. 

See the endpoint documentation for more information on the action mechanism. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 



**Returns:**
 
 - <b>`List[ResourceAction]`</b>:  Available actions for given services. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_services`

```python
list_services(
    project_id: str,
    deployment_type: Literal[<SERVICE: 'service'>, <EXTENSION: 'extension'>] = <DeploymentType.SERVICE: 'service'>
) → List[Service]
```

Lists all services associated with the given project. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID to filter the services. 
 - <b>`deployment_type`</b> (One of [DeploymentType.SERVICE, DeploymentType.JOB]):  The deployment type of either Service or Extension (which is a subtype of Service). 



**Returns:**
 
 - <b>`List[Service]`</b>:  The list of services associated with the project. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_job_config`

```python
suggest_job_config(project_id: str, container_image: str) → JobInput
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `suggest_service_config`

```python
suggest_service_config(project_id: str, container_image: str) → ServiceInput
```

Suggests an input configuration based on the provided `container_image`. 

The suggestion is based on metadata extracted from the container image (e.g. labels) as well as suggestions based on previous project deployments with the same image. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`container_image`</b> (str):  The container image to use as context for the suggestion. 



**Returns:**
 
 - <b>`ServiceInput`</b>:  The suggested service configuration. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_service`

```python
update_service(
    project_id: str,
    service_id: str,
    service_update: ServiceUpdate
) → Service
```

Updates the service. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 
 - <b>`service_update`</b> (ServiceUpdate):  Updates that should be applied to the service 

**Returns:**
 
 - <b>`Service`</b>:  The updated service metadata 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/deployment.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_service_access`

```python
update_service_access(project_id: str, service_id: str) → None
```

Updates the last time the service was accessed and by which user. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project ID associated with the service. 
 - <b>`service_id`</b> (str):  The ID of the service. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
