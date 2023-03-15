import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, Union

from fastapi.encoders import jsonable_encoder
from starlette.responses import Response

from contaxy import config
from contaxy.config import settings
from contaxy.managers.deployment.docker import DockerDeploymentPlatform
from contaxy.managers.deployment.kubernetes import KubernetesDeploymentPlatform
from contaxy.managers.deployment.utils import (
    create_deployment_config,
    enrich_deployment_with_runtime_info,
    get_job_collection_id,
    get_service_collection_id,
    split_image_name_and_tag,
)
from contaxy.operations import (
    AuthOperations,
    DeploymentOperations,
    JsonDocumentOperations,
    SystemOperations,
)
from contaxy.operations.components import ComponentOperations
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
from contaxy.schema.deployment import (
    ACTION_ACCESS,
    ACTION_DELIMITER,
    ACTION_RESTART,
    ACTION_START,
    ACTION_STOP,
    DeploymentStatus,
    DeploymentType,
    ServiceUpdate,
)
from contaxy.schema.shared import ResourceActionExecution
from contaxy.utils.auth_utils import parse_userid_from_resource_name
from contaxy.utils.id_utils import generate_short_uuid


class DeploymentManager(DeploymentOperations):
    def __init__(
        self,
        deployment_platform: Union[
            DockerDeploymentPlatform, KubernetesDeploymentPlatform
        ],
        component_manager: ComponentOperations,
    ):
        self._global_state = component_manager.global_state
        self._request_state = component_manager.request_state
        self.deployment_platform = deployment_platform
        self._component_manager = component_manager

    @property
    def _json_db_manager(self) -> JsonDocumentOperations:
        return self._component_manager.get_json_db_manager()

    @property
    def _system_manager(self) -> SystemOperations:
        return self._component_manager.get_system_manager()

    @property
    def _auth_manager(self) -> AuthOperations:
        return self._component_manager.get_auth_manager()

    def deploy_service(
        self,
        project_id: str,
        service_input: ServiceInput,
        action_id: Optional[str] = None,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
        wait: bool = False,
    ) -> Service:
        # Create service in DB
        db_service: Service = create_deployment_config(
            project_id=project_id,
            deployment_input=service_input,
            deployment_type=deployment_type,
            authorized_subject=self._request_state.authorized_subject,
            system_manager=self._system_manager,
            auth_manager=self._auth_manager,
            deployment_class=Service,
        )
        self._create_service_db_document(db_service, project_id)

        # Start service container
        if not service_input.is_stopped:
            deployed_service = self._deploy_service(
                project_id, db_service, action_id, wait
            )
            enrich_deployment_with_runtime_info(db_service, deployed_service)
        else:
            db_service.status = DeploymentStatus.STOPPED
        return db_service

    def list_services(
        self,
        project_id: str,
        deployment_type: Literal[
            DeploymentType.SERVICE, DeploymentType.EXTENSION
        ] = DeploymentType.SERVICE,
    ) -> List[Service]:
        service_docs = self._json_db_manager.list_json_documents(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_service_collection_id(project_id),
        )
        # Create lookup for all running services
        deployed_service_lookup: Dict[str, Service] = {
            service.id: service
            for service in self.deployment_platform.list_services(
                project_id, deployment_type
            )
            if service.id is not None
        }
        services = []
        # Go through all services in the DB and update their status and internal id
        for service_doc in service_docs:
            db_service = Service.parse_raw(service_doc.json_value)
            if db_service.deployment_type != deployment_type:
                continue
            deployed_service = deployed_service_lookup.pop(db_service.id, None)
            if deployed_service is None:
                db_service.status = DeploymentStatus.STOPPED
            else:
                enrich_deployment_with_runtime_info(db_service, deployed_service)
            services.append(db_service)
        # Add services to DB that were not added via the contaxy API
        for deployed_service in deployed_service_lookup.values():
            self._create_service_db_document(deployed_service, project_id)
            services.append(deployed_service)

        return services

    def _create_service_db_document(self, service: Service, project_id: str) -> None:
        self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_service_collection_id(project_id),
            key=service.id,
            json_document=service.json(exclude={"status", "internal_id"}),
            upsert=False,
        )

    def get_service_metadata(self, project_id: str, service_id: str) -> Service:
        db_service = self._get_service_from_db(project_id, service_id)
        try:
            deployed_service = self.deployment_platform.get_service_metadata(
                project_id, db_service.id
            )
            enrich_deployment_with_runtime_info(db_service, deployed_service)
        except ResourceNotFoundError:
            db_service.status = DeploymentStatus.STOPPED

        return db_service

    def update_service(
        self, project_id: str, service_id: str, service_update: ServiceUpdate
    ) -> Service:
        service_update_dict = jsonable_encoder(service_update, exclude_unset=True)

        if "display_name" in service_update_dict:
            raise ClientValueError("Display name of service cannot be updated!")
        if "container_image" in service_update_dict:
            image_name, image_tag = split_image_name_and_tag(
                service_update.container_image
            )
            self._system_manager.check_allowed_image(image_name, image_tag)
        service_update_dict.update(
            {
                "updated_at": str(datetime.now(timezone.utc)),
                "updated_by": parse_userid_from_resource_name(
                    self._request_state.authorized_subject
                ),
            }
        )
        service_doc = self._json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_service_collection_id(project_id),
            key=service_id,
            json_document=json.dumps(service_update_dict),
        )
        db_service = Service.parse_raw(service_doc.json_value)
        try:
            deployed_service = self._execute_restart_service_action(
                project_id, service_id
            )
            enrich_deployment_with_runtime_info(db_service, deployed_service)
        except ClientValueError:
            db_service.status = DeploymentStatus.STOPPED
            db_service.internal_id = None

        return db_service

    def update_service_access(self, project_id: str, service_id: str) -> None:
        user = self._request_state.authorized_subject
        self._json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_service_collection_id(project_id),
            key=service_id,
            json_document=json.dumps(
                {
                    "last_access_time": str(datetime.now(timezone.utc)),
                    "last_access_user": user,
                }
            ),
        )

    def delete_service(
        self, project_id: str, service_id: str, delete_volumes: bool = False
    ) -> None:
        db_service = self._get_service_from_db(project_id, service_id)

        try:
            self.deployment_platform.delete_service(
                project_id=project_id,
                service_id=db_service.id,
                delete_volumes=delete_volumes,
            )
        except ResourceNotFoundError:
            # Workspace is already stopped and service does not exist
            pass

        self._json_db_manager.delete_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_service_collection_id(project_id),
            key=db_service.id,
        )

    def delete_services(self, project_id: str) -> None:
        self.deployment_platform.delete_services(project_id)
        self._json_db_manager.delete_json_collection(
            config.SYSTEM_INTERNAL_PROJECT, get_service_collection_id(project_id)
        )

    def _get_service_from_db(self, project_id: str, service_id: str) -> Service:
        try:
            service_doc = self._json_db_manager.get_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=get_service_collection_id(project_id),
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
        return self.deployment_platform.get_service_logs(
            project_id, service_id, lines, since
        )

    def list_jobs(self, project_id: str) -> List[Job]:
        job_docs = self._json_db_manager.list_json_documents(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_job_collection_id(project_id),
        )
        deployed_job_lookup: Dict[Optional[str], Job] = {
            job.id: job for job in self.deployment_platform.list_jobs(project_id)
        }
        jobs = []
        for job_doc in job_docs:
            db_job = Job.parse_raw(job_doc.json_value)
            deployed_job = deployed_job_lookup.get(db_job.id)
            if deployed_job is None:
                db_job.status = DeploymentStatus.STOPPED
            else:
                enrich_deployment_with_runtime_info(db_job, deployed_job)
            jobs.append(db_job)

        return jobs

    def deploy_job(
        self,
        project_id: str,
        job_input: JobInput,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Job:
        # Create job in DB
        db_job: Job = create_deployment_config(
            project_id=project_id,
            deployment_input=job_input,
            deployment_type=DeploymentType.JOB,
            authorized_subject=self._request_state.authorized_subject,
            system_manager=self._system_manager,
            auth_manager=self._auth_manager,
            deployment_class=Job,
        )
        self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_job_collection_id(project_id),
            key=db_job.id,
            json_document=db_job.json(),
            upsert=False,
        )
        # Start job container
        deployed_job = self.deployment_platform.deploy_job(
            project_id, db_job, action_id, wait
        )
        enrich_deployment_with_runtime_info(db_job, deployed_job)
        return db_job

    def get_job_metadata(self, project_id: str, job_id: str) -> Job:
        db_job = self._get_job_from_db(project_id, job_id)
        try:
            deployed_job = self.deployment_platform.get_job_metadata(
                project_id, db_job.id
            )
            enrich_deployment_with_runtime_info(db_job, deployed_job)
        except ResourceNotFoundError:
            db_job.status = DeploymentStatus.UNKNOWN

        return db_job

    def delete_job(self, project_id: str, job_id: str) -> None:
        db_job = self._get_job_from_db(project_id, job_id)

        try:
            self.deployment_platform.delete_job(
                project_id=project_id,
                job_id=db_job.id,
            )
        except ResourceNotFoundError:
            pass

        self._json_db_manager.delete_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=get_job_collection_id(project_id),
            key=db_job.id,
        )

    def delete_jobs(
        self,
        project_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> None:
        if date_from and date_to:
            db_jobs = self.list_jobs(project_id)
            for db_job in db_jobs:
                if db_job.created_at and (
                    date_to.date() >= db_job.created_at.date() >= date_from.date()
                ):
                    self.delete_job(project_id, db_job.id)
        else:
            self.deployment_platform.delete_jobs(project_id)
            self._json_db_manager.delete_json_collection(
                config.SYSTEM_INTERNAL_PROJECT, get_job_collection_id(project_id)
            )

    def _get_job_from_db(self, project_id: str, job_id: str) -> Job:
        try:
            job_doc = self._json_db_manager.get_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=get_job_collection_id(project_id),
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
        return self.deployment_platform.get_job_logs(project_id, job_id, lines, since)

    def execute_service_action(
        self,
        project_id: str,
        service_id: str,
        action_id: str,
        action_execution: ResourceActionExecution = ResourceActionExecution(),
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
        self._deploy_service(project_id, service, wait=True)

    def _deploy_service(
        self,
        project_id: str,
        service: Service,
        action_id: Optional[str] = None,
        wait: bool = False,
    ) -> Service:
        # Make sure service access time is updated before starting the container
        # to avoid it being considered idle immediately due to an only access time
        self.update_service_access(project_id, service.id)
        return self.deployment_platform.deploy_service(
            project_id, service, action_id=action_id, wait=wait
        )

    def _execute_stop_service_action(
        self,
        project_id: str,
        service_id: str,
    ) -> None:
        service = self.get_service_metadata(project_id, service_id)
        if service.status == DeploymentStatus.STOPPED:
            raise ClientValueError(
                f"Action {ACTION_STOP} on service {service_id} can only be performed "
                f"when service is not stopped already!"
            )
        self.deployment_platform.delete_service(
            project_id, service_id, delete_volumes=service.clear_volume_on_stop
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
        self.deployment_platform.delete_service(
            project_id, service.id, delete_volumes=False
        )
        self._wait_for_deployment_deletion(project_id, service.id)
        return self._deploy_service(project_id, service, wait=True)

    def _wait_for_deployment_deletion(
        self, project_id: str, service_id: str, timeout_seconds: int = 60
    ) -> None:
        try:
            start_time = time.time()
            while time.time() - start_time < timeout_seconds:
                self.deployment_platform.get_service_metadata(project_id, service_id)
                time.sleep(3)
            raise ServerBaseError(
                f"Action {ACTION_RESTART} on service {service_id} failed as service "
                f"did not stop after waiting {timeout_seconds} seconds."
            )
        except ResourceNotFoundError:
            # Service was successfully deleted
            pass

    def execute_job_action(
        self,
        project_id: str,
        job_id: str,
        action_id: str,
        action_execution: ResourceActionExecution = ResourceActionExecution(),
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
        return self.deployment_platform.list_deploy_service_actions(project_id, service)

    def list_deploy_job_actions(
        self, project_id: str, job: JobInput
    ) -> List[ResourceAction]:
        return self.deployment_platform.list_deploy_job_actions(project_id, job)

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
        return ServiceInput(
            display_name=f"Service {generate_short_uuid()}",
            container_image=container_image,
        )

    def suggest_job_config(self, project_id: str, container_image: str) -> JobInput:
        # TODO: add sensible logic here
        return JobInput(
            display_name=f"Job {generate_short_uuid()}", container_image=container_image
        )
