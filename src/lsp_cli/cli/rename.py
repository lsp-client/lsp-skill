from pathlib import Path
from typing import Annotated

import cyclopts
from lsap.schema.rename import (
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenamePreviewRequest,
    RenamePreviewResponse,
)

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .shared import create_locate, managed_client

app = cyclopts.App(name="rename", help="Rename a symbol at a specific location.")


@app.command
async def preview(
    locate: op.LocateOpt,
    new_name: Annotated[
        str,
        cyclopts.Parameter(
            name=["-n", "--new_name"], help="The new name for the symbol."
        ),
    ],
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Preview the effects of renaming a symbol at a specific location.
    """
    main_callback(opts.debug)
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/rename/preview",
            Nullable[RenamePreviewResponse],
            json=RenamePreviewRequest(locate=locate_obj, new_name=new_name),
        ):
            case Nullable(root=RenamePreviewResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("Warning: No rename possibilities found at the location")


@app.command
async def execute(
    rename_id: Annotated[
        str, cyclopts.Parameter(help="Rename ID from a previous preview.")
    ],
    opts: op.GlobalOpts = op.GlobalOpts(),
    exclude: Annotated[
        list[str] | None,
        cyclopts.Parameter(
            name="--exclude",
            help="File paths or glob patterns to exclude from the rename operation. Can be specified multiple times.",
        ),
    ] = None,
    workspace: op.WorkspaceOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Execute a rename operation using the ID from a previous preview.
    """
    main_callback(opts.debug)
    if workspace is None:
        workspace = Path.cwd()

    if not workspace.is_absolute():
        workspace = workspace.resolve()

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
        match await client.post(
            "/capability/rename/execute",
            Nullable[RenameExecuteResponse],
            json=RenameExecuteRequest(
                rename_id=rename_id,
                exclude_files=normalized_exclude,
            ),
        ):
            case Nullable(root=RenameExecuteResponse() as resp):
                print(resp.format())
            case _:
                raise RuntimeError("Failed to execute rename")
