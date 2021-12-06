<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.deployment.kube_utils`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_label_selector`

```python
get_label_selector(label_pairs: List[Tuple[str, str]]) → str
```

Bring label tuples into the form required by the Kubernetes client, e.g. 'key1=value1,key2=value2,key3=value3)'. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_deployment_selection_labels`

```python
get_deployment_selection_labels(
    project_id: str,
    deployment_type: DeploymentType = <DeploymentType.SERVICE: 'service'>
) → str
```

Return selector identifying project services/jobs in the form Kubernetes expects a label selector. 



**Args:**
 
 - <b>`project_id`</b> (str):  The project id of the resources to select. 
 - <b>`deployment_type`</b> (DeploymentType, optional):  The deployment type by which the selected resources are filtered. Defaults to DeploymentType.SERVICE. 



**Returns:**
 
 - <b>`str`</b>:  Kubernetes label string in the form of 'key1=value1,key2=value2,key3=value3,...' 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_pod`

```python
get_pod(
    project_id: str,
    service_id: str,
    kube_namespace: str,
    core_api: CoreV1Api
) → Union[V1Pod, NoneType]
```

Get the pod filtered by the project id and service id labels in the given Kubernetes namespace. 



**Args:**
 
 - <b>`service_id`</b> (str):  If deployed via Contaxy, corresponds to the deployment id of the pod. 
 - <b>`kube_namespace`</b> (str):  The Kubernetes namespaces in which to look for the pod. 
 - <b>`core_api`</b> (kube_client.CoreV1Api):  Initialized Kubernetes CoreV1Api object. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  Raised when no pod matches the selection criteria. 



**Returns:**
 
 - <b>`Optional[V1Pod]`</b>:  Returns the pod matching the selection criteria. In case of replicas, multiple pods can match the criteria; in this case, the first pod is selected arbitrarily. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_pvc`

```python
create_pvc(
    pvc: Optional[V1PersistentVolumeClaim],
    kube_namespace: str,
    core_api: CoreV1Api
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L142"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_service`

```python
create_service(
    service_config: Optional[V1Service],
    kube_namespace: str,
    core_api: CoreV1Api
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_kube_service_config`

```python
build_kube_service_config(
    service_id: str,
    service: ServiceInput,
    project_id: str,
    kube_namespace: str
) → V1Service
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L208"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_pod_template_spec`

```python
build_pod_template_spec(
    project_id: str,
    service_id: str,
    service: Union[ServiceInput, JobInput],
    metadata: V1ObjectMeta,
    auth_manager: AuthManager,
    user_id: Optional[str] = None
) → V1PodTemplateSpec
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L294"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_deployment_metadata`

```python
build_deployment_metadata(
    kube_namespace: str,
    project_id: str,
    deployment_id: str,
    display_name: Optional[str],
    labels: Optional[Dict[str, str]],
    compute_resources: Optional[DeploymentCompute],
    endpoints: Optional[List[str]],
    deployment_type: DeploymentType = <DeploymentType.SERVICE: 'service'>,
    user_id: Optional[str] = None
) → V1ObjectMeta
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L329"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_kube_deployment_config`

```python
build_kube_deployment_config(
    service_id: str,
    service: ServiceInput,
    project_id: str,
    kube_namespace: str,
    auth_manager: AuthManager,
    user_id: Optional[str] = None
) → Tuple[V1Deployment, Union[V1PersistentVolumeClaim, NoneType]]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L407"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_project_network_policy_spec`

```python
build_project_network_policy_spec(
    project_id: str,
    kube_namespace: str
) → V1NetworkPolicy
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L451"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_or_create_project_network_policy`

```python
check_or_create_project_network_policy(
    network_policy: V1NetworkPolicy,
    networking_api: NetworkingV1Api
) → V1NetworkPolicy
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L465"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `wait_for_deployment`

```python
wait_for_deployment(
    deployment_name: str,
    kube_namespace: str,
    apps_api: AppsV1Api,
    timeout: int = 60
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L495"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `wait_for_job`

```python
wait_for_job(
    job_name: str,
    kube_namespace: str,
    batch_api: BatchV1Api,
    timeout: int = 60
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L513"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `wait_for_deletion`

```python
wait_for_deletion(
    api: Union[AppsV1Api, BatchV1Api],
    kube_namespace: str,
    deployment_id: str
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L534"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_deployment`

```python
map_deployment(deployment: Union[V1Deployment, V1Job]) → Dict[str, Any]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L614"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_kube_service`

```python
map_kube_service(deployment: V1Deployment) → Service
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L621"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_kube_job`

```python
map_kube_job(job: V1Job) → Job
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
