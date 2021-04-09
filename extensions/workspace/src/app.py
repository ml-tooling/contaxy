from typing import Any
from fastapi import Depends, FastAPI, status

from contaxy.schema import ServiceInput
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.api.dependencies import get_api_token
from contaxy.clients import DeploymentManagerClient
from contaxy.clients.shared import BaseUrlSession
from contaxy.schema.exceptions import CREATE_RESOURCE_RESPONSES

import os

CONTAXY_ENDPOINT = os.getenv("CONTAXY_ENDPOINT", None)
if not CONTAXY_ENDPOINT:
    raise RuntimeError("CONTAXY_ENDPOINT must be set")

CONTAXY_BASE_URL = os.getenv("CONTAXY_BASE_URL", "/")

app = FastAPI()


@app.post(
    "/projects/{project_id}/services",
    summary="Deploy a workspace.",
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
)
def deploy_workspace(
    service: ServiceInput,
    project_id: str = PROJECT_ID_PARAM,
    token: str = Depends(get_api_token),
) -> Any:
    """Deploy a workspace container as a Contaxy service."""
    # {env.CONTAXY_BASE_URL} will be replaced by Contaxy
    service.parameters["WORKSPACE_BASE_URL"] = "{env.CONTAXY_BASE_URL}"
    service.endpoints = ["8080b"]
    return DeploymentManagerClient(
        BaseUrlSession(
            base_url=CONTAXY_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
        )
    ).deploy_service(project_id=project_id, service=service)
