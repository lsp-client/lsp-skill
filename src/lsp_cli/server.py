from pathlib import Path
from typing import Annotated

import cyclopts

from lsp_cli.cli import options as op
from lsp_cli.cli.main import main_callback
from lsp_cli.manager.manager import connect_manager
from lsp_cli.manager.models import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    DeleteClientResponse,
    ManagedClientInfo,
    ManagedClientInfoList,
)
from lsp_cli.utils.model import Nullable

app = cyclopts.App(
    name="server",
    help="Manage background LSP server processes.",
)


@app.default
async def default(opts: op.GlobalOpts = op.GlobalOpts()) -> None:
    """Manage LSP servers."""
    main_callback(opts.debug)
    await list_servers(opts)


@app.command(name="list")
async def list_servers(opts: op.GlobalOpts = op.GlobalOpts()) -> None:
    """List all currently running and managed LSP servers."""
    main_callback(opts.debug)
    async with connect_manager() as client:
        if resp := await client.get("/list", ManagedClientInfoList):
            print(ManagedClientInfo.format(resp.root))
        else:
            print("No servers running.")


@app.command(name="start")
async def start_server(
    path: Annotated[
        Path,
        cyclopts.Parameter(
            help="Path to a code file or project directory to start the LSP server for."
        ),
    ],
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """Start a background LSP server for the project containing the specified path."""
    main_callback(opts.debug)
    async with connect_manager() as client:
        if resp := await client.post(
            "/create",
            CreateClientResponse,
            json=CreateClientRequest(path=path.resolve(), project_path=project),
        ):
            print(f"Success: Started server for {path.resolve()}")
            print(ManagedClientInfo.format([resp.info]))


@app.command(name="stop")
async def stop_server(
    path: Annotated[
        Path,
        cyclopts.Parameter(
            help="Path to a code file or project directory to stop the LSP server for."
        ),
    ],
    opts: op.GlobalOpts = op.GlobalOpts(),
) -> None:
    """Stop the background LSP server for the project containing the specified path."""
    main_callback(opts.debug)
    path = path.resolve()

    async with connect_manager() as client:
        match await client.delete(
            "/delete",
            Nullable[DeleteClientResponse],
            json=DeleteClientRequest(path=path),
        ):
            case Nullable(root=DeleteClientResponse(info=resp_info)):
                print(f"Success: Stopped server for {resp_info.project_path}")
            case Nullable(root=None):
                print(f"Warning: No server running for {path}")


if __name__ == "__main__":
    app()
