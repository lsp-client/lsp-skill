from pathlib import Path
from typing import Annotated

import cyclopts
from pydantic import RootModel

from lsp_cli.cli import options as op
from lsp_cli.manager.manager import connect_manager
from lsp_cli.manager.models import (
    CreateClientRequest,
    CreateClientResponse,
    DeleteClientRequest,
    ManagedClientInfo,
    ManagedClientInfoList,
)

app = cyclopts.App(
    name="server",
    help="Manage background LSP server processes.",
)


@app.default
async def default() -> None:
    """Manage LSP servers."""
    await list_servers()


@app.command(name="list")
async def list_servers() -> None:
    """List all currently running and managed LSP servers."""
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
    project: op.ProjectOpt = None,
) -> None:
    """Start a background LSP server for the project containing the specified path."""
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
        Path | None,
        cyclopts.Parameter(
            help="Path to a code file or project directory to stop the LSP server for."
        ),
    ] = None,
    all: Annotated[
        bool,
        cyclopts.Parameter(
            name=["--all", "-a"],
            help="Stop all running LSP servers.",
        ),
    ] = False,
) -> None:
    """Stop background LSP server(s)."""
    if not all and path is None:
        print("Error: Must provide a path or specify --all.")
        return

    async with connect_manager() as client:
        resp = await client.delete(
            "/delete",
            RootModel[list[ManagedClientInfo]],
            json=DeleteClientRequest(
                path=path.resolve() if path else None,
                all=all,
            ),
        )
        if stopped := resp.root:
            for info in stopped:
                print(f"Success: Stopped server for {info.project_path}")
        else:
            if all:
                print("No servers running.")
            else:
                print(f"Warning: No server running for {path}")


@app.command(name="shutdown")
async def shutdown_manager() -> None:
    """Shutdown the background LSP manager process."""

    async with connect_manager() as client:
        await client.post("/shutdown", RootModel[None])
        print("Success: Shutdown manager.")


if __name__ == "__main__":
    app()
