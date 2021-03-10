from .deployment_manager import JobDeploymentManager, ServiceDeploymentManager


class KubernetesDeploymentManager(ServiceDeploymentManager, JobDeploymentManager):
    pass
