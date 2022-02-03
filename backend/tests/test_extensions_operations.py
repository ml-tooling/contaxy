from abc import ABC, abstractmethod
from random import randint
from typing import Generator

import pytest
import requests

from contaxy import config
from contaxy.clients import AuthClient, DeploymentManagerClient, ExtensionClient
from contaxy.managers.extension import ExtensionInput
from contaxy.operations.deployment import DeploymentOperations
from contaxy.operations.extension import ExtensionOperations
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
)
from contaxy.schema.extension import GLOBAL_EXTENSION_PROJECT, Extension
from contaxy.utils import auth_utils

from .conftest import test_settings

ui_extension_endpoint = "ui/endpoint"
api_extension_endpoint = "api/endpoint"


def create_test_extension_input(uid: int) -> ExtensionInput:
    return ExtensionInput(
        container_image="tutum/hello-world",  # not an extension image, but that is not needed (yet)
        display_name=f"{uid}-em-test-extension",
        description="This is a text extension",
        endpoints=["80"],
        ui_extension_endpoint=ui_extension_endpoint,
        api_extension_endpoint=api_extension_endpoint,
    )


def get_cleaned_extension_dict(extension: Extension):
    """
    Removes the started_at and status field from extension description because
    they should not be considered for comparison of extension objects.
    """
    extension_dict = extension.dict()
    for key in ["started_at", "status"]:
        extension_dict.pop(key)
    return extension_dict


class ExtensionOperationsTests(ABC):
    @property
    @abstractmethod
    def extension_manager(self) -> ExtensionOperations:
        pass

    @property
    @abstractmethod
    def deployment_manager(self) -> DeploymentOperations:
        pass

    def test_install_extension(self) -> None:
        uid = randint(1, 100000)
        project_id = f"{uid}-em-test-project"
        extension_input = create_test_extension_input(uid=uid)

        extension = self.extension_manager.install_extension(
            extension=extension_input,
            project_id=project_id,
        )

        assert extension
        assert extension.ui_extension_endpoint
        assert extension.api_extension_endpoint
        assert extension.ui_extension_endpoint.endswith(ui_extension_endpoint)
        assert extension.api_extension_endpoint.endswith(api_extension_endpoint)

        # TODO: delete extension is not implemented yet
        # self.extension_manager.delete_extension(
        #     project_id=project_id, extension_id=extension.id
        # )

    def test_list_extensions(self) -> None:
        uid = randint(1, 100000)
        project_id = f"{uid}-em-test-project"
        extension_input = create_test_extension_input(uid=uid)

        # Install local and global extension
        global_extension = self.extension_manager.install_extension(
            extension=extension_input,
            project_id=GLOBAL_EXTENSION_PROJECT,
        )
        project_extension = self.extension_manager.install_extension(
            extension=extension_input,
            project_id=project_id,
        )

        assert project_extension

        # List extensions should return project and global extensions
        extensions = self.extension_manager.list_extensions(project_id=project_id)

        assert extensions
        assert (
            len(extensions) > 1
        )  # The remote instance might already have extensions installed
        is_project_extension_found = False
        is_global_extension_found = False
        for e in extensions:
            if e.id == project_extension.id:
                assert get_cleaned_extension_dict(e) == get_cleaned_extension_dict(
                    project_extension
                )
                is_project_extension_found = True
            elif e.id == global_extension.id:
                assert get_cleaned_extension_dict(e) == get_cleaned_extension_dict(
                    global_extension
                )
                is_global_extension_found = True

        assert is_project_extension_found is True
        assert is_global_extension_found is True

        # TODO: delete extension is not implemented yet
        # self.extension_manager.delete_extension(
        #     project_id=project_id, extension_id=extension.id
        # )


# TODO: the issue with testing via local DeploymentManager is that again the differentiation between Docker and Kubernetes must be made...
# @pytest.mark.integration
# class TestExtensionManager(ExtensionOperationsTests):
#     @pytest.fixture(autouse=True)
#     def _init_extension_manager(
#         self, global_state: GlobalState, request_state: RequestState
#     ) -> Generator:
#         if config.settings.DEPLOYMENT_MANAGER == "kubernetes":
#             uid = randint(1, 100000)
#             deployment_manager = KubernetesDeploymentManager(
#                 global_state=global_state,
#                 request_state=request_state,
#                 kube_namespace=f"{uid}-deployment-manager-test-namespace",
#             )
#         else:
#             deployment_manager = DockerDeploymentManager(
#                 global_state=global_state, request_state=request_state
#             )
#         self._extension_manager = ExtensionManager(
#             global_state=global_state,
#             request_state=request_state,
#             deployment_manager=deployment_manager,
#         )

#         yield

#     @property
#     def deployment_manager(self) -> ExtensionOperations:
#         return self._extension_manager


@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_TESTS,
    reason="Remote Backend Tests are deactivated, use REMOTE_BACKEND_TESTS to activate.",
)
@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_ENDPOINT,
    reason="No remote backend is configured (via REMOTE_BACKEND_ENDPOINT).",
)
@pytest.mark.integration
class TestExtensionManagerViaRemoteEndpoint(ExtensionOperationsTests):
    @pytest.fixture(autouse=True)
    def _client(self, remote_client: requests.Session) -> requests.Session:
        return remote_client

    @pytest.fixture(autouse=True)
    def _init_managers(self, _client: requests.Session) -> Generator:
        self._auth_manager = AuthClient(_client)
        self._deployment_manager = DeploymentManagerClient(_client)
        self._extension_manager = ExtensionClient(_client)

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )

        yield

    @property
    def extension_manager(self) -> ExtensionOperations:
        return self._extension_manager

    @property
    def deployment_manager(self) -> DeploymentOperations:
        return self._deployment_manager

    def login_user(self, username: str, password: str) -> None:
        self._auth_manager.request_token(
            OAuth2TokenRequestFormNew(
                grant_type=OAuth2TokenGrantTypes.PASSWORD,
                username=username,
                password=password,
                scope=auth_utils.construct_permission(
                    "*", AccessLevel.ADMIN
                ),  # Get full scope
                set_as_cookie=True,
            )
        )
