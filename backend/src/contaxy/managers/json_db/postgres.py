import json
from datetime import datetime
from typing import Dict, List, Optional

import json_merge_patch
from loguru import logger
from sqlalchemy import Column, DateTime, MetaData, Table, func, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Row
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound,
    OperationalError,
    ProgrammingError,
)
from sqlalchemy.future import Engine, create_engine

from contaxy.operations import JsonDocumentOperations
from contaxy.schema.exceptions import (
    ClientValueError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    ServerBaseError,
)
from contaxy.schema.json_db import JsonDocument
from contaxy.utils.postgres_utils import create_schema
from contaxy.utils.state_utils import GlobalState, RequestState


class PostgresJsonDocumentManager(JsonDocumentOperations):
    def __init__(
        self,
        global_state: GlobalState,
        request_state: RequestState,
    ):
        """Initializes the Postgres Json Document Manager.

        Args:
            global_state: The global state of the app instance.
            request_state: The state for the current request.
        """
        self.global_state = global_state
        self.request_state = request_state
        self._engine = self._create_db_engine()
        self._metadata = MetaData()

    def create_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
        upsert: bool = True,
    ) -> JsonDocument:
        """Creates a json document for a given key.

        An upsert strategy is used, i.e. if a document already exists for the given key it will be overwritten. The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created.

        Args:
            project_id (str): Project Id, i.e. DB schema.
            collection_id (str): Json document collection Id, i.e. DB table.
            key (str): Json Document Id, i.e. DB row key.
            json_document (Dict): The actual Json document.
            upsert (bool): Indicates, wheter upsert strategy is used.

        Raises:
            ClientValueError: If the given json_document does not contain valid json.
            ResourceAlreadyExistsError: If a document already exists for the given key and `upsert` is False.

        Returns:
            JsonDocument: The created Json document.
        """
        try:
            json_dict = json.loads(json_document)
        except json.decoder.JSONDecodeError:
            raise ClientValueError("Invalid Json provided")

        table = self._get_collection_table(project_id, collection_id)

        insert_data = {"key": key, "json_value": json_dict}
        insert_data = self._add_metadata_for_insert(insert_data)
        upsert_data = self._add_metadata_for_update(insert_data)

        stmt = postgresql.insert(table).values(**insert_data)
        if upsert:
            stmt = stmt.on_conflict_do_update(index_elements=["key"], set_=upsert_data)

        with self._engine.begin() as conn:
            try:
                result = conn.execute(stmt)
                if result.rowcount == 0:
                    raise ServerBaseError(
                        f"Json Document creation for key {key} for an unknown reason"
                    )
                conn.commit()
            except IntegrityError:
                raise ResourceAlreadyExistsError(
                    f"A Json document for key {key} already exists."
                )

        return self.get_json_document(project_id, collection_id, key)

    def get_json_document(
        self, project_id: str, collection_id: str, key: str
    ) -> JsonDocument:
        """Get a Json document by key.

        The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created.

        Args:
            project_id (str): Project Id, i.e. DB schema.
            collection_id (str): Json document collection Id, i.e. DB table.
            key (str): Json Document Id, i.e. DB row key.
            json_document (Dict): The actual Json document.

        Raises:
            ResourceNotFoundError: If no JSON document is found with the given `key`.

        Returns:
            JsonDocument: The requested Json document.
        """
        table = self._get_collection_table(project_id, collection_id)
        select_statement = table.select().where(table.c.key == key)
        with self._engine.begin() as conn:
            result = conn.execute(select_statement)
            try:
                row = result.one()
            except NoResultFound:
                raise ResourceNotFoundError(f"No document with key {key} found")
        return self._map_db_row_to_document_model(row)

    def update_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
    ) -> JsonDocument:
        """Updates a Json document via Json Merge Patch strategy.

        The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created.

        Args:
            project_id (str): Project Id, i.e. DB schema.
            collection_id (str): Json document collection Id, i.e. DB table.
            key (str): Json Document Id, i.e. DB row key.
            json_document (Dict): The actual Json document.

        Raises:
            ResourceNotFoundError: If no JSON document is found with the given `key`.
            ServerBaseError: Document not updatded for an unknown reason.

        Returns:
            JsonDocument: The updated document.
        """
        table = self._get_collection_table(project_id, collection_id)

        update_data = self._add_metadata_for_update({})

        select_statement = table.select().with_for_update().where(table.c.key == key)

        with self._engine.begin() as conn:
            result = conn.execute(select_statement)

            if result.rowcount == 0:
                raise ResourceNotFoundError(
                    f"Update failed - No document with key {key} found"
                )
            row = result.one()

            update_data["json_value"] = json_merge_patch.merge(
                # TODO: Allow passing dict directly to avoid converting a dict to json and right back to a dict here
                row["json_value"],
                json.loads(json_document),
            )

            # The json_value needs to be a dict otherwise the string gets escaped
            update_statement = (
                table.update().where(table.c.key == key).values(**update_data)
            )

            result = conn.execute(update_statement)

            conn.commit()

        return self.get_json_document(project_id, collection_id, key)

    def delete_json_document(
        self, project_id: str, collection_id: str, key: str
    ) -> None:
        """Delete a Json document by key.

        The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created.

        Args:
            project_id (str): Project Id, i.e. DB schema.
            collection_id (str): Json document collection Id, i.e. DB table.
            key (str): Json Document Id, i.e. DB row key.
            json_document (Dict): The actual Json document.

        Raises:
            ResourceNotFoundError: If no JSON document is found with the given `key`.
            ServerBaseError: Document not deleted for an unknown reason.
        """

        table = self._get_collection_table(project_id, collection_id)
        delete_statement = table.delete().where(table.c.key == key)
        with self._engine.begin() as conn:
            result = conn.execute(delete_statement)
            if result.rowcount == 0:
                # This will raise a ResourceNotFoundError if doc not exists
                self.get_json_document(project_id, collection_id, key)
                raise ServerBaseError(
                    f"Document {key} could not be deleted (project_id: {project_id}, collection_id {collection_id})"
                )
            conn.commit()

    def delete_documents(
        self, project_id: str, collection_id: str, keys: List[str]
    ) -> int:
        """Delete Json documents by key.

        The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created.

        Args:
            project_id (str): Project Id, i.e. DB schema.
            collection_id (str): Json document collection Id, i.e. DB table.
            keys (List[str]): Json Document Ids, i.e. DB row keys.
            json_document (Dict): The actual Json document.

        """
        table = self._get_collection_table(project_id, collection_id)
        delete_statement = table.delete().where(table.c.key.in_(keys))
        with self._engine.begin() as conn:
            result = conn.execute(delete_statement)
            conn.commit()

        return result.rowcount

    def list_json_documents(
        self,
        project_id: str,
        collection_id: str,
        filter: Optional[str] = None,
        keys: Optional[List[str]] = None,
    ) -> List[JsonDocument]:
        """List all existing Json documents and optionally filter via Json Path syntax.

            The project is equivalent to the DB schema and the collection to a DB table inside the respective DB schema. Schema as well as table will be lazily created.

        Args:
            project_id (str): Project Id, i.e. DB schema.
            collection_id (str): Json document collection Id, i.e. DB table.
            filter (Optional[str], optional): Json Path filter. Defaults to None.
            keys (Optional[List[str]], optional): Json Document Ids, i.e. DB row keys. Defaults to None.

        Raises:
            ClientValueError: If filter is provided and does not contain a valid Json Path filter.

        Returns:
            List[JsonDocument]: List of Json documents.
        """

        table = self._get_collection_table(project_id, collection_id)
        sql_statement = table.select()
        if filter:
            sql_statement = sql_statement.where(
                func.jsonb_path_exists(table.c.json_value, filter),
            )

        if keys:
            sql_statement = sql_statement.where(table.c.key.in_(keys))

        with self._engine.begin() as conn:
            try:
                result = conn.execute(sql_statement)
            except ProgrammingError:
                raise ClientValueError("Please provide a valid Json Path filter.")

            rows = result.fetchall()
        return self._map_db_rows_to_document_models(rows)

    def delete_json_collections(
        self,
        project_id: str,
    ) -> None:
        """Deletes all JSON collections for a project.

        Args:
            project_id: Project ID associated with the collections.
        """
        # TODO: Check if further error handling is needed
        with self._engine.begin() as conn:
            stmt = text(
                f'DROP SCHEMA IF EXISTS "{self._get_schema_name(project_id)}" cascade'
            )
            conn.execute(stmt)
            conn.commit()

    def delete_json_collection(
        self,
        project_id: str,
        collection_id: str,
    ) -> None:
        """Delete a JSON collection.

        Args:
            project_id (str): Project ID associated with the collection.
            collection_id (str): The collection to be deleted.
        """

        stmt = text(
            f'DROP TABLE IF EXISTS "{self._get_schema_name(project_id)}"."{collection_id}" cascade'
        )
        with self._engine.begin() as conn:
            conn.execute(stmt)
            conn.commit()

    def _add_metadata_for_insert(self, data: dict) -> dict:
        # TODO: Copy required?
        insert_data = data.copy()
        # TODO: Finalize
        insert_data["created_at"] = datetime.utcnow()
        # Added the updated_at column to facilitate the document deletion based on timestamp.
        insert_data["updated_at"] = insert_data["created_at"]
        # data["created_by"] =
        return insert_data

    def _add_metadata_for_update(self, data: dict) -> dict:
        update_data = data.copy()
        # TODO: Finalize
        update_data["updated_at"] = datetime.utcnow()
        # data["updated_by"] =
        return update_data

    def _map_db_rows_to_document_models(self, rows: List[Row]) -> List[JsonDocument]:
        docs = []
        for row in rows:
            docs.append(self._map_db_row_to_document_model(row))
        return docs

    def _map_db_row_to_document_model(self, row: Row) -> JsonDocument:
        data: Dict = {}
        for column_name, value in row._mapping.items():
            if column_name == "json_value":
                value = json.dumps(value)
            data.update({column_name: value})
        return JsonDocument(**data)

    def _get_collection_table(self, project_id: str, collection_id: str) -> Table:
        # TODO: Decide on actual column datatypes
        collection = Table(
            collection_id,
            self._metadata,
            Column("key", postgresql.VARCHAR, primary_key=True),
            Column("json_value", postgresql.JSONB),
            Column("created_at", DateTime),
            Column("created_by", postgresql.VARCHAR),
            Column("updated_at", DateTime),
            Column("updated_by", postgresql.VARCHAR),
            schema=self._get_schema_name(project_id),
            keep_existing=True,  # TODO: Depends on how we handle schema modifications
        )

        try:
            collection.create(self._engine, checkfirst=True)
        except ProgrammingError:
            create_schema(self._engine, self._get_schema_name(project_id))
            collection.create(self._engine, checkfirst=True)

        return collection

    def _create_db_engine(self) -> Engine:
        state_namespace = self.global_state[PostgresJsonDocumentManager]
        if not state_namespace.db_engine:
            url = self.global_state.settings.POSTGRES_CONNECTION_URI
            engine = create_engine(url, future=True)
            # Test the DB connection and set to global state if succesful
            try:
                with engine.begin():
                    state_namespace.db_engine = engine
            except OperationalError as ex:
                logger.exception("POSTGRES DB Problem")
                raise ServerBaseError(
                    "Postgres DB connection failed. Validate connection URI."
                ) from ex
            logger.info("Postgres DB Engine created")
        return state_namespace.db_engine

    def _get_schema_name(self, project_id: str) -> str:
        prefix = self.global_state.settings.SYSTEM_NAMESPACE
        return project_id if not prefix else f"{prefix}_{project_id}"
