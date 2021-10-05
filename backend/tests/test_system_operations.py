from abc import ABC, abstractmethod
from typing import Generator

import pytest

from contaxy import config
from contaxy.managers.json_db.inmemory_dict import InMemoryDictJsonDocumentManager
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.managers.system import SystemManager
from contaxy.schema.exceptions import ClientValueError, ResourceNotFoundError
from contaxy.schema.system import AllowedImageInfo
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings


class SystemOperationsTests(ABC):
    @property
    @abstractmethod
    def system_manager(self) -> SystemManager:
        pass

    def test_allowed_images_crud(self):
        assert len(self.system_manager.list_allowed_images()) == 0
        # Add new allowed image
        allowed_image = AllowedImageInfo(image_name="test-image", image_tags=["0.1"])
        assert allowed_image == self.system_manager.add_allowed_image(allowed_image)
        # Check if allowed image is now set
        allowed_images = self.system_manager.list_allowed_images()
        assert len(allowed_images) == 1
        assert allowed_images[0] == allowed_image
        assert self.system_manager.get_allowed_image("test-image") == allowed_image
        # Update allowed image by replacing
        allowed_image_update = AllowedImageInfo(
            image_name="test-image", image_tags=["0.1", "0.2"]
        )
        self.system_manager.add_allowed_image(allowed_image_update)
        # Check if allowed image is now updated
        assert (
            self.system_manager.get_allowed_image("test-image") == allowed_image_update
        )
        # Delete allowed image
        self.system_manager.delete_allowed_image("test-image")
        assert len(self.system_manager.list_allowed_images()) == 0
        with pytest.raises(ResourceNotFoundError):
            self.system_manager.get_allowed_image("test-image")

    def test_all_images_allowed_by_default(self):
        assert len(self.system_manager.list_allowed_images()) == 0
        self.system_manager.check_image("test-image", "0.1")

    def test_only_specific_image_allowed(self):
        assert len(self.system_manager.list_allowed_images()) == 0
        self.system_manager.add_allowed_image(
            AllowedImageInfo(image_name="test-image", image_tags=["0.1", "0.2"])
        )
        self.system_manager.check_image("test-image", "0.1")
        with pytest.raises(ClientValueError):
            self.system_manager.check_image("other-image", "0.1")
        with pytest.raises(ClientValueError):
            self.system_manager.check_image("other-image", "0.3")

    def test_wildcard_for_allowed_image_tag(self):
        assert len(self.system_manager.list_allowed_images()) == 0
        self.system_manager.add_allowed_image(
            AllowedImageInfo(image_name="test-image", image_tags=["*"])
        )
        self.system_manager.check_image("test-image", "0.1")
        self.system_manager.check_image("test-image", "0.2")


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestSystemManagerWithPostgresDB(SystemOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_system_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        json_db = PostgresJsonDocumentManager(global_state, request_state)
        # Cleanup everything at the startup
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        self._system_manager = SystemManager(
            global_state, request_state, json_db, None, None
        )
        yield
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        # Do cleanup

    @property
    def system_manager(self) -> SystemManager:
        return self._system_manager


@pytest.mark.unit
class TestSystemManagerWithInMemoryDB(SystemOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_system_manager(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        json_db = InMemoryDictJsonDocumentManager(global_state, request_state)
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)
        self._system_manager = SystemManager(
            global_state, request_state, json_db, None, None
        )
        yield
        json_db.delete_json_collections(config.SYSTEM_INTERNAL_PROJECT)

    @property
    def system_manager(self) -> SystemManager:
        return self._system_manager
