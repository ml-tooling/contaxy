<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.deployment`




**Global Variables**
---------------
- **OPEN_URL_REDIRECT**
- **RESOURCE_ID_REGEX**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_services`

```python
list_services(
    project_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all services associated with the given project. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `suggest_service_config`

```python
suggest_service_config(
    project_id: str = Path(Ellipsis),
    container_image: str = Query(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Suggests an input configuration based on the provided `container_image`. 

The suggestion is based on metadata extracted from the container image (e.g. labels) as well as suggestions based on previous project deployments with the same image. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_service_metadata`

```python
get_service_metadata(
    project_id: str = Path(Ellipsis),
    service_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the metadata of a single service. 

The returned metadata might be filtered based on the permission level of the authenticated user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_deploy_service_actions`

```python
list_deploy_service_actions(
    service: ServiceInput,
    project_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all available service deployment options (actions). 

The returned action IDs should be used when calling the [deploy_service](#services/deploy_service) operation. 

The action mechanism allows extensions to provide additional deployment options for a service based on the provided configuration. It works the following way: 

1. The user requests all available deployment options via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. 3. Extensions can run arbitrary code based on the provided service configuration and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [deploy_service](#services/deploy_service) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to deploy the service based on the provided configuration. 6. The return value of the operation should be a `Service` object. 

The same action mechanism is also used for other type of actions on resources. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `deploy_service`

```python
deploy_service(
    service: ServiceInput,
    project_id: str = Path(Ellipsis),
    action_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deploy a service for the specified project. 

If no `action_id` is provided, the system will automatically select the best deployment option. 

Available deployment options (actions) can be requested via the [list_deploy_service_actions](#services/list_deploy_service_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_deploy_service_actions](#services/list_deploy_service_actions). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L164"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_service`

```python
delete_service(
    project_id: str = Path(Ellipsis),
    service_id: str = Path(Ellipsis),
    delete_volumes: Optional[bool] = Query(False),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes a service. 

This will kill and remove the container and all associated deployment artifacts. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L186"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_service_logs`

```python
get_service_logs(
    project_id: str = Path(Ellipsis),
    service_id: str = Path(Ellipsis),
    lines: Optional[int] = Query(None),
    since: Optional[datetime] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the stdout/stderr logs of the service. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_service_actions`

```python
list_service_actions(
    project_id: str = Path(Ellipsis),
    service_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all actions available for the specified service. 

The returned action IDs should be used when calling the [execute_service_action](#services/execute_service_action) operation. 

The action mechanism allows extensions to provide additional functionality on services. It works the following way: 

1. The user requests all available actions via the [list_service_actions](#services/list_service_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_service_actions](#services/list_service_actions) operation. 3. Extensions can run arbitrary code - e.g., request and check the service metadata for compatibility - and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [execute_service_action](#services/execute_service_action) operation by providing the selected action ID.  The `action_id` from an extension contains the extension ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action. 6. The return value of the operation can be either a simple message (shown to the user) or a redirect to another URL (e.g., to show a web UI). 

The same action mechanism is also used for other resources (e.g., files, jobs). It can support a very broad set of use-cases, for example: Access to service endpoints, dashboards for monitoring, adminsitration tools, and more... 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L240"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `execute_service_action`

```python
execute_service_action(
    project_id: str = Path(Ellipsis),
    service_id: str = Path(Ellipsis),
    action_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Executes the selected service action. 

The actions need to be first requested from the [list_service_actions](#services/list_service_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_service_actions](#services/list_service_actions). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L269"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `access_service`

```python
access_service(
    project_id: str = Path(Ellipsis),
    service_id: str = Path(Ellipsis),
    endpoint: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Accesses the specified HTTP endpoint of the given service. 

The endpoint should be based on the endpoint information from the service metadata. This is usually a combination of port and URL path information. 

The user is expected to be redirected to the specified endpoint. If required, cookies can be attached to the response with session tokens to authorize access. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L300"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_jobs`

```python
list_jobs(
    project_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all jobs associated with the given project. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L317"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_job_metadata`

```python
get_job_metadata(
    project_id: str = Path(Ellipsis),
    job_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the metadata of a single job. 

The returned metadata might be filtered based on the permission level of the authenticated user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L337"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `suggest_job_config`

```python
suggest_job_config(
    project_id: str = Path(Ellipsis),
    container_image: str = Query(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Suggests an input configuration based on the provided `container_image`. 

The suggestion is based on metadata extracted from the container image (e.g. labels) as well as suggestions based on previous project deployments with the same image. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L361"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_deploy_job_actions`

```python
list_deploy_job_actions(
    job: JobInput,
    project_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all available job deployment options (actions). 

The returned action IDs should be used when calling the [deploy_job](#job/deploy_job) operation. 

The action mechanism allows extensions to provide additional deployment options for a job based on the provided configuration. It works the following way: 

1. The user requests all available deployment options via the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation. 3. Extensions can run arbitrary code based on the provided job configuration and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [deploy_job](#jobs/deploy_job) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to deploy the job based on the provided configuration. 6. The return value of the operation should be a `Job` object. 

The same action mechanism is also used for other type of actions on resources. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L393"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `deploy_job`

```python
deploy_job(
    job: JobInput,
    project_id: str = Path(Ellipsis),
    action_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deploy a job for the specified project. 

If no `action_id` is provided, the system will automatically select the best deployment option. 

Available actions can be requested via the [list_deploy_job_actions](#jobs/list_deploy_job_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_deploy_job_actions](#jobs/list_deploy_job_actions). 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L424"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_job`

```python
delete_job(
    project_id: str = Path(Ellipsis),
    job_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes a job. 

This will kill and remove the container and all associated deployment artifacts. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L443"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_job_logs`

```python
get_job_logs(
    project_id: str = Path(Ellipsis),
    job_id: str = Path(Ellipsis),
    lines: Optional[int] = Query(None),
    since: Optional[datetime] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the stdout/stderr logs of the job. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L464"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_job_actions`

```python
list_job_actions(
    project_id: str = Path(Ellipsis),
    job_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Query(None),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Lists all actions available for the specified job. 

The returned action IDs should be used when calling the [execute_job_action](#jobs/execute_job_action) operation. 

The action mechanism allows extensions to provide additional functionality on jobs. It works the following way: 

1. The user requests all available actions via the [list_job_actions](#jobs/list_job_actions) operation. 2. The operation will be forwarded to all installed extensions that have implemented the [list_job_actions](#jobs/list_job_actions) operation. 3. Extensions can run arbitrary code - e.g., request and check the job metadata for compatibility - and return a list of actions with self-defined action IDs. 4. The user selects one of those actions and triggers the [execute_job_action](#jobs/execute_job_action) operation by providing the selected action ID. The `action_id` from an extension contains the extension ID. 5. The operation is forwarded to the selected extension, which can run arbitrary code to execute the selected action. 6. The return value of the operation can be either a simple message (shown to the user) or a redirect to another URL (e.g., to show a web UI). 

The same action mechanism is also used for other resources (e.g., files, services). It can support a very broad set of use-cases, for example: Access to dashboards for monitoring, adminsitration tools, and more... 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/deployment.py#L497"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `execute_job_action`

```python
execute_job_action(
    project_id: str = Path(Ellipsis),
    job_id: str = Path(Ellipsis),
    action_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Executes the selected job action. 

The actions need to be first requested from the [list_job_actions](#jobs/list_job_actions) operation. If the action is from an extension, the `action_id` must be a composite ID with the following format: `{extension_id}~{action_id}`. 

The action mechanism is further explained in the description of the [list_job_actions](#jobs/list_job_actions). 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
