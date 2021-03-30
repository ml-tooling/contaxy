from loguru import logger
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.future import Engine
from sqlalchemy.schema import CreateSchema


def create_schema(engine: Engine, schema_name: str) -> None:
    with engine.begin() as conn:
        stmt = CreateSchema(schema_name)
        try:
            conn.execute(stmt)
            conn.commit()
            # logger.debug(f"Postgres DB Schema {schema_name} created")
        except ProgrammingError:
            logger.debug(
                f"Postgres DB Schema {schema_name} not created. This because it already exists."
            )
