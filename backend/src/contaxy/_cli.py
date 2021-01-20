"""Command line interface."""

import typer

from contaxy import main

cli = typer.Typer()


@cli.command()
def hello(name: str) -> None:
    typer.echo(f"Hello {name}")


@cli.command()
def start_api_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    typer.echo("Starting API Server.")

    uvicorn.run(
        main.app, host=host, port=port, log_level="info"
    )  # cannot use reload=True anymore


if __name__ == "__main__":
    cli()
