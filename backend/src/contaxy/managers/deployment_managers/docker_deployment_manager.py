from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import docker
import psutil

from ... import data_model
from .deployment_manager import JobDeploymentManager, ServiceDeploymentManager
from .docker_utils import (
    create_network,
    get_gpu_info,
    get_network_name,
    get_this_container,
    transform_job,
    transform_service,
)
from .utils import (
    APP_NAME_UPPER,
    DEFAULT_DEPLOYMENT_ACTION_ID,
    HOST_DATA_ROOT_PATH,
    NAMESPACE,
    ComputeResourcesError,
    DeploymentError,
    Labels,
    get_label_string,
    get_volume_name,
    normalize_service_name,
)


class DockerDeploymentManager(ServiceDeploymentManager, JobDeploymentManager):
    def __init__(self) -> None:
        self.client = docker.from_env()
        self.system_cpu_count = psutil.cpu_count()
        self.system_memory_in_mb = round(psutil.virtual_memory().total / 1024 / 1024, 1)
        self.system_gpu_count = get_gpu_info()

    def list_services(self, project_id: str) -> Any:
        containers = self.client.containers.list(
            filters={
                "label": [
                    get_label_string(Labels.NAMESPACE.value, NAMESPACE),
                    get_label_string(Labels.PROJECT_NAME.value, project_id),
                    get_label_string(
                        Labels.DEPLOYMENT_TYPE.value,
                        data_model.DeploymentType.SERVICE.value,
                    ),
                ]
            }
        )

        return [transform_service(container) for container in containers]

    def list_service_deploy_actions(
        self, service: Union[data_model.JobInput, data_model.ServiceInput]
    ) -> Any:
        compute_resources = service.compute or data_model.DeploymentCompute()
        min_cpus, min_memory, min_gpus = self.extract_minimal_resources(
            compute_resources
        )
        try:
            self.check_minimal_resources(
                min_cpus=min_cpus, min_memory=min_memory, min_gpus=min_gpus
            )
        except ComputeResourcesError:
            return []

        return [
            data_model.ResourceAction(
                action_id=DEFAULT_DEPLOYMENT_ACTION_ID,
                display_name=DEFAULT_DEPLOYMENT_ACTION_ID,
            )
        ]

    def get_service_metadata(self, service_id: str) -> Any:
        try:
            container = self.client.containers.get(service_id)
        except docker.errors.NotFound:
            return None

        return transform_service(container)

    def extract_minimal_resources(
        self, compute_resources: data_model.DeploymentCompute
    ) -> Tuple[int, int, int]:
        min_cpus = (
            compute_resources.min_cpus if compute_resources.min_cpus is not None else 0
        )
        min_memory = (
            compute_resources.min_memory
            if compute_resources.min_memory is not None
            else 0
        )
        min_gpus = (
            compute_resources.min_gpus if compute_resources.min_gpus is not None else 0
        )

        return min_cpus, min_memory, min_gpus

    def check_minimal_resources(
        self,
        min_cpus: int,
        min_memory: int,
        min_gpus: int,
        compute_resources: data_model.DeploymentCompute = None,
    ) -> None:
        if min_cpus > self.system_cpu_count:
            raise ComputeResourcesError(
                f"The minimal amount of cpus of {min_cpus} cannot be fulfilled as the system has only {self.system_cpu_count} cpus."
            )
        if min_memory > self.system_memory_in_mb:
            raise ComputeResourcesError(
                f"The minimal amount of memory of {min_memory}MB cannot be fulfilled as the system has only {self.system_memory_in_mb}MB memory"
            )
        if min_gpus > self.system_gpu_count:
            raise ComputeResourcesError(
                f"The minimal amount of gpus of {min_gpus} cannot be fulfilled as the system has only {self.system_gpu_count} gpus."
            )

        if compute_resources is None:
            return

        if compute_resources.min_replicas is not None:
            raise ComputeResourcesError("Replicas are not supported in Docker-mode")

    def define_mounts(
        self,
        project_id: str,
        container_name: str,
        compute_resources: data_model.DeploymentCompute,
        service_requirements: Optional[
            List[Union[data_model.DeploymentRequirement, str]]
        ] = [],
    ) -> list:
        mounts = []
        if (
            service_requirements
            and data_model.DeploymentRequirement.DOCKER_SOCKET in service_requirements
        ):
            # TODO: IMPORTANT mark container as having extended privileges so that on a higher level the platform
            # can prevent that a non-admin creates a container with the Docker socket mounted
            mounts.append(
                docker.types.Mount(
                    target="/var/run/docker.sock", source="/var/run/docker.sock"
                )
            )

        if (
            compute_resources.volume_path is not None
            and compute_resources.volume_path != ""
        ):
            mount_type = "bind" if HOST_DATA_ROOT_PATH != "" else "volume"
            mounts.append(
                docker.types.Mount(
                    target=str(compute_resources.volume_path),
                    source=f"{HOST_DATA_ROOT_PATH}{get_volume_name(project_id, container_name)}",
                    labels={
                        Labels.NAMESPACE.value: NAMESPACE,
                        Labels.PROJECT_NAME.value: project_id,
                        Labels.DEPLOYMENT_NAME.value: container_name,
                    },
                    type=mount_type,
                )
            )

        return mounts

    def create_container_config(
        self,
        service: Union[data_model.JobInput, data_model.ServiceInput],
        project_id: str,
    ) -> Dict[str, Any]:
        compute_resources = service.compute or data_model.DeploymentCompute()
        min_cpus, min_memory, min_gpus = self.extract_minimal_resources(
            compute_resources=compute_resources
        )
        self.check_minimal_resources(
            min_cpus=min_cpus, min_memory=min_memory, min_gpus=min_gpus
        )

        container_name = normalize_service_name(project_id, service.display_name)

        max_cpus = (
            compute_resources.max_cpus if compute_resources.max_cpus is not None else 1
        )
        max_memory = (
            compute_resources.max_memory
            if compute_resources.max_memory is not None
            else 6
        )
        # Make sure that the user-entered compute requirements are not bigger than the system's maximum available
        nano_cpus = min(max_cpus, self.system_cpu_count) * 1e9
        # Additionally for memory Docker requires at least 4MB for a container
        mem_limit = f"{max(6, min(max_memory, self.system_memory_in_mb))}MB"

        mounts = self.define_mounts(
            project_id=project_id,
            container_name=container_name,
            compute_resources=compute_resources,
            service_requirements=service.requirements,
        )

        environment = service.parameters or {}
        # The user MUST not be able to manually set (which) GPUs to use
        if "NVIDIA_VISIBLE_DEVICES" in environment:
            del environment["NVIDIA_VISIBLE_DEVICES"]
        if compute_resources.max_gpus is not None and compute_resources.max_gpus > 0:
            # TODO: add logic to prevent overcommitting of GPUs!
            environment["NVIDIA_VISIBLE_DEVICES"] = str(compute_resources.max_gpus)

        if compute_resources.max_volume_size is not None:
            environment[f"{APP_NAME_UPPER}_MAX_VOLUME_SIZE_MB"] = str(
                compute_resources.max_volume_size
            )
        min_lifetime = (
            compute_resources.min_lifetime
            if compute_resources.min_lifetime is not None
            else "0"
        )

        endpoints_label = ",".join(service.endpoints) if service.endpoints else None
        requirements_label = (
            ",".join(service.requirements) if service.requirements else None
        )
        additional_metadata = service.additional_metadata or {}
        return {
            "image": service.container_image,
            "command": service.command or None,
            "detach": True,
            "environment": environment,
            "labels": {
                Labels.DISPLAY_NAME.value: service.display_name,
                Labels.NAMESPACE.value: NAMESPACE,
                Labels.MIN_LIFETIME.value: min_lifetime,
                Labels.PROJECT_NAME.value: project_id,
                Labels.DEPLOYMENT_NAME.value: container_name,
                Labels.ENDPOINTS.value: endpoints_label,
                Labels.REQUIREMENTS.value: requirements_label,
                **additional_metadata,
            },
            "name": container_name,
            "nano_cpus": int(nano_cpus),
            "mem_limit": mem_limit,
            "network": get_network_name(project_id),
            "restart_policy": {"Name": "on-failure", "MaximumRetryCount": 10},
            "mounts": mounts if mounts != [] else None,
        }

    def handle_network(self, project_id: str) -> docker.models.networks.Network:
        network_name = get_network_name(project_id)
        try:
            network = self.client.networks.get(network_id=network_name)
        except docker.errors.NotFound:
            network = create_network(
                client=self.client,
                name=network_name,
                labels={
                    Labels.NAMESPACE.value: NAMESPACE,
                    Labels.PROJECT_NAME.value: project_id,
                },
            )

            backend_container = get_this_container(self.client)
            if backend_container:
                is_backend_connected_to_network = backend_container.attrs[
                    "NetworkSettings"
                ]["Networks"].get(network_name, False)
                if not is_backend_connected_to_network:
                    try:
                        network.connect(backend_container)
                    except docker.errors.APIError:
                        # Remove the network again as it is not connected to any service.
                        network.remove()
                        raise DeploymentError(
                            f"Could not connect the backend container to the network {network_name}"
                        )

        return network

    def deploy_service(self, service: data_model.ServiceInput, project_id: str) -> Any:
        container_config = self.create_container_config(
            service=service, project_id=project_id
        )
        container_config["labels"][
            Labels.DEPLOYMENT_TYPE.value
        ] = data_model.DeploymentType.SERVICE.value
        self.handle_network(project_id=project_id)
        container = self.client.containers.run(**container_config)
        return transform_service(container)

    def delete_service(
        self, service_id: str, delete_volumes: Optional[bool] = False
    ) -> Any:
        try:
            container = self.client.containers.get(service_id)
        except docker.errors.NotFound:
            return False

        try:
            container.stop()
        except docker.errors.APIError:
            pass

        container.remove(v=delete_volumes)

        return True

    def get_service_logs(
        self,
        service_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> Any:
        try:
            container = self.client.containers.get(service_id)
        except docker.errors.NotFound:
            return ""

        logs = container.logs(tail=lines or "all", since=since)

        if logs:
            logs = logs.decode("utf-8")

        return logs

    def cleanup(self) -> Any:
        # Remove all unused networks belonging to this namespace (to prevent removing networks handled by other applications)
        self.client.networks.prune(get_label_string(Labels.NAMESPACE.value, NAMESPACE))

        # TODO: remove all networks where the backend container is the only member

    def list_jobs(self, project_id: str) -> Any:
        containers = self.client.containers.list(
            filters={
                "label": [
                    get_label_string(Labels.NAMESPACE.value, NAMESPACE),
                    get_label_string(Labels.PROJECT_NAME.value, project_id),
                    get_label_string(
                        Labels.DEPLOYMENT_TYPE.value,
                        data_model.DeploymentType.JOB.value,
                    ),
                ]
            }
        )

        return [transform_service(container) for container in containers]

    def list_job_deploy_actions(self, job: data_model.JobInput) -> Any:
        return self.list_service_deploy_actions(service=job)

    def deploy_job(self, job: data_model.JobInput, project_id: str) -> Any:
        container_config = self.create_container_config(
            service=job, project_id=project_id
        )
        container_config["labels"][
            Labels.DEPLOYMENT_TYPE.value
        ] = data_model.DeploymentType.JOB.value
        self.handle_network(project_id=project_id)
        container = self.client.containers.run(**container_config)
        response_service = transform_job(container)
        return response_service

    def delete_job(self, job_id: str) -> Any:
        return self.delete_service(service_id=job_id, delete_volumes=True)

    def get_job_logs(
        self, job_id: str, lines: Optional[int] = None, since: Optional[datetime] = None
    ) -> Any:
        return self.get_service_logs(service_id=job_id, lines=lines, since=since)
