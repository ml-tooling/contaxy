import re
from datetime import datetime
from typing import List, Optional

from loguru import logger

from contaxy import config
from contaxy.managers.auth import AuthManager
from contaxy.operations import JsonDocumentOperations, ProjectOperations
from contaxy.schema.auth import AccessLevel, User
from contaxy.schema.exceptions import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from contaxy.schema.project import (
    MAX_PROJECT_ID_LENGTH,
    Project,
    ProjectCreation,
    ProjectInput,
)
from contaxy.utils import auth_utils, id_utils
from contaxy.utils.state_utils import GlobalState, RequestState


class ProjectManager(ProjectOperations):
    _PROJECT_COLLECTION = "projects"
    _PROJECT_NAME_TO_ID_REGEX = re.compile(r"^projects/([^/:\s]+)$")
    _MAX_ID_COUNTER = 9999

    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
        json_db_manager: JsonDocumentOperations,
        auth_manager: AuthManager,
    ):
        """Initializes the project manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
            json_db_manager: JSON DB Manager instance to store structured data.
            auth_manager: Auth Manager instance for permission handling.
        """
        self._global_state = global_state
        self._request_state = request_state
        self._json_db_manager = json_db_manager
        self._auth_manager = auth_manager

    def list_projects(self) -> List[Project]:
        authorized_user = None
        if self._request_state.authorized_access:
            authorized_user = self._request_state.authorized_access.authorized_subject
        projects: List[Project] = []
        if authorized_user:
            # Filter by the user
            resource_permissions = self._auth_manager.list_permissions(authorized_user)
            for permission in resource_permissions:
                resource_name, _ = auth_utils.parse_permission(permission)
                match = re.match(self._PROJECT_NAME_TO_ID_REGEX, resource_name)
                if match:
                    resource_id = match[1]
                    try:
                        project = self.get_project(resource_id)
                        projects.append(project)
                    except ResourceNotFoundError:
                        # this should not happen
                        logger.info(
                            f"Project not found: {resource_id} during list projects."
                        )
                        continue
        else:
            # TODO: also return all projects if user has admin role
            # If called without authorized user -> return all projects
            for json_document in self._json_db_manager.list_json_documents(
                config.SYSTEM_INTERNAL_PROJECT, self._PROJECT_COLLECTION
            ):
                projects.append(Project.parse_raw(json_document.json_value))

        return projects

    def create_project(
        self, project_input: ProjectCreation, technical_project: bool = False
    ) -> Project:
        try:
            # Check if project exists
            self.get_project(project_input.id)
            raise ResourceAlreadyExistsError(
                f"The project ID {project_input.id} is already used. Please select another project ID."
            )
        except ResourceNotFoundError:
            # This is expected, the project should not exist
            pass

        authorized_user = None
        if self._request_state.authorized_access:
            authorized_user = self._request_state.authorized_access.authorized_subject

        creation_timestamp = datetime.now()
        project = Project(
            **project_input.dict(exclude_unset=True),
            created_at=creation_timestamp,
            updated_at=creation_timestamp,
            created_by=authorized_user,
            updated_by=authorized_user,
            technical_project=technical_project,
        )

        created_document = self._json_db_manager.create_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._PROJECT_COLLECTION,
            key=project_input.id,
            json_document=project.json(),
        )

        created_project = Project.parse_raw(created_document.json_value)

        if authorized_user:
            # Add admin permission for the project to the authorized user
            assert created_project.id is not None
            self._auth_manager.add_permission(
                authorized_user,
                f"projects/{created_project.id}#{AccessLevel.ADMIN.value}",  # TODO how to set the resource name and kind?
            )
        return created_project

    def get_project(self, project_id: str) -> Project:
        json_document = self._json_db_manager.get_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._PROJECT_COLLECTION,
            key=project_id,
        )
        return Project.parse_raw(json_document.json_value)

    def update_project(self, project_id: str, project_input: ProjectInput) -> Project:
        updated_project = Project.parse_raw(project_input.json(exclude_unset=True))
        updated_project.updated_at = datetime.now()
        if self._request_state.authorized_access:
            updated_project.updated_by = (
                self._request_state.authorized_access.authorized_subject
            )

        updated_document = self._json_db_manager.update_json_document(
            project_id=config.SYSTEM_INTERNAL_PROJECT,
            collection_id=self._PROJECT_COLLECTION,
            key=project_id,
            json_document=updated_project.json(exclude_unset=True),
        )
        return Project.parse_raw(updated_document.json_value)

    def suggest_project_id(self, display_name: str) -> str:
        for i in range(self._MAX_ID_COUNTER):
            id_prefix = ""
            if i > 0:
                id_prefix = "-" + str(i)

            project_id = id_utils.generate_readable_id(
                display_name, max_length=MAX_PROJECT_ID_LENGTH, suffix=id_prefix
            )

            try:
                self.get_project(project_id)
            except ResourceNotFoundError:
                # No project exists with this ID -> return
                return project_id
        raise ClientValueError(
            f"Could not select project ID for name: {display_name}. Please try with another name."
        )

    def delete_project(self, project_id: str) -> None:
        # TODO: what to do on project deletion
        self._json_db_manager.delete_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._PROJECT_COLLECTION, project_id
        )

    def list_project_members(self, project_id: str) -> List[User]:
        pass

    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        permission_level: Optional[AccessLevel],
    ) -> List[User]:
        pass

    def remove_project_member(self, project_id: str, user_id: str) -> List[User]:
        pass
