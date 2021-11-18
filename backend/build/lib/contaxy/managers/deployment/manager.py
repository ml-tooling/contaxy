from typing import List

from starlette.responses import Response

from contaxy.config import settings
from contaxy.operations import DeploymentOperations
from contaxy.schema import JobInput, ResourceAction, ServiceInput

ACTION_DELIMITER = "-"
ACTION_ACCESS = "access"


class DeploymentManager(DeploymentOperations):
    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
    ) -> Response:
        # TODO: redirect from web app fetch / request does not work as the request itself is redirected and not the page.
        # try:
        #     if action_id.startswith(ACTION_ACCESS):
        #         port = action_id.split(ACTION_DELIMITER)[1]

        #         return RedirectResponse(
        #             url=f"{settings.CONTAXY_BASE_URL}/projects/{project_id}/services/{service_id}/access/{port}"
        #         )
        # except Exception:
        #     raise ServerBaseError("Could not execute action")

        # return Response(
        #     content=f"No implementation for action id '{action_id}'", status_code=501
        # )
        raise NotImplementedError

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
                endpoint = endpoint.replace("/", "")
                resource_actions.append(
                    ResourceAction(
                        action_id=f"{ACTION_ACCESS}{ACTION_DELIMITER}{endpoint}",
                        display_name=f"Endpoint: {endpoint}",
                        instructions=[
                            {
                                "type": "new-tab",
                                "url": f"{settings.CONTAXY_BASE_URL}/projects/{project_id}/services/{service_id}/access/{endpoint}",
                            }
                        ],
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
