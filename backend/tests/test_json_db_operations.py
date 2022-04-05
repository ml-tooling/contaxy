import json
from abc import ABC, abstractmethod
from random import randint
from typing import Generator, List
from uuid import uuid4

import pytest
import requests
from fastapi.testclient import TestClient

from contaxy import config
from contaxy.clients import AuthClient, JsonDocumentClient
from contaxy.clients.system import SystemClient
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.operations.json_db import JsonDocumentOperations
from contaxy.schema.auth import (
    AccessLevel,
    OAuth2TokenGrantTypes,
    OAuth2TokenRequestFormNew,
)
from contaxy.schema.exceptions import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from contaxy.schema.json_db import JsonDocument
from contaxy.utils import auth_utils
from contaxy.utils.state_utils import GlobalState, RequestState

from .conftest import test_settings


def get_defaults() -> dict:
    json_dict = {
        "title": "Goodbye!",
        "author": {"givenName": "John", "familyName": "Doe"},
        "tags": ["example", "sample"],
        "content": "This will be unchanged",
    }

    return {
        "key": str(uuid4()),
        "json_value": json.dumps(json_dict),
    }


class JsonDocumentOperationsTests(ABC):
    COLLECTTION = "test-collection"

    @property
    @abstractmethod
    def json_document_manager(self) -> JsonDocumentOperations:
        pass

    @property
    @abstractmethod
    def project_id(self) -> str:
        """Returns the project id for the given run."""
        pass

    def test_create_json_document(self) -> None:
        # TODO: Check for user data

        defaults = get_defaults()
        created_doc = self._create_doc(
            self.json_document_manager, self.project_id, defaults
        )

        assert defaults.get("key") == created_doc.key
        assert created_doc.created_at

        # Test - Upsert case
        new_json_value = "{}"
        overwritten_doc = self.json_document_manager.create_json_document(
            self.project_id,
            self.COLLECTTION,
            created_doc.key,
            new_json_value,
        )

        self._assert_updated_doc(created_doc, overwritten_doc, new_json_value)

        # Test - Insert case with existing key
        with pytest.raises(ResourceAlreadyExistsError):
            self._create_doc(
                self.json_document_manager, self.project_id, defaults, upsert=False
            )

        # Test - Invalid json
        defaults.update({"json_value": "invalid-json"})
        with pytest.raises(ClientValueError):
            self._create_doc(self.json_document_manager, self.project_id, defaults)

    def test_get_json_document(self) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(
            self.json_document_manager, self.project_id, defaults
        )

        read_doc = self.json_document_manager.get_json_document(
            self.project_id, self.COLLECTTION, created_doc.key
        )

        assert read_doc.key == created_doc.key
        assert read_doc.created_at == created_doc.created_at
        assert json.loads(read_doc.json_value) == json.loads(created_doc.json_value)

        with pytest.raises(ResourceNotFoundError):
            self.json_document_manager.get_json_document(
                self.project_id, self.COLLECTTION, str(uuid4())
            )

    def test_delete_json_document(self) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(
            self.json_document_manager, self.project_id, defaults
        )
        self.json_document_manager.delete_json_document(
            self.project_id, self.COLLECTTION, created_doc.key
        )

        with pytest.raises(ResourceNotFoundError):
            self.json_document_manager.get_json_document(
                self.project_id, self.COLLECTTION, created_doc.key
            )

    def test_update_json_document(self) -> None:

        original_dict = {
            "title": "Goodbye!",
            "author": {"givenName": "John", "familyName": "Doe"},
            "tags": ["example", "sample"],
            "content": "This will be unchanged",
        }
        changes_dict = {
            "title": "Hello!",
            "phoneNumber": "+01-123-456-7890",
            "author": {"familyName": None},
            "tags": ["example"],
            "added-str": "foo-str",
            "added-list": ["foo", "bar", 5],
            "added-dict": {"foo": "bar"},
        }
        desired_dict = {
            "title": "Hello!",
            "author": {"givenName": "John"},
            "tags": ["example"],
            "content": "This will be unchanged",
            "phoneNumber": "+01-123-456-7890",
            "added-list": ["foo", "bar", 5],
            "added-str": "foo-str",
            "added-dict": {"foo": "bar"},
        }
        desired_json_value = json.dumps(desired_dict)

        created_doc = self.json_document_manager.create_json_document(
            self.project_id,
            self.COLLECTTION,
            str(uuid4()),
            json.dumps(original_dict),
        )

        updated_doc = self.json_document_manager.update_json_document(
            self.project_id,
            self.COLLECTTION,
            created_doc.key,
            json.dumps(changes_dict),
        )

        self._assert_updated_doc(created_doc, updated_doc, desired_json_value)

        read_doc = self.json_document_manager.get_json_document(
            self.project_id, self.COLLECTTION, updated_doc.key
        )

        self._assert_updated_doc(created_doc, read_doc, desired_json_value)

        with pytest.raises(ResourceNotFoundError):
            self.json_document_manager.update_json_document(
                self.project_id,
                self.COLLECTTION,
                str(uuid4()),
                "{}",
            )

    def test_list_json_documents(self) -> None:

        collection_id = self.COLLECTTION

        data = [
            {
                "title": "Goodbye!",
                "author": {"givenName": "John", "familyName": "Doe"},
                "tags": ["example", "sample"],
                "content": "This will be unchanged",
            },
            {
                "title": "Hello!",
                "author": {"givenName": "John"},
                "tags": ["example"],
                "content": "This will be unchanged",
                "phoneNumber": "+01-123-456-7890",
            },
        ]

        for json_dict in data:
            self.json_document_manager.create_json_document(
                self.project_id, collection_id, str(uuid4()), json.dumps(json_dict)
            )

        docs = self.json_document_manager.list_json_documents(
            self.project_id, collection_id
        )
        assert len(docs) >= len(data)

        json_path_filter = '$ ? (@.title == "Hello!")'
        docs = self.json_document_manager.list_json_documents(
            self.project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            assert json_value.get("title") == "Hello!"

        json_path_filter = '$ ? (@.title == "Goodbye!")'
        docs = self.json_document_manager.list_json_documents(
            self.project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            assert json_value.get("title") == "Goodbye!"

        json_path_filter = '$ ? (@.author.givenName == "John")'
        docs = self.json_document_manager.list_json_documents(
            self.project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            author = json_value.get("author")
            assert author.get("givenName") == "John"
        previous_result_count = len(docs)

        json_path_filter = (
            '$ ? (@.author.givenName == "John" && @.author.familyName == "Doe")'
        )

        docs = self.json_document_manager.list_json_documents(
            self.project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            author = json_value.get("author")
            assert (
                author.get("givenName") == "John" and author.get("familyName") == "Doe"
            )
        assert previous_result_count >= len(docs)
        previous_result_count = len(docs)

        with pytest.raises(ClientValueError):
            json_path_filter = '? (@.title == "Hello!")'
            self.json_document_manager.list_json_documents(
                self.project_id, collection_id, json_path_filter
            )

    def test_list_json_documents_by_key(self) -> None:

        docs = []
        db_keys = []
        for i in range(3):
            defaults = get_defaults()
            if i % 2 != 0:
                json_value = json.loads(defaults["json_value"])
                del json_value["author"]["familyName"]
                defaults["json_value"] = json.dumps(json_value)
            doc = self._create_doc(
                self.json_document_manager, self.project_id, defaults
            )
            docs.append(doc)
            db_keys.append(doc.key)

        read_docs = self.json_document_manager.list_json_documents(
            self.project_id, self.COLLECTTION, keys=db_keys
        )

        assert len(db_keys) == len(read_docs)

        for doc in read_docs:
            db_keys.index(doc.key)

        json_path_filter = (
            '$ ? (@.author.givenName == "John" && @.author.familyName == "Doe")'
        )
        read_docs = self.json_document_manager.list_json_documents(
            self.project_id,
            self.COLLECTTION,
            json_path_filter,
            db_keys,
        )
        for doc in read_docs:
            json_value = json.loads(doc.json_value)
            author = json_value.get("author")
            assert (
                author.get("givenName") == "John" and author.get("familyName") == "Doe"
            )
            db_keys.index(doc.key)

    def test_delete_json_collections(self) -> None:
        # Currently, there is no operation function to check whether the collections themselves are actually deleted
        key = "test"
        self.json_document_manager.create_json_document(
            self.project_id, self.COLLECTTION, key, json_document="{}"
        )
        self.json_document_manager.delete_json_collections(self.project_id)

        with pytest.raises(ResourceNotFoundError):
            self.json_document_manager.get_json_document(
                self.project_id, self.COLLECTTION, key
            )

    def test_delete_json_collection(self) -> None:
        # Currently, there is no operation function to check whether the collection itself is actually deleted
        key = "test"
        self.json_document_manager.create_json_document(
            self.project_id, self.COLLECTTION, key, json_document="{}"
        )
        self.json_document_manager.delete_json_collection(
            self.project_id, self.COLLECTTION
        )

        with pytest.raises(ResourceNotFoundError):
            self.json_document_manager.get_json_document(
                self.project_id, self.COLLECTTION, key
            )

    def _create_doc(
        self,
        jdm: JsonDocumentOperations,
        project_id: str,
        defaults: dict,
        upsert: bool = True,
    ) -> JsonDocument:
        return jdm.create_json_document(
            project_id,
            self.COLLECTTION,
            defaults.get("key"),
            defaults.get("json_value"),
            upsert,
        )

    def _assert_updated_doc(
        self, doc: JsonDocument, updated_doc: JsonDocument, new_json_value: str
    ) -> None:
        assert updated_doc.key == doc.key
        if new_json_value:
            assert json.loads(updated_doc.json_value) == json.loads(new_json_value)
        else:
            assert not updated_doc.json_value
        assert updated_doc.updated_at and updated_doc.created_at
        assert updated_doc.created_at < updated_doc.updated_at


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestJsonDocumentManagerWithPostgres(JsonDocumentOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(
        self, global_state: GlobalState, request_state: RequestState
    ) -> Generator:
        self._json_db = PostgresJsonDocumentManager(global_state, request_state)
        self._project_id = f"{randint(1, 100000)}-file-manager-test"
        self._json_db.delete_json_collections(self.project_id)
        yield
        self._json_db.delete_json_collections(self.project_id)

    @property
    def json_document_manager(self) -> JsonDocumentOperations:
        return self._json_db

    @property
    def project_id(self) -> str:
        return self._project_id

    def test_delete_documents(self) -> None:
        # Not implemented in default operations and endpoints.
        db_keys: List[str] = []
        for _ in range(5):
            doc = self._create_doc(
                self.json_document_manager, self.project_id, get_defaults()
            )
            db_keys.append(doc.key)

        delete_count = self.json_document_manager.delete_documents(
            self.project_id, self.COLLECTTION, db_keys
        )
        assert delete_count == len(db_keys)
        docs = self.json_document_manager.list_json_documents(
            self.project_id, self.COLLECTTION, keys=db_keys
        )

        assert len(docs) == 0


@pytest.mark.skipif(
    not test_settings.POSTGRES_INTEGRATION_TESTS,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
@pytest.mark.integration
class TestJsonDocumentManagerViaLocalEndpoints(JsonDocumentOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self) -> Generator:
        from contaxy.api import app

        with TestClient(app=app, root_path="/") as test_client:
            self._test_client = test_client
            system_manager = SystemClient(self._test_client)
            self._json_db = JsonDocumentClient(self._test_client)
            self._auth_manager = AuthClient(self._test_client)
            self._project_id = f"{randint(1, 100000)}-file-manager-test"
            system_manager.initialize_system()

            self.login_user(
                config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
            )
            # TODO: create project
            yield
            # Login as admin again -> logged in user might have been changed
            self.login_user(
                config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
            )
            self._json_db.delete_json_collections(self._project_id)

    @property
    def json_document_manager(self) -> JsonDocumentOperations:
        return self._json_db

    @property
    def project_id(self) -> str:
        return self._project_id

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


@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_ENDPOINT,
    reason="No remote backend is configured (via REMOTE_BACKEND_ENDPOINT).",
)
@pytest.mark.skipif(
    not test_settings.REMOTE_BACKEND_TESTS,
    reason="Remote Backend Tests are deactivated, use REMOTE_BACKEND_TESTS to activate.",
)
@pytest.mark.integration
class TestJsonDocumentManagerViaRemoteEndpoints(JsonDocumentOperationsTests):
    @pytest.fixture(autouse=True)
    def _init_managers(self, remote_client: requests.Session) -> Generator:
        self._endpoint_client = remote_client
        self._json_db = JsonDocumentClient(self._endpoint_client)
        self._auth_manager = AuthClient(self._endpoint_client)
        self._project_id = f"{randint(1, 100000)}-file-manager-test"

        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        # TODO: create project
        yield
        self.login_user(
            config.SYSTEM_ADMIN_USERNAME, config.SYSTEM_ADMIN_INITIAL_PASSWORD
        )
        self._json_db.delete_json_collections(self._project_id)

    @property
    def json_document_manager(self) -> JsonDocumentOperations:
        return self._json_db

    @property
    def project_id(self) -> str:
        return self._project_id

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
