import json
from random import randint
from typing import Generator, List
from uuid import uuid4

import pytest
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.schema.exceptions import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from contaxy.schema.json_db import JsonDocument
from contaxy.utils.state_utils import GlobalState, RequestState
from tests.unit_tests.conftest import test_settings


@pytest.fixture(scope="session")
def global_state() -> GlobalState:
    state = GlobalState(State())
    state.settings = settings
    return state


@pytest.fixture()
def request_state() -> RequestState:
    return RequestState(State())


@pytest.fixture()
def json_document_manager(
    global_state: GlobalState, request_state: RequestState
) -> PostgresJsonDocumentManager:
    return PostgresJsonDocumentManager(global_state, request_state)


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


@pytest.fixture(scope="function")
def project_id(
    json_document_manager: PostgresJsonDocumentManager,
) -> Generator[str, None, None]:
    project_id = f"{randint(1, 100000)}-file-manager-test"
    yield project_id
    if test_settings.POSTGRES_INTEGRATION_TESTS:
        json_document_manager.delete_json_collections(project_id)


@pytest.mark.skipif(
    test_settings.POSTGRES_INTEGRATION_TESTS is None,
    reason="Postgres Integration Tests are deactivated, use POSTGRES_INTEGRATION_TESTS to activate.",
)
class TestPostgresJsonDocumentManager:
    COLLECTTION = "test-collection"

    def test_create_json_document(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:
        # TODO: Check for user data

        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, project_id, defaults)

        assert defaults.get("key") == created_doc.key
        assert created_doc.created_at

        # Test - Upsert case
        new_json_value = "{}"
        overwritten_doc = json_document_manager.create_json_document(
            project_id,
            self.COLLECTTION,
            created_doc.key,
            new_json_value,
        )

        self._assert_updated_doc(created_doc, overwritten_doc, new_json_value)

        # Test - Insert case with existing key
        try:
            self._create_doc(json_document_manager, project_id, defaults, upsert=False)
            assert False
        except ResourceAlreadyExistsError:
            pass

        # Test - Invalid json
        defaults.update({"json_value": "invalid-json"})
        try:
            self._create_doc(json_document_manager, project_id, defaults)
            assert False
        except ClientValueError:
            pass

    def test_get_json_document(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, project_id, defaults)

        read_doc = json_document_manager.get_json_document(
            project_id, self.COLLECTTION, created_doc.key
        )

        assert read_doc.key == created_doc.key
        assert read_doc.created_at == created_doc.created_at
        assert json.loads(read_doc.json_value) == json.loads(created_doc.json_value)

        try:
            json_document_manager.get_json_document(
                project_id, self.COLLECTTION, str(uuid4())
            )
            assert False
        except ResourceNotFoundError:
            pass

    def test_delete_json_document(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, project_id, defaults)
        json_document_manager.delete_json_document(
            project_id, self.COLLECTTION, created_doc.key
        )
        try:
            json_document_manager.get_json_document(
                project_id, self.COLLECTTION, created_doc.key
            )
            assert False
        except ResourceNotFoundError:
            assert True

    def test_update_json_document(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:

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

        created_doc = json_document_manager.create_json_document(
            project_id,
            self.COLLECTTION,
            str(uuid4()),
            json.dumps(original_dict),
        )

        updated_doc = json_document_manager.update_json_document(
            project_id,
            self.COLLECTTION,
            created_doc.key,
            json.dumps(changes_dict),
        )

        self._assert_updated_doc(created_doc, updated_doc, desired_json_value)

        read_doc = json_document_manager.get_json_document(
            project_id, self.COLLECTTION, updated_doc.key
        )

        self._assert_updated_doc(created_doc, read_doc, desired_json_value)

        try:
            json_document_manager.update_json_document(
                project_id,
                self.COLLECTTION,
                str(uuid4()),
                "{}",
            )
            assert False
        except ResourceNotFoundError:
            pass

    def test_list_json_documents(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:

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
            json_document_manager.create_json_document(
                project_id, collection_id, str(uuid4()), json.dumps(json_dict)
            )

        docs = json_document_manager.list_json_documents(project_id, collection_id)
        assert len(docs) >= len(data)

        json_path_filter = '$ ? (@.title == "Hello!")'
        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            assert json_value.get("title") == "Hello!"

        json_path_filter = '$ ? (@.title == "Goodbye!")'
        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            assert json_value.get("title") == "Goodbye!"

        json_path_filter = '$ ? (@.author.givenName == "John")'
        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            author = json_value.get("author")
            assert author.get("givenName") == "John"
        previous_result_count = len(docs)

        json_path_filter = (
            '$ ? (@.author.givenName == "John" && @.author.familyName == "Doe")'
        )

        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            json_value = json.loads(doc.json_value)
            author = json_value.get("author")
            assert (
                author.get("givenName") == "John" and author.get("familyName") == "Doe"
            )
        assert previous_result_count >= len(docs)
        previous_result_count = len(docs)

        try:
            json_path_filter = '? (@.title == "Hello!")'
            json_document_manager.list_json_documents(
                project_id, collection_id, json_path_filter
            )
            assert False
        except ClientValueError:
            pass

    def test_list_json_documents_by_key(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:

        docs = []
        db_keys = []
        for i in range(3):
            defaults = get_defaults()
            if i % 2 != 0:
                json_value = json.loads(defaults["json_value"])
                del json_value["author"]["familyName"]
                defaults["json_value"] = json.dumps(json_value)
            doc = self._create_doc(json_document_manager, project_id, defaults)
            docs.append(doc)
            db_keys.append(doc.key)

        read_docs = json_document_manager.list_json_documents(
            project_id, self.COLLECTTION, keys=db_keys
        )

        assert len(db_keys) == len(read_docs)

        for doc in read_docs:
            db_keys.index(doc.key)

        json_path_filter = (
            '$ ? (@.author.givenName == "John" && @.author.familyName == "Doe")'
        )
        read_docs = json_document_manager.list_json_documents(
            project_id,
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

    def test_delete_documents(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:

        db_keys: List[str] = []
        for i in range(5):
            doc = self._create_doc(json_document_manager, project_id, get_defaults())
            db_keys.append(doc.key)

        delete_count = json_document_manager.delete_documents(
            project_id, self.COLLECTTION, db_keys
        )
        assert delete_count == len(db_keys)
        docs = json_document_manager.list_json_documents(
            project_id, self.COLLECTTION, keys=db_keys
        )

        assert len(docs) == 0

    def test_delete_json_collections(
        self, json_document_manager: PostgresJsonDocumentManager, project_id: str
    ) -> None:
        key = "test"
        json_document_manager.create_json_document(
            project_id, self.COLLECTTION, key, json_document="{}"
        )
        json_document_manager.delete_json_collections(project_id)
        try:
            json_document_manager.get_json_document(project_id, self.COLLECTTION, key)
            assert False
        except ResourceNotFoundError:
            pass

    def _create_doc(
        self,
        jdm: PostgresJsonDocumentManager,
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
