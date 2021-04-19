from abc import ABC, abstractmethod
from random import randint
from typing import Generator

import pytest
import requests

from contaxy import config
from contaxy.clients import (
    AuthClient,
    DeploymentManagerClient,
    ExtensionClient,
    SystemClient,
)
from contaxy.managers.extension import ExtensionInput
from contaxy.operations.deployment import DeploymentOperations
from contaxy.operations.extension import ExtensionOperations
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
)
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

        extension = self.extension_manager.install_extension(
            extension=extension_input,
            project_id=project_id,
        )

        assert extension

        extensions = self.extension_manager.list_extensions(project_id=project_id)

        assert extensions
        assert (
            len(extensions) > 1
        )  # The remote instance might already have extensions installed
        is_extension_found = False
        for e in extensions:
            if extension.id == e.id:
                is_extension_found = True

        assert is_extension_found is True

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
        system_manager = SystemClient(_client)
        self._auth_manager = AuthClient(_client)
        self._deployment_manager = DeploymentManagerClient(_client)
        self._extension_manager = ExtensionClient(_client)
        system_manager.initialize_system()

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
