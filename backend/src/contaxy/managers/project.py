import re
from datetime import datetime, timezone
from typing import List

from loguru import logger

from contaxy import config
from contaxy.operations import AuthOperations, JsonDocumentOperations, ProjectOperations
from contaxy.operations.components import ComponentOperations
from contaxy.schema.auth import USERS_KIND, AccessLevel, User
from contaxy.schema.exceptions import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from contaxy.schema.project import (
    MAX_PROJECT_ID_LENGTH,
    PROJECTS_KIND,
    Project,
    ProjectCreation,
    ProjectInput,
)
from contaxy.utils import auth_utils, id_utils


class ProjectManager(ProjectOperations):
    _PROJECT_COLLECTION = "projects"
    _PROJECT_NAME_TO_ID_REGEX = re.compile(r"^projects/([^/:\s]+)$")
    _MAX_ID_COUNTER = 9999

    def __init__(
        self,
        component_manager: ComponentOperations,
    ):
        """Initializes the project manager.

        Args:
            component_manager: Instance of the component manager that grants access to the other managers.
        """
        self._global_state = component_manager.global_state
        self._request_state = component_manager.request_state
        self._component_manager = component_manager

    @property
    def _json_db_manager(self) -> JsonDocumentOperations:
        return self._component_manager.get_json_db_manager()

    @property
    def _auth_manager(self) -> AuthOperations:
        return self._component_manager.get_auth_manager()

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
                try:
                    project_id = id_utils.extract_project_id_from_resource_name(
                        resource_name
                    )
                    try:
                        project = self.get_project(project_id)
                        # If the project is a technical project, it is only returned for users with the `projects#admin` permission
                        if (
                            not project.technical_project
                            or auth_utils.construct_permission(
                                "projects", AccessLevel.ADMIN
                            )
                            in resource_permissions
                            or auth_utils.construct_permission("*", AccessLevel.ADMIN)
                            in resource_permissions
                        ):
                            projects.append(project)
                    except ResourceNotFoundError:
                        # this should not happen
                        logger.info(
                            f"Project not found: {project_id} during list projects."
                        )
                        continue
                except ValueError:
                    # do nothing
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

        creation_timestamp = datetime.now(timezone.utc)
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
            self.add_project_member(
                created_project.id,
                id_utils.extract_user_id_from_resource_name(authorized_user),
                AccessLevel.ADMIN,
            )
        return created_project

    def get_project(self, project_id: str) -> Project:
        try:
            json_document = self._json_db_manager.get_json_document(
                project_id=config.SYSTEM_INTERNAL_PROJECT,
                collection_id=self._PROJECT_COLLECTION,
                key=project_id,
            )
        except ResourceNotFoundError as ex:
            raise ResourceNotFoundError(
                f"Project not found for ID: {project_id}"
            ) from ex

        return Project.parse_raw(json_document.json_value)

    def update_project(self, project_id: str, project_input: ProjectInput) -> Project:
        updated_project = Project.parse_raw(project_input.json(exclude_unset=True))
        updated_project.updated_at = datetime.now(timezone.utc)
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
        project_members = self.list_project_members(project_id)
        for project_member in project_members:
            # Remove all project permissions from all users
            self.remove_project_member(project_id, project_member.id)
        self._json_db_manager.delete_json_document(
            config.SYSTEM_INTERNAL_PROJECT, self._PROJECT_COLLECTION, project_id
        )

    def list_project_members(self, project_id: str) -> List[User]:
        project_member_resource_names: List[str] = []
        admin_permission = auth_utils.construct_permission(
            f"{PROJECTS_KIND}/{project_id}",
            AccessLevel.ADMIN,
        )
        project_member_resource_names.extend(
            self._auth_manager.list_resources_with_permission(
                admin_permission, resource_name_prefix=USERS_KIND
            )
        )

        write_permission = auth_utils.construct_permission(
            f"{PROJECTS_KIND}/{project_id}",
            AccessLevel.WRITE,
        )
        project_member_resource_names.extend(
            self._auth_manager.list_resources_with_permission(
                write_permission, resource_name_prefix=USERS_KIND
            )
        )

        read_permission = auth_utils.construct_permission(
            f"{PROJECTS_KIND}/{project_id}",
            AccessLevel.READ,
        )
        project_member_resource_names.extend(
            self._auth_manager.list_resources_with_permission(
                read_permission, resource_name_prefix=USERS_KIND
            )
        )

        project_users: List[User] = []

        for resource_name in project_member_resource_names:
            try:
                user_id = id_utils.extract_user_id_from_resource_name(resource_name)
            except ValueError:
                logger.warning(
                    "Failed to extract user id from resource name: " + resource_name
                )
                continue
            try:
                project_users.append(self._auth_manager.get_user(user_id))
            except ResourceNotFoundError:
                logger.warning(
                    f"User with id {user_id} does not exist anymore but its permissions have not been removed from the DB!"
                )
                continue

        return project_users

    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        access_level: AccessLevel,
    ) -> List[User]:

        try:
            # Check if user with the given ID exists
            self._auth_manager.get_user(user_id)
        except ResourceNotFoundError as ex:
            raise ResourceNotFoundError(f"User {user_id} does not exist.") from ex

        self._auth_manager.add_permission(
            f"{USERS_KIND}/{user_id}",
            auth_utils.construct_permission(
                f"{PROJECTS_KIND}/{project_id}",
                access_level,
            )
            # TODO how to set the resource name and kind?
        )
        return self.list_project_members(project_id)

    def _remove_project_member(self, project_id: str, user_id: str) -> None:
        self._auth_manager.remove_permission(
            f"{USERS_KIND}/{user_id}",
            auth_utils.construct_permission(
                f"{PROJECTS_KIND}/{project_id}", AccessLevel.ADMIN
            ),
            remove_sub_permissions=True,
        )

    def remove_project_member(self, project_id: str, user_id: str) -> List[User]:
        # Remove all permissions from the user that grant access to any part of the project
        self._remove_project_member(project_id, user_id)
        return self.list_project_members(project_id)
