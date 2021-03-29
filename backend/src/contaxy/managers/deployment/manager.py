from typing import List

from starlette.responses import Response

from contaxy.operations import DeploymentOperations, project
from contaxy.schema import JobInput, ResourceAction, ServiceInput


class DeploymentManager(DeploymentOperations):
    def access_service(
        self,
        project_id: str,
        service_id: str,
        endpoint: str,
    ) -> Response:
        # 501: not implemented
        return Response(status_code=501)

    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
    ) -> Response:
        return Response(501)

    def execute_job_action(
        self, project_id: str, job_id: str, action_id: str
    ) -> Response:
        # 501: not implemented
        return Response(status_code=501)

    def list_service_actions(
        self, project_id: str, service_id: str
    ) -> List[ResourceAction]:
        service_metadata = self.get_service_metadata(
            project_id=project_id, service_id=service_id
        )

        resource_actions: List[ResourceAction] = []
        if service_metadata.endpoints:
            for endpoint in service_metadata.endpoints:
                print(endpoint)
                endpoint = endpoint.replace("/", "")
                resource_actions.append(
                    ResourceAction(
                        action_id=f"access-{endpoint}",
                        display_name=endpoint,
                    )
                )

        return resource_actions

    def list_job_actions(
        self,
        project_id: str,
        job_id: str,
    ) -> List[ResourceAction]:
        return []

    def suggest_service_config(
        self,
        project_id: str,
        container_image: str,
    ) -> ServiceInput:
        # TODO: add sensible logic here
        return ServiceInput(container_image=container_image)

    def suggest_job_config(self, project_id: str, container_image: str) -> JobInput:
        # TODO: add sensible logic here
        return JobInput(container_image=container_image)
