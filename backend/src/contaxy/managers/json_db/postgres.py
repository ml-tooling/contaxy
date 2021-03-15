import datetime
import json
from typing import List, Optional

from sqlalchemy import Column, DateTime, Table, func, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Row
from sqlalchemy.exc import NoResultFound, ProgrammingError
from sqlalchemy.future import Engine
from sqlalchemy.schema import DDL, CreateSchema

from contaxy.operations import JsonDocumentOperations
from contaxy.schema.json_db import JsonDocument
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

    def create_json_document(
        self,
        project_id: str,
        collection_id: str,
        key: str,
        json_document: str,
    ) -> JsonDocument:
        """Upsert."""

        table = self._get_collection_table(project_id, collection_id)

        insert_data = self._add_metadata_for_insert(
            json_document.dict(exclude_none=True)
        )
        upsert_data = self._add_metadata_for_update(insert_data)

        upsert_statement = (
            postgresql.insert(table)
            .values(**insert_data)
            .on_conflict_do_update(index_elements=["key"], set_=upsert_data)
        )

        with self._engine.begin() as conn:
            result = conn.execute(upsert_statement)
            if result.rowcount == 0:
                raise Exception("Upsert failed")
            conn.commit()

        return self.get_document(project_id, collection_id, json_document.key)

    def get_document(
        self, project_id: str, collection_id: str, key: str
    ) -> JsonDocument:
        table = self._get_collection_table(project_id, collection_id)
        select_statement = table.select().where(table.c.key == key)
        with self._engine.begin() as conn:
            result = conn.execute(select_statement)
            try:
                row = result.one()
            except NoResultFound:
                raise ValueError(f"No document with key {key} found")
        return self._map_db_row_to_document_model(row)

    def get_documents(
        self, project_id: str, collection_id: str, keys: List[str]
    ) -> List[JsonDocument]:
        if not keys:
            raise ValueError("At least one key must be provided")

        table = self._get_collection_table(project_id, collection_id)
        select_statement = table.select().where(table.c.key.in_(keys))
        with self._engine.begin() as conn:
            result = conn.execute(select_statement)
            rows = result.fetchall()
        return self._map_db_rows_to_document_models(rows)

    def update_document(
        self, project_id: str, collection_id: str, document: JsonDocument
    ) -> JsonDocument:
        """Updates the document via Json Merge Patch strategy and returns the updated document."""
        table = self._get_collection_table(project_id, collection_id)
        json_value = document.json_value
        if isinstance(json_value, dict):
            json_value = json.dumps(document.json_value)

        update_data = self._add_metadata_for_update({})

        sql_statement = (
            table.update()
            .where(table.c.key == document.key)
            .values(
                json_value=func.jsonb_merge_patch(table.c.json_value, json_value),
                **update_data,
            )
        )

        with self._engine.begin() as conn:
            conn.execute(sql_statement)
            conn.commit()

        return self.get_document(project_id, collection_id, document.key)

    def delete_document(self, project_id: str, collection_id: str, key: str) -> None:
        table = self._get_collection_table(project_id, collection_id)
        delete_statement = table.delete().where(table.c.key == key)
        with self._engine.begin() as conn:
            result = conn.execute(delete_statement)
            if result.rowcount != 1:
                # TODO: Use specific excp
                raise Exception(
                    f"Document {key} could not be deleted (project_id: {project_id}, collection_id {collection_id})"
                )
            conn.commit()

    def delete_documents(
        self, project_id: str, collection_id: str, keys: List[str]
    ) -> int:
        table = self._get_collection_table(project_id, collection_id)
        delete_statement = table.delete().where(table.c.key.in_(keys))
        with self._engine.begin() as conn:
            result = conn.execute(delete_statement)
            # TODO raise meaningful error
            conn.commit()
        return result.rowcount

    def get_collection(
        self, project_id: str, collection_id: str, filter: Optional[str] = None
    ) -> List[JsonDocument]:
        # TODO: Evaluate JsonPath, incl indices
        # table = self._get_collection_table(project_id, collection_id)

        # select_statement = table.select()

        # for filter_str in filters:
        #     select_statement = select_statement.where(
        #         table.c.json_value.contains(filter_str)
        #     )
        with self._engine.begin() as conn:

            stmt = f'select * from "{collection_id}".{project_id}'
            if filter:
                stmt = f"{stmt} {filter}"

            result = conn.execute(text(stmt))
            rows = result.fetchall()
        return self._map_db_rows_to_document_models(rows)

    def _add_metadata_for_insert(self, data: dict) -> dict:
        insert_data = data.copy()
        # TODO: Finalize
        insert_data["created_at"] = datetime.datetime.utcnow()
        # data["created_by"] =
        return insert_data

    def _add_metadata_for_update(self, data: dict) -> dict:
        update_data = data.copy()
        # TODO: Finalize
        update_data["updated_at"] = datetime.datetime.utcnow()
        # data["updated_by"] =
        return update_data

    def _map_db_rows_to_document_models(self, rows: List[Row]) -> List[JsonDocument]:
        docs = []
        for row in rows:
            docs.append(self._map_db_row_to_document_model(row))
        return docs

    def _map_db_row_to_document_model(self, row: Row) -> JsonDocument:
        data = {}
        for column_name, value in row._mapping.items():
            if isinstance(value, dict):
                data.update({column_name: json.dumps(value)})
                continue
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
            schema=project_id,  # TODO: Check if sufficient if we set on metadata object
            keep_existing=True,  # TODO: Depends on how we handle schema modifications
        )

        try:
            collection.create(self._engine, checkfirst=True)
        except ProgrammingError as err:
            if err.code != "f405":
                raise err
            self._create_schema(project_id)
            collection.create(self._engine, checkfirst=True)

        return collection

    def _create_schema(self, project_id: str) -> None:

        with self._engine.begin() as conn:
            stmt = CreateSchema(project_id)
            try:
                conn.execute(stmt)
                conn.commit()
                print(f"Postgres Schema {project_id} created")
            except ProgrammingError:
                # This should only happen if the schema exists already
                pass


