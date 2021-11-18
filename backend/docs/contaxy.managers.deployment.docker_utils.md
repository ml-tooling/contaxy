<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.deployment.docker_utils`




**Global Variables**
---------------
- **DEFAULT_DEPLOYMENT_ACTION_ID**
- **NO_LOGS_MESSAGE**
- **INITIAL_CIDR_FIRST_OCTET**
- **INITIAL_CIDR_SECOND_OCTET**
- **INITIAL_CIDR**
- **system_cpu_count**
- **system_memory_in_mb**
- **system_gpu_count**

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_container`

```python
map_container(container: Container) → Dict[str, Any]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L126"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_service`

```python
map_service(container: Container) → Service
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `map_job`

```python
map_job(container: Container) → Job
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L139"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_network`

```python
create_network(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>,
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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L205"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `handle_network`

```python
handle_network(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>,
    project_id: str
) → Network
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L224"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `connect_to_network`

```python
connect_to_network(container: Container, network: Network) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L244"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `reconnect_to_all_networks`

```python
reconnect_to_all_networks(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>
) → None
```

Connects the backend container to all networks that belong to the installation. 

A reconnect is required after the container was recreated (e.g. to update the image) and is therefore no longer part of all the networks. :param client: Docker client 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_backend_networks`

```python
get_backend_networks(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>
) → List[Network]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_project_container_selection_labels`

```python
get_project_container_selection_labels(
    project_id: str,
    deployment_type: DeploymentType = <DeploymentType.SERVICE: 'service'>
) → List[str]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L290"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_project_containers`

```python
get_project_containers(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>,
    project_id: str,
    deployment_type: DeploymentType = <DeploymentType.SERVICE: 'service'>
) → List[Container]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L309"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_project_container`

```python
get_project_container(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>,
    project_id: str,
    deployment_id: str,
    deployment_type: DeploymentType = <DeploymentType.SERVICE: 'service'>
) → Container
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L337"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_this_container`

```python
get_this_container(
    client: <module 'client' from '/github/workspace/backend/venv/lib/8/site-packages/docker/py'>
) → Container
```

This function returns the Docker container in which this code is running or None if it does not run in a container. 



**Args:**
 
 - <b>`client`</b> (docker.client):  The Docker client object 



**Returns:**
 
 - <b>`docker.models.containers.Container`</b>:  If this code runs in a container, it returns this container otherwise None 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L354"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_container`

```python
delete_container(container: Container, delete_volumes: bool = False) → None
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L371"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L397"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `extract_minimal_resources`

```python
extract_minimal_resources(
    compute_resources: DeploymentCompute
) → Tuple[int, int, int]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L413"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L455"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_container_config`

```python
create_container_config(
    service: Union[JobInput, ServiceInput],
    project_id: str,
    auth_manager: AuthManager,
    user_id: Optional[str] = None
) → Dict[str, Any]
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L560"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `read_container_logs`

```python
read_container_logs(
    container: Container,
    lines: Optional[int] = None,
    since: Optional[datetime] = None
) → str
```






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/deployment/docker_utils.py#L578"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_deploy_service_actions`

```python
list_deploy_service_actions(
    project_id: str,
    deploy_input: Union[ServiceInput, JobInput]
) → List[ResourceAction]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
