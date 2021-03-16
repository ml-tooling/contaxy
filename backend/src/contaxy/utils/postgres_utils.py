from sqlalchemy.exc import ProgrammingError
from sqlalchemy.future import Engine
from sqlalchemy.schema import DDL, CreateSchema


def create_schema(engine: Engine, schema_name: str) -> None:

    with engine.begin() as conn:
        stmt = CreateSchema(schema_name)
        try:
            conn.execute(stmt)
            conn.commit()
            print(f"Postgres Schema {schema_name} created")
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