def create_jsonb_merge_patch_func(engine: Engine) -> None:

    func = DDL(
        "create or replace function jsonb_merge_patch(v_basedoc jsonb, v_patch jsonb) "
        "returns jsonb as $$ "
        "with recursive patchexpand as("
        "select '{}'::text[] as jpath, v_patch as jobj, jsonb_typeof(v_patch) as jtype, 0 as lvl "
        "union all "
        "select p.jpath||o.key as jpath, p.jobj->o.key as jobj, jsonb_typeof(p.jobj->o.key) as jtype, p.lvl + 1 as lvl "
        "from patchexpand p "
        "cross join lateral jsonb_each(case when p.jtype = 'object' then p.jobj else '{}'::jsonb end) as o(key, value) "
        "), pathnum as ( "
        "select *, row_number() over (order by lvl, jpath) as rn "
        "from patchexpand "
        "), apply as ("
        "select case "
        "when jsonb_typeof(v_basedoc) = 'object' then v_basedoc "
        "else '{}'::jsonb "
        "end as basedoc, "
        "p.rn "
        "from pathnum p "
        "where p.rn = 1 "
        "union all "
        "select case "
        "when p.jtype = 'object' then a.basedoc "
        "when p.jtype = 'null' then a.basedoc #- p.jpath "
        "else jsonb_set(a.basedoc, p.jpath, p.jobj) "
        "end as basedoc, "
        "p.rn "
        "from apply a "
        "join pathnum p "
        "on p.rn = a.rn + 1 "
        ") "
        "select case "
        "when jsonb_typeof(v_patch) != 'object' then v_patch "
        "else basedoc "
        "end "
        "from apply "
        "order by rn desc "
        "limit 1; "
        "$$ "
        "language sql;"
    )

    with engine.begin() as conn:
        conn.execute(func)
        conn.commit()
