from typing import Any
from fastapi import Depends, FastAPI, status
from fastapi.responses import HTMLResponse

from contaxy.schema import ServiceInput
from contaxy.schema.project import PROJECT_ID_PARAM
from contaxy.api.dependencies import (
    get_api_token,
    ComponentManager,
    get_component_manager,
)
from contaxy.clients import DeploymentManagerClient
from contaxy.clients.shared import BaseUrlSession
from contaxy.schema.exceptions import CREATE_RESOURCE_RESPONSES, UnauthenticatedError

import os

CONTAXY_ENDPOINT = os.getenv("CONTAXY_ENDPOINT", None)
if not CONTAXY_ENDPOINT:
    raise RuntimeError("CONTAXY_ENDPOINT must be set")

SELF_ACCESS_URL = os.getenv("CONTAXY_BASE_URL", "")

LABEL_EXTENSION_DEPLOYMENT_TYPE = "ctxy.workspaceExtension.deploymentType"

app = FastAPI()


@app.post(
    "/projects/{project_id}/workspace",
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

    if not token:
        raise UnauthenticatedError("No token provided.")

    # {env.CONTAXY_BASE_URL} will be replaced by Contaxy
    service.parameters["WORKSPACE_BASE_URL"] = "{env.CONTAXY_BASE_URL}"
    # TODO: In Contaxy, the labels are prefixed with the System Namespace (e.g. 'ctxy') -> should extension / user labels be prefixed as well? Problem of prefixing might be that the extension cannot find it's own labels
    service.metadata[LABEL_EXTENSION_DEPLOYMENT_TYPE] = "workspace"
    service.endpoints = ["8080b"]
    return DeploymentManagerClient(
        BaseUrlSession(
            base_url=CONTAXY_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
        )
    ).deploy_service(project_id=project_id, service=service)


@app.get(
    "/projects/{project_id}/workspace",
    summary="Get the launcher UI",
    status_code=status.HTTP_200_OK,
    responses={**CREATE_RESOURCE_RESPONSES},
    response_class=HTMLResponse,
)
def get_ui(
    project_id: str = PROJECT_ID_PARAM,
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token),
) -> Any:
    """Redirects to the existing user workspaces or """

    # Check the token and get the authorized user
    component_manager.verify_access(token)

    services = DeploymentManagerClient(
        BaseUrlSession(
            base_url=CONTAXY_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
        )
    ).list_services(project_id=project_id)

    html_body = ""
    for service in services:
        if (
            LABEL_EXTENSION_DEPLOYMENT_TYPE in service.metadata
            and service.metadata[LABEL_EXTENSION_DEPLOYMENT_TYPE] == "workspace"
        ):
            # TODO: do a redirect response that redirects to the workspace (service_access url, e.g. /projects/<project_id>/services/<service_id>/...)
            # TODO: instead of a redirect, it can return a list of workspaces (with a button to access the workspace directly, although this would be similar to the services screen then...)
            html_body = "The Workspace is already launched. Go to the services screen to access it."

    if not html_body:
        html_body = (
            "<button onclick='checkAndLaunchWorkspace()'>Launch Workspace</button>"
        )
    # if the service does not exist, send a launch screen to the use
    # TODO: rather use a nice web app here that can also be extended with resource settings etc. like JupyterHub
    html_content = f"""
    <html>
        <head>
            <title>Workspace Launcher</title>
            <script>
                function launchWorkspace() {{
                    fetch('{SELF_ACCESS_URL}/projects/{project_id}/workspace', {{ method: 'POST' }});
                }}
            </script>
        </head>
        <body>
            {html_body}
        </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=200)
