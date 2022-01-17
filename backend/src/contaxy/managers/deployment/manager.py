import time
from datetime import datetime
from typing import Dict, List, Literal, Optional

from starlette.responses import Response

from contaxy import config
from contaxy.config import settings
from contaxy.operations import DeploymentOperations, JsonDocumentOperations
from contaxy.schema import (
    ClientValueError,
    Job,
    JobInput,
    ResourceAction,
    ResourceNotFoundError,
    ServerBaseError,
    Service,
    ServiceInput,
)
from contaxy.schema.deployment import DeploymentStatus, DeploymentType, ServiceUpdate

ACTION_DELIMITER = "-"
ACTION_ACCESS = "access"
ACTION_START = "start"
ACTION_STOP = "stop"
ACTION_RESTART = "restart"


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
        wait: bool = False,
    ) -> Service:
        deployed_service = self.deployment_manager.deploy_service(
            project_id, service, action_id, deployment_type, wait
        )
        self._create_service_db_document(deployed_service, project_id)
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
        # Create lookup for all running services
        deployed_service_lookup: Dict[str, Service] = {
            service.id: service
            for service in self.deployment_manager.list_services(
                project_id, deployment_type
            )
            if service.id is not None
        }
        services = []
        # Go through all services in the DB and update their status and internal id
        for service_doc in service_docs:
            db_service = Service.parse_raw(service_doc.json_value)
            deployed_service = deployed_service_lookup.pop(db_service.id, None)
            if deployed_service is None:
                db_service.status = DeploymentStatus.STOPPED
                db_service.internal_id = None
            else:
                db_service.status = deployed_service.status
                db_service.internal_id = deployed_service.internal_id
            services.append(db_service)
        # Add services to DB that were not added via the contaxy API
        for deployed_service in deployed_service_lookup.values():
            self._create_service_db_document(deployed_service, project_id)
            services.append(deployed_service)

        return services

    def _create_service_db_document(self, service: Service, project_id: str) -> None:
        self.json_db.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_service_collection_id(project_id),
            key=service.id,
            json_document=service.json(exclude={"status", "internal_id"}),
            upsert=False,
        )

    def get_service_metadata(self, project_id: str, service_id: str) -> Service:
        db_service = self._get_service_from_db(project_id, service_id)
        try:
            deployed_service = self.deployment_manager.get_service_metadata(
                project_id, db_service.id
            )
            db_service.status = deployed_service.status
            db_service.internal_id = deployed_service.internal_id
        except ResourceNotFoundError:
            db_service.status = DeploymentStatus.STOPPED
            db_service.internal_id = None

        return db_service

    def update_service(
        self, project_id: str, service_id: str, service: ServiceUpdate
    ) -> Service:
        if "display_name" in service.dict(exclude_unset=True):
            raise ClientValueError("Display name of service cannot be updated!")
        service_doc = self.json_db.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=_get_service_collection_id(project_id),
            key=service_id,
            json_document=service.json(exclude_unset=True),
        )
        db_service = Service.parse_raw(service_doc.json_value)
        try:
            deployed_service = self._execute_restart_service_action(
                project_id, service_id
            )
            db_service.status = deployed_service.status
            db_service.internal_id = deployed_service.internal_id
        except ClientValueError:
            db_service.status = DeploymentStatus.STOPPED
            db_service.internal_id = None

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
                db_job.internal_id = None
            else:
                db_job.status = deployed_job.status
                db_job.internal_id = deployed_job.internal_id
            jobs.append(db_job)

        return jobs

    def deploy_job(
        self,
        project_id: str,
        job: JobInput,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Job:
        deployed_job = self.deployment_manager.deploy_job(
            project_id, job, action_id, wait
        )
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
            db_job.internal_id = deployed_job.internal_id
        except ResourceNotFoundError:
            db_job.status = DeploymentStatus.STOPPED
            db_job.internal_id = None

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
        if action_id == ACTION_START:
            self._execute_start_service_action(project_id, service_id)
        elif action_id == ACTION_STOP:
            self._execute_stop_service_action(project_id, service_id)
        elif action_id == ACTION_RESTART:
            self._execute_restart_service_action(project_id, service_id)
        else:
            return Response(
                content=f"No implementation for action id '{action_id}'",
                status_code=501,
            )
        return Response(
            content=f"Action {action_id} successfully executed.", status_code=200
        )

    def _execute_start_service_action(self, project_id: str, service_id: str) -> None:
        service = self.get_service_metadata(project_id, service_id)
        if service.status != DeploymentStatus.STOPPED:
            raise ClientValueError(
                f"Action {ACTION_START} on service {service_id} can only be performed "
                f"when service is stopped but status is {service.status}!"
            )
        self.deployment_manager.deploy_service(
            project_id, ServiceInput(**service.dict()), wait=True
        )

    def _execute_stop_service_action(self, project_id: str, service_id: str) -> None:
        service = self.get_service_metadata(project_id, service_id)
        if service.status == DeploymentStatus.STOPPED:
            raise ClientValueError(
                f"Action {ACTION_STOP} on service {service_id} can only be performed "
                f"when service is not stopped already!"
            )
        self.deployment_manager.delete_service(
            project_id, service_id, delete_volumes=False
        )

    def _execute_restart_service_action(
        self, project_id: str, service_id: str
    ) -> Service:
        service = self.get_service_metadata(project_id, service_id)
        if service.status == DeploymentStatus.STOPPED:
            raise ClientValueError(
                f"Action {ACTION_RESTART} on service {service_id} can only be performed "
                f"when service is not stopped already!"
            )
        return self._restart_service(project_id, service)

    def _restart_service(self, project_id: str, service: Service) -> Service:
        self.deployment_manager.delete_service(
            project_id, service.id, delete_volumes=False
        )
        self._wait_for_deployment_deletion(project_id, service.id)
        return self.deployment_manager.deploy_service(
            project_id, ServiceInput(**service.dict()), wait=True
        )

    def _wait_for_deployment_deletion(
        self, project_id: str, service_id: str, timeout_seconds: int = 60
    ) -> None:
        try:
            start_time = time.time()
            while time.time() - start_time < timeout_seconds:
                self.deployment_manager.get_service_metadata(project_id, service_id)
                time.sleep(3)
            raise ServerBaseError(
                f"Action {ACTION_RESTART} on service {service_id} failed as service "
                f"did not stop after waiting {timeout_seconds} seconds."
            )
        except ResourceNotFoundError:
            # Service was successfully deleted
            pass

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
        if service_metadata.status == DeploymentStatus.STOPPED:
            resource_actions.append(
                ResourceAction(action_id=ACTION_START, display_name="Start Service")
            )
        else:
            resource_actions.append(
                ResourceAction(action_id=ACTION_STOP, display_name="Stop Service")
            )
            resource_actions.append(
                ResourceAction(action_id=ACTION_RESTART, display_name="Restart Service")
            )
            resource_actions += self._get_service_access_actions(
                project_id, service_id, service_metadata
            )

        return resource_actions

    @staticmethod
    def _get_service_access_actions(
        project_id: str, service_id: str, service_metadata: Service
    ) -> List[ResourceAction]:
        if not service_metadata.endpoints:
            return []
        access_actions = []
        for endpoint in service_metadata.endpoints:
            if len(service_metadata.endpoints) > 1:
                display_name = f"Access Service on Endpoint: {endpoint}"
            else:
                display_name = "Access Service"
            access_actions.append(
                ResourceAction(
                    action_id=f"{ACTION_ACCESS}{ACTION_DELIMITER}{endpoint.replace('/', '')}",
                    display_name=display_name,
                    instructions=[
                        {
                            "type": "new-tab",
                            "url": f"{settings.CONTAXY_BASE_URL}/projects/{project_id}/services/{service_id}/access/{endpoint}",
                        }
                    ],
                )
            )
        return access_actions

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
