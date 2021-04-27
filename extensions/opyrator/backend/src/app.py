from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse
from contaxy.api.dependencies import get_api_token
from typing import Any
from contaxy.schema.exceptions import UnauthenticatedError
from contaxy.clients import DeploymentManagerClient
from contaxy.clients.shared import BaseUrlSession
from contaxy.schema import ServiceInput
import os
from starlette.staticfiles import StaticFiles

CONTAXY_API_ENDPOINT = os.getenv("CONTAXY_API_ENDPOINT", None)
if not CONTAXY_API_ENDPOINT:
    raise RuntimeError("CONTAXY_API_ENDPOINT must be set")

CONTAXY_SERVICE_URL = os.getenv("CONTAXY_SERVICE_URL", "")

api = FastAPI()


@api.post("/deploy/")
async def deploy(
    project_id: str = None,
    filekey: str = Form(...),
    token: str = Depends(get_api_token),
) -> Any:
    if not token:
        raise UnauthenticatedError("No token provided.")
    if not project_id:
        raise ValueError("Project information missing.")
    if not filekey:
        raise ValueError("A file key must be provided.")

    service = ServiceInput(
        container_image="opyrator-contaxy-playground",
        display_name=f"opyrator-{project_id}-{filekey}",
        metadata={"ctxy.deploymentSource": "opyrator-extension"},
        endpoints=["8080/"],
        parameters={"OPYRATOR_FILE": filekey},
    )

    session = BaseUrlSession(base_url=CONTAXY_API_ENDPOINT)
    session.headers = {"Authorization": f"Bearer {token}"}
    return DeploymentManagerClient(session).deploy_service(
        project_id=project_id, service=service
    )


# @api.get("/ui")
# async def get_ui(project_id: str = None) -> Any:
#     # content = """
#     #     <body>
#     #     <form action="/files/" enctype="multipart/form-data" method="post">
#     #     <input name="files" type="file" multiple>
#     #     <input type="submit">
#     #     </form>
#     #     <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
#     #     <input name="files" type="file" multiple>
#     #     <input type="submit">
#     #     </form>
#     #     </body>
#     # """
#     print(project_id)
#     service_url = CONTAXY_SERVICE_URL.replace("{project_id}", project_id) if project_id else CONTAXY_SERVICE_URL
#     content = f"""
#         <body>
#         <form action="{service_url}/deploy/" method="post">
#             <label for="filekey">Filekey</label>
#             <input id="filekey" name="filekey" type="text">
#             <input type="submit">
#         </form>
#         </body>
#     """

#     return HTMLResponse(content=content)
api.mount('/ui', StaticFiles(directory='/resources/webapp', html=True), name='webapp')
