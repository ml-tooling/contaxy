from typing import Dict, List
from uuid import uuid4

import pytest
from sqlalchemy.future import create_engine
from starlette.datastructures import State

from contaxy.config import settings
from contaxy.managers.json_db.postgres import PostgresJsonDocumentManager
from contaxy.schema.json_db import JsonDocument
from contaxy.utils.postgres_utils import create_jsonb_merge_patch_func
from contaxy.utils.state_utils import GlobalState, RequestState


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
    engine = create_engine(
        global_state.settings.POSTGRES_CONNECTION_URI,
        future=True,
    )
    # Ensure existence of db function for json merge patch
    create_jsonb_merge_patch_func(engine)
    return PostgresJsonDocumentManager(global_state, request_state)


def get_defaults() -> dict:
    json_dict = {
        "title": "Goodbye!",
        "author": {"givenName": "John", "familyName": "Doe"},
        "tags": ["example", "sample"],
        "content": "This will be unchanged",
    }

    return {
        "collection": "jdm_test",
        "project": "test-project",
        "key": str(uuid4()),
        "json_value": json_dict,
    }


@pytest.mark.integration
class TestPostgresJsonDocumentManager:
    def test_create_json_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:
        # TODO: Check for user data

        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, defaults)

        assert defaults.get("key") == created_doc.key
        assert created_doc.created_at

        # Test upsert case
        new_json_value: Dict = {}
        overwritten_doc = json_document_manager.create_json_document(
            defaults.get("project"),
            defaults.get("collection"),
            created_doc.key,
            new_json_value,
        )

        self._assert_updated_doc(created_doc, overwritten_doc, new_json_value)

    def test_get_json_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, defaults)

        read_doc = json_document_manager.get_json_document(
            defaults.get("project"), defaults.get("collection"), created_doc.key
        )

        assert read_doc.key == created_doc.key
        assert read_doc.created_at == created_doc.created_at

        try:
            json_document_manager.get_json_document(
                defaults.get("project"), defaults.get("collection"), str(uuid4())
            )
            assert False
        except ValueError:
            pass

    def test_get_json_documents(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:

        defaults = get_defaults()
        docs = []
        db_keys = []
        for i in range(2):
            doc = self._create_doc(json_document_manager, defaults)
            docs.append(doc)
            db_keys.append(doc.key)
            defaults.update({"key": str(uuid4())})

        read_docs = json_document_manager.get_json_documents(
            defaults.get("project"), defaults.get("collection"), db_keys
        )

        assert len(db_keys) == len(read_docs)

        for doc in read_docs:
            db_keys.index(doc.key)

    def test_delete_json_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, defaults)
        json_document_manager.delete_json_document(
            defaults.get("project"), defaults.get("collection"), created_doc.key
        )
        try:
            json_document_manager.get_json_document(
                defaults.get("project"), defaults.get("collection"), created_doc.key
            )
            assert False
        except ValueError:
            assert True

    def test_update_json_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:

        defaults = get_defaults()

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
        }
        desired_dict = {
            "title": "Hello!",
            "author": {"givenName": "John"},
            "tags": ["example"],
            "content": "This will be unchanged",
            "phoneNumber": "+01-123-456-7890",
        }

        created_doc = json_document_manager.create_json_document(
            defaults.get("project"),
            defaults.get("collection"),
            str(uuid4()),
            original_dict,
        )

        updated_doc = json_document_manager.update_json_document(
            defaults.get("project"),
            defaults.get("collection"),
            created_doc.key,
            changes_dict,
        )

        self._assert_updated_doc(created_doc, updated_doc, desired_dict)

        read_doc = json_document_manager.get_json_document(
            defaults.get("project"), defaults.get("collection"), updated_doc.key
        )

        self._assert_updated_doc(created_doc, read_doc, desired_dict)

        try:
            json_document_manager.update_json_document(
                defaults.get("project"),
                defaults.get("collection"),
                str(uuid4()),
                {},
            )
            assert False
        except ValueError:
            pass

    def test_list_json_documents(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:

        project_id = "test_get_collection_project"
        collection_id = "test_get_collection"

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
                project_id, collection_id, str(uuid4()), json_dict
            )

        docs = json_document_manager.list_json_documents(project_id, collection_id)
        assert len(docs) >= len(data)

        json_path_filter = '$ ? (@.title == "Hello!")'
        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            assert doc.json_value.get("title") == "Hello!"

        json_path_filter = '$ ? (@.title == "Goodbye!")'
        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            assert doc.json_value.get("title") == "Goodbye!"

        json_path_filter = '$ ? (@.author.givenName == "John")'
        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            author = doc.json_value.get("author")
            assert author.get("givenName") == "John"
        previous_result_count = len(docs)

        json_path_filter = (
            '$ ? (@.author.givenName == "John" && @.author.familyName == "Doe")'
        )

        docs = json_document_manager.list_json_documents(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            author = doc.json_value.get("author")
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
        except ValueError:
            pass

    def _create_doc(
        self, jdm: PostgresJsonDocumentManager, defaults: dict
    ) -> JsonDocument:
        return jdm.create_json_document(
            defaults.get("project"),
            defaults.get("collection"),
            defaults.get("key"),
            defaults.get("json_value"),
        )

    def test_delete_documents(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:

        db_keys: List[str] = []
        for i in range(5):
            doc = self._create_doc(json_document_manager, get_defaults())
            db_keys.append(doc.key)

        defaults = get_defaults()
        delete_count = json_document_manager.delete_documents(
            defaults.get("project"), defaults.get("collection"), db_keys
        )
        assert delete_count == len(db_keys)
        docs = json_document_manager.get_json_documents(
            defaults.get("project"), defaults.get("collection"), db_keys
        )

        assert len(docs) == 0

    def _assert_updated_doc(
        self, doc: JsonDocument, updated_doc: JsonDocument, new_json_value: dict
    ) -> None:
        assert updated_doc.key == doc.key
        assert updated_doc.json_value == new_json_value
        assert updated_doc.updated_at and updated_doc.created_at
        assert updated_doc.created_at < updated_doc.updated_at
