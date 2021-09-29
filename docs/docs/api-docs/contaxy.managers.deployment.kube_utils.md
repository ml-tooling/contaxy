<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.deployment.kube_utils`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_label_selector`

```python
get_label_selector(label_pairs: List[Tuple[str, str]]) → str
```

Bring label tuples into the form required by the Kubernetes client, e.g. 'key1=value1,key2=value2,key3=value3)'. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_pod`

```python
get_pod(
    service_id: str,
    kube_namespace: str,
    core_api: CoreV1Api
) → Union[V1Pod, NoneType]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_pvc`

```python
create_pvc(
    pvc: Optional[V1PersistentVolumeClaim],
    kube_namespace: str,
    core_api: CoreV1Api
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_service`

```python
create_service(
    service_config: Optional[V1Service],
    kube_namespace: str,
    core_api: CoreV1Api
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_pod_template_spec`

```python
build_pod_template_spec(
    service_id: str,
    service: Union[ServiceInput, JobInput],
    metadata: V1ObjectMeta
) → V1PodTemplateSpec
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_kube_deployment_config`

```python
build_kube_deployment_config(
    service_id: str,
    service: ServiceInput,
    project_id: str,
    kube_namespace: str
) → Tuple[V1Deployment, Union[V1PersistentVolumeClaim, NoneType]]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L309"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_project_network_policy_spec`

```python
build_project_network_policy_spec(
    project_id: str,
    kube_namespace: str
) → V1NetworkPolicy
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L354"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_or_create_project_network_policy`

```python
check_or_create_project_network_policy(
    network_policy: V1NetworkPolicy,
    networking_api: NetworkingV1Api
) → V1NetworkPolicy
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L368"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L398"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L416"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_deployment`

```python
map_deployment(deployment: Union[V1Deployment, V1Job]) → Dict[str, Any]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L488"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_kube_service`

```python
map_kube_service(deployment: V1Deployment) → Service
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/kube_utils.py#L495"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_kube_job`

```python
map_kube_job(job: V1Job) → Job
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
