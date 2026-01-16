from pathlib import Path
from typing import Annotated

import typer

from lsp_cli.manager import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    DeleteClientResponse,
    ManagedClientInfo,
    ManagedClientInfoList,
    connect_manager,
)
from lsp_cli.utils.http import HttpClient

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


def get_manager_client() -> HttpClient:
    return connect_manager()


@app.command("list")
def list_servers() -> None:
    """List all currently running and managed LSP servers."""
    with get_manager_client() as client:
        resp = client.get("/list", ManagedClientInfoList)
        servers = resp.root if resp else []
        if not servers:
            print("No servers running.")
            return
        print(ManagedClientInfo.format(servers))


@app.command("start")
def start_server(
    path: Path = typer.Argument(
        None,
        help="Path to a code file or project directory to start the LSP server for.",
    ),
    project: ProjectOpt = None,
) -> None:
    """Start a background LSP server for the project containing the specified path."""
    if path is None:
        path = Path.cwd()

    if not path.is_absolute():
        path = path.absolute()

    with get_manager_client() as client:
        resp = client.post(
            "/create",
            CreateClientResponse,
            json=CreateClientRequest(path=path, project_path=project),
        )
        assert resp is not None
        info = resp.info
        print(f"Success: Started server for {path}")
        print(ManagedClientInfo.format(info))


@app.command("stop")
def stop_server(
    path: Path = typer.Argument(
        None,
        help="Path to a code file or project directory to stop the LSP server for.",
    ),
    project: ProjectOpt = None,
) -> None:
    """Stop the background LSP server for the project containing the specified path."""
    if path is None:
        path = Path.cwd()

    if not path.is_absolute():
        path = path.absolute()

    with get_manager_client() as client:
        client.delete(
            "/delete",
            DeleteClientResponse,
            json=DeleteClientRequest(path=path, project_path=project),
        )
        print(f"Success: Stopped server for {path}")


if __name__ == "__main__":
    app()
