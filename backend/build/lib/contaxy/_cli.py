"""Command line interface."""

from pathlib import Path

import typer
from loguru import logger

cli = typer.Typer()


@cli.command()
def install_contaxy() -> None:
    from contaxy.managers.components import install_components

    install_components()


@cli.command()
def export_openapi_specs(output_path: Path) -> None:
    import json

    from contaxy.api import app

    # write openapi.json spec to file
    with open(output_path, "w") as outfile:
        json.dump(app.openapi(), outfile)


@cli.command()
def start_dev_server(host: str = "0.0.0.0", port: int = 8082) -> None:
    import sys

    import uvicorn

    logger.add(
        sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
    )

    typer.echo("Starting Dev Server.")

    # TODO: Run with: Run with: PYTHONASYNCIODEBUG=1
    uvicorn.run("contaxy.api:app", host=host, port=port, log_level="info", reload=True)


if __name__ == "__main__":
    cli()
