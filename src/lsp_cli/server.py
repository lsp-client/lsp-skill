from pathlib import Path
from typing import Annotated

import typer

from lsp_cli.manager.manager import connect_manager
from lsp_cli.manager.models import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    DeleteClientResponse,
    ManagedClientInfo,
    ManagedClientInfoList,
)
from lsp_cli.utils.sync import cli_syncify

app = typer.Typer(
    name="server",
    help="Manage background LSP server processes.",
    add_completion=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 1000,
        "terminal_width": 1000,
    },
)


ProjectOpt = Annotated[
    Path | None,
    typer.Option(
        "--project",
        help="Path to the project. If specified, start a server in this directory.",
    ),
]


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """Manage LSP servers."""
    if ctx.invoked_subcommand is None:
        list_servers()


@app.command("list")
@cli_syncify
async def list_servers() -> None:
    """List all currently running and managed LSP servers."""
    async with connect_manager() as client:
        if resp := await client.get("/list", ManagedClientInfoList):
            print(ManagedClientInfo.format(resp.root))
        else:
            print("No servers running.")


@app.command("start")
@cli_syncify
async def start_server(
    path: Path = typer.Argument(
        help="Path to a code file or project directory to start the LSP server for.",
    ),
    project: ProjectOpt = None,
) -> None:
    """Start a background LSP server for the project containing the specified path."""

    async with connect_manager() as client:
        if resp := await client.post(
            "/create",
            CreateClientResponse,
            json=CreateClientRequest(path=path.absolute(), project_path=project),
        ):
            print(f"Success: Started server for {path}")
            print(ManagedClientInfo.format([resp.info]))


@app.command("stop")
@cli_syncify
async def stop_server(
    path: Path = typer.Argument(
        help="Path to a code file or project directory to stop the LSP server for.",
    ),
    project: ProjectOpt = None,
) -> None:
    """Stop the background LSP server for the project containing the specified path."""

    async with connect_manager() as client:
        if resp := await client.delete(
            "/delete",
            DeleteClientResponse,
            json=DeleteClientRequest(path=path.absolute(), project_path=project),
        ):
            print(f"Success: Stopped server for {resp.info.project_path}")
        else:
            print(f"Warning: No server running for {project}")


if __name__ == "__main__":
    app()
