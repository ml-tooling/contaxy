<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.deployment.docker_utils`




**Global Variables**
---------------
- **DEFAULT_DEPLOYMENT_ACTION_ID**
- **INITIAL_CIDR_FIRST_OCTET**
- **INITIAL_CIDR_SECOND_OCTET**
- **INITIAL_CIDR**
- **system_cpu_count**
- **system_memory_in_mb**
- **system_gpu_count**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_container`

```python
map_container(container: Container) → Dict[str, Any]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_service`

```python
map_service(container: Container) → Service
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_job`

```python
map_job(container: Container) → Job
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_network`

```python
create_network(
    client: <module 'client' from '/root/local/share/virtualenvs/backend-VRxcNolS/lib/8/site-packages/docker/py'>,
    name: str,
    labels: Dict[str, str]
) → Network
```

Create a new network to put the new container into it. 

Containers are separated by networks to prevent them from seeing each other. Determine whether a new subnet has to be used. Otherwise, the default Docker subnet would be used and, as a result, the amount of networks that can be created is strongly limited. We create networks in the range of 172.33-255.0.0/24 whereby Docker by default uses the range 172.17-32.0.0 See: https://stackoverflow.com/questions/41609998/how-to-increase-maximum-docker-network-on-one-server ; https://loomchild.net/2016/09/04/docker-can-create-only-31-networks-on-a-single-machine/ 



**Args:**
 
 - <b>`network_name`</b> (str):  name of the network to be created 
 - <b>`network_labels`</b> (Dict[str, str]):  labels that will be attached to the network 

**Raises:**
 
 - <b>`docker.errors.APIError`</b>:  Thrown by `docker.client.networks.create` upon error. 



**Returns:**
 
 - <b>`docker.Network`</b>:  the newly created network or the existing network with the given name 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L175"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `handle_network`

```python
handle_network(
    client: <module 'client' from '/root/local/share/virtualenvs/backend-VRxcNolS/lib/8/site-packages/docker/py'>,
    project_id: str
) → Network
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L209"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_this_container`

```python
get_this_container(
    client: <module 'client' from '/root/local/share/virtualenvs/backend-VRxcNolS/lib/8/site-packages/docker/py'>
) → Container
```

This function returns the Docker container in which this code is running or None if it does not run in a container. 



**Args:**
 
 - <b>`client`</b> (docker.client):  The Docker client object 



**Returns:**
 
 - <b>`docker.models.containers.Container`</b>:  If this code runs in a container, it returns this container otherwise None 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L226"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_minimal_resources`

```python
check_minimal_resources(
    min_cpus: int,
    min_memory: int,
    min_gpus: int,
    compute_resources: DeploymentCompute = None
) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L252"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `extract_minimal_resources`

```python
extract_minimal_resources(
    compute_resources: DeploymentCompute
) → Tuple[int, int, int]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L268"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `define_mounts`

```python
define_mounts(
    project_id: str,
    container_name: str,
    compute_resources: DeploymentCompute,
    service_requirements: Optional[List[str]] = []
) → list
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L305"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_container_config`

```python
create_container_config(
    service: Union[JobInput, ServiceInput],
    project_id: str
) → Dict[str, Any]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L399"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_deploy_service_actions`

```python
list_deploy_service_actions(
    project_id: str,
    deploy_input: Union[ServiceInput, JobInput]
) → List[ResourceAction]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._