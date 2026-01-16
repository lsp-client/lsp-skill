from pathlib import Path
from typing import Annotated

import typer
from lsap.schema.rename import (
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenamePreviewRequest,
    RenamePreviewResponse,
)

from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer(name="rename", help="Rename a symbol at a specific location.")


@app.command("preview")
@cli_syncify
async def rename_preview(
    new_name: Annotated[str, typer.Argument(help="The new name for the symbol.")],
    locate: op.LocateOpt,
    project: op.ProjectOpt = None,
) -> None:
    """
    Preview the effects of renaming a symbol at a specific location.
    """

    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        resp_obj = await client.post(
            "/capability/rename/preview",
            RenamePreviewResponse,
            json=RenamePreviewRequest(locate=locate_obj, new_name=new_name),
        )

        if resp_obj:
            print(resp_obj.format())
        else:
            print("Warning: No rename possibilities found at the location")


@app.command("execute")
@cli_syncify
async def rename_execute(
    rename_id: Annotated[
        str, typer.Argument(help="Rename ID from a previous preview.")
    ],
    exclude: Annotated[
        list[str] | None,
        typer.Option(
            "--exclude",
            help="File paths or glob patterns to exclude from the rename operation. Can be specified multiple times.",
        ),
    ] = None,
    workspace: op.WorkspaceOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Execute a rename operation using the ID from a previous preview.
    """
    if workspace is None:
        workspace = Path.cwd()

    if not workspace.is_absolute():
        workspace = workspace.absolute()

    # Normalize exclude paths and globs to absolute paths/globs
    normalized_exclude = []
    if exclude:
        cwd = Path.cwd()
        for p in exclude:
            p_obj = Path(p)
            if p_obj.is_absolute():
                normalized_exclude.append(p)
            else:
                normalized_exclude.append(str(cwd / p))

    async with managed_client(workspace, project_path=project) as client:
        resp_obj = await client.post(
            "/capability/rename/execute",
            RenameExecuteResponse,
            json=RenameExecuteRequest(
                rename_id=rename_id,
                exclude_files=normalized_exclude,
            ),
        )

        if resp_obj:
            print(resp_obj.format())
        else:
            raise RuntimeError("Failed to execute rename")
