import json
import os
from typing import Generator, List
from uuid import uuid4

import pytest
from sqlalchemy import MetaData
from sqlalchemy.future import Engine, create_engine

from contaxy.managers.json_db.postgres import (
    PostgresJsonDocumentManager,
    create_jsonb_merge_patch_func,
)
from contaxy.schema.json_db import JsonDocument

from .utils.db_utils import destroy_db, start_db


@pytest.fixture(scope="session")
def settings() -> dict:

    CONTAINER_NAME = "ct_postgres_test"

    return {
        "user": os.getenv("POSTGRES_USER", "admin"),
        "pw": os.getenv("POSTGRES_PASSWORD", "admin"),
        "host": os.getenv("POSTGRES_ENDPOINT")
        if os.getenv("POSTGRES_ENDPOINT")
        else CONTAINER_NAME,
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "db_name": os.getenv("DB_NAME", "jdm_test"),
        "docker_network": os.getenv("DOCKER_NETWORK"),
        "docker_image": os.getenv("POSTGRES_DOCKER_IMAGE", "postgres:11"),
        "container_name": "ct_postgres_test"
        if not os.getenv("POSTGRES_ENDPOINT")
        else CONTAINER_NAME,
    }


@pytest.fixture(scope="session")
def db_engine(settings: dict) -> Generator[Engine, None, None]:
    if not settings.get("container_name"):
        yield
        return

    start_db(settings)

    url = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
        settings.get("user"),
        settings.get("pw"),
        settings.get("host"),
        settings.get("port"),
        settings.get("db_name"),
    )

    engine = create_engine(
        url,
        future=True,
    )
    # Test the DB connection
    engine.connect()

    yield engine

    destroy_db(settings)


@pytest.fixture(scope="session")
def json_document_manager(db_engine: Engine) -> PostgresJsonDocumentManager:
    # Create the db function for json merge patch needed
    create_jsonb_merge_patch_func(db_engine)
    return PostgresJsonDocumentManager(db_engine, metadata=MetaData())


def get_defaults() -> dict:
    json_dict = {
        "title": "Goodbye!",
        "author": {"givenName": "John", "familyName": "Doe"},
        "tags": ["example", "sample"],
        "content": "This will be unchanged",
    }

    json_value = json.dumps(json_dict)
    return {
        "collection": "jdm_test",
        "project": "test-project",
        "key": str(uuid4()),
        "json_value": json_value,
    }


@pytest.mark.unit
class TestPostgresJsonDocumentManager:
    def test_create_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:
        # TODO: Check for user data

        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, defaults)

        assert defaults.get("key") == created_doc.key
        assert created_doc.created_at

        # Test upsert case
        new_json_value: dict = {}
        created_doc.json_value = new_json_value
        overwritten_doc = json_document_manager.create_document(
            defaults.get("project"), defaults.get("collection"), created_doc
        )

        self._assert_updated_doc(created_doc, overwritten_doc, new_json_value)

    def test_get_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, defaults)

        read_doc = json_document_manager.get_document(
            defaults.get("project"), defaults.get("collection"), created_doc.key
        )

        assert read_doc.key == created_doc.key
        assert read_doc.created_at == created_doc.created_at

    def test_delete_document(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:
        defaults = get_defaults()
        created_doc = self._create_doc(json_document_manager, defaults)
        json_document_manager.delete_document(
            defaults.get("project"), defaults.get("collection"), created_doc.key
        )
        try:
            json_document_manager.get_document(
                defaults.get("project"), defaults.get("collection"), created_doc.key
            )
            assert False
        except ValueError:
            assert True

    def test_update_document(
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

        doc = JsonDocument(key=str(uuid4()), json_value=json.dumps(original_dict))

        json_document_manager.create_document(
            defaults.get("project"), defaults.get("collection"), doc
        )

        doc.json_value = changes_dict

        updated_doc = json_document_manager.update_document(
            defaults.get("project"), defaults.get("collection"), doc
        )

        self._assert_updated_doc(doc, updated_doc, desired_dict)

        read_doc = json_document_manager.get_document(
            defaults.get("project"), defaults.get("collection"), updated_doc.key
        )

        self._assert_updated_doc(doc, read_doc, desired_dict)

    def test_get_collection(
        self, json_document_manager: PostgresJsonDocumentManager
    ) -> None:

        project_id = "test_get_collection"
        collection_id = "test_get_collectio1"

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
            doc = JsonDocument(key=str(uuid4()), json_value=json.dumps(json_dict))
            json_document_manager.create_document(project_id, collection_id, doc)

        docs = json_document_manager.get_collection(project_id, collection_id)
        assert len(docs) == len(data)

        json_path_filter = 'json_value @> \'{"title": "Hello!"}\''
        docs = json_document_manager.get_collection(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            assert doc.json_value.get("title") == "Hello!"

        json_path_filter = 'json_value @> \'{"title": "Hello!"}\''
        docs = json_document_manager.get_collection(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            assert doc.json_value.get("title") == "Hello!"

        json_path_filter = 'json_value @> \'{"title": "Hello!"}\''
        docs = json_document_manager.get_collection(
            project_id, collection_id, json_path_filter
        )
        for doc in docs:
            assert doc.json_value.get("title") == "Hello!"

    def _create_doc(
        self, jdm: PostgresJsonDocumentManager, defaults: dict
    ) -> JsonDocument:
        doc = JsonDocument(
            key=defaults.get("key"), json_value=defaults.get("json_value")
        )
        return jdm.create_document(
            defaults.get("project"), defaults.get("collection"), doc
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
        docs = json_document_manager.get_documents(
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
