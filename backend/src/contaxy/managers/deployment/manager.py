from datetime import datetime
from typing import Dict, List, Literal, Optional

from starlette.responses import Response

from contaxy import config
from contaxy.config import settings
from contaxy.operations import DeploymentOperations, JsonDocumentOperations
from contaxy.schema import (
    Job,
    JobInput,
    ResourceAction,
    ResourceNotFoundError,
    Service,
    ServiceInput,
)
from contaxy.schema.deployment import DeploymentStatus, DeploymentType

ACTION_DELIMITER = "-"
ACTION_ACCESS = "access"


def _get_service_collection_id(project_id: str) -> str:
    return f"project_{project_id}_service_metadata"


def _get_job_collection_id(project_id: str) -> str:
    return f"project_{project_id}_job_metadata"


class DeploymentManagerWithDB(DeploymentOperations):
    def __init__(
        self,
        deployment_manager: DeploymentOperations,
        json_db_manager: JsonDocumentOperations,
    ):
        self.deployment_manager = deployment_manager
        self.json_db = json_db_manager

    def deploy_service(
        self,
        project_id: str,
        service: ServiceInput,
        action_id: Optional[str] = None,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> Service:
        deployed_service = self.deployment_manager.deploy_service(
            project_id, service, action_id, deployment_type
        )
        self.json_db.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_service_collection_id(project_id),
            key=deployed_service.id,
            json_document=deployed_service.json(),
            upsert=False,
        )
        return deployed_service

    def list_services(
        self,
        project_id: str,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> List[Service]:
        service_docs = self.json_db.list_json_documents(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_service_collection_id(project_id),
        )
        deployed_service_lookup: Dict[str, Service] = {
            service.id: service
            for service in self.deployment_manager.list_services(
                project_id, deployment_type
            )
            if service.id is not None
        }
        services = []
        # Go through all services in the DB and update their status
        for service_doc in service_docs:
            db_service = Service.parse_raw(service_doc.json_value)
            deployed_service = deployed_service_lookup.pop(db_service.id, None)
            if deployed_service is None:
                db_service.status = DeploymentStatus.STOPPED
            else:
                db_service.status = deployed_service.status
            services.append(db_service)
        # Add services to DB that were not added via the contaxy API
        for deployed_service in deployed_service_lookup.values():
            self.json_db.create_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=_get_service_collection_id(project_id),
                key=deployed_service.id,
                json_document=deployed_service.json(),
                upsert=False,
            )
            services.append(deployed_service)

        return services

    def get_service_metadata(self, project_id: str, service_id: str) -> Service:
        db_service = self._get_service_from_db(project_id, service_id)
        try:
            deployed_service = self.deployment_manager.get_service_metadata(
                project_id, db_service.id
            )
            db_service.status = deployed_service.status
        except ResourceNotFoundError:
            db_service.status = DeploymentStatus.STOPPED

        return db_service

    def delete_service(
        self, project_id: str, service_id: str, delete_volumes: bool = False
    ) -> None:
        db_service = self._get_service_from_db(project_id, service_id)

        try:
            self.deployment_manager.delete_service(
                project_id=project_id,
                service_id=db_service.id,
                delete_volumes=delete_volumes,
            )
        except ResourceNotFoundError:
            # Workspace is already stopped and service does not exist
            pass

        self.json_db.delete_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_service_collection_id(project_id),
            key=db_service.id,
        )

    def delete_services(self, project_id: str) -> None:
        self.deployment_manager.delete_services(project_id)
        self.json_db.delete_json_collection(
            config.SYSTEM_INTERNAL_PROJECT, _get_service_collection_id(project_id)
        )

    def _get_service_from_db(self, project_id: str, service_id: str) -> Service:
        try:
            service_doc = self.json_db.get_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=_get_service_collection_id(project_id),
                key=service_id,
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                f"The service with id {service_id} could not "
                f"be found in project {project_id}!"
            )
        db_service = Service.parse_raw(service_doc.json_value)
        return db_service

    def get_service_logs(
        self,
        project_id: str,
        service_id: str,
        lines: Optional[int],
        since: Optional[datetime],
    ) -> str:
        return self.deployment_manager.get_service_logs(
            project_id, service_id, lines, since
        )

    def list_jobs(self, project_id: str) -> List[Job]:
        job_docs = self.json_db.list_json_documents(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_job_collection_id(project_id),
        )
        deployed_job_lookup: Dict[Optional[str], Job] = {
            job.id: job for job in self.deployment_manager.list_jobs(project_id)
        }
        jobs = []
        for job_doc in job_docs:
            db_job = Job.parse_raw(job_doc.json_value)
            deployed_job = deployed_job_lookup.get(db_job.id)
            if deployed_job is None:
                db_job.status = DeploymentStatus.STOPPED
            else:
                db_job.status = deployed_job.status
            jobs.append(db_job)

        return jobs

    def deploy_job(
        self, project_id: str, job: JobInput, action_id: Optional[str] = None
    ) -> Job:
        deployed_job = self.deployment_manager.deploy_job(project_id, job, action_id)
        self.json_db.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_job_collection_id(project_id),
            key=deployed_job.id,
            json_document=deployed_job.json(),
            upsert=False,
        )
        return deployed_job

    def get_job_metadata(self, project_id: str, job_id: str) -> Job:
        db_job = self._get_job_from_db(project_id, job_id)
        try:
            deployed_job = self.deployment_manager.get_job_metadata(
                project_id, db_job.id
            )
            db_job.status = deployed_job.status
        except ResourceNotFoundError:
            db_job.status = DeploymentStatus.STOPPED

        return db_job

    def delete_job(self, project_id: str, job_id: str) -> None:
        db_job = self._get_job_from_db(project_id, job_id)

        try:
            self.deployment_manager.delete_job(
                project_id=project_id,
                job_id=db_job.id,
            )
        except ResourceNotFoundError:
            pass

        self.json_db.delete_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_job_collection_id(project_id),
            key=db_job.id,
        )

    def delete_jobs(self, project_id: str) -> None:
        self.deployment_manager.delete_jobs(project_id)
        self.json_db.delete_json_collection(
            config.SYSTEM_INTERNAL_PROJECT, _get_job_collection_id(project_id)
        )

    def _get_job_from_db(self, project_id: str, job_id: str) -> Job:
        try:
            job_doc = self.json_db.get_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=_get_job_collection_id(project_id),
                key=job_id,
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                f"The job with id {job_id} could not "
                f"be found in project {project_id}!"
            )
        db_job = Job.parse_raw(job_doc.json_value)
        return db_job

    def get_job_logs(
        self,
        project_id: str,
        job_id: str,
        lines: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> str:
        return self.deployment_manager.get_job_logs(project_id, job_id, lines, since)

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

    def list_deploy_service_actions(
        self, project_id: str, service: ServiceInput
    ) -> List[ResourceAction]:
        return self.deployment_manager.list_deploy_service_actions(project_id, service)

    def list_deploy_job_actions(
        self, project_id: str, job: JobInput
    ) -> List[ResourceAction]:
        return self.deployment_manager.list_deploy_job_actions(project_id, job)

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
