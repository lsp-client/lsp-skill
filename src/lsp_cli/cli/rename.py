from pathlib import Path
from typing import Annotated

import cyclopts
from lsap.schema.rename import (
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenamePreviewRequest,
    RenamePreviewResponse,
)
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(name="rename", help="Rename a symbol at a specific location.")


@app.command
async def preview(
    file_path: op.FilePathOpt,
    new_name: Annotated[str, cyclopts.Parameter(help="The new name for the symbol.")],
    /,
    *,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Preview the effects of renaming a symbol.
    """

    locate = create_locate(file_path, scope, find)

    async with connect_server(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/rename/preview",
            RootModel[RenamePreviewResponse | None],
            json=RenamePreviewRequest(locate=locate, new_name=new_name),
        ):
            case RootModel(root=RenamePreviewResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("Warning: No rename possibilities found at the location")


@app.command
async def execute(
    rename_id: Annotated[
        str, cyclopts.Parameter(help="Rename ID from a previous preview.")
    ],
    /,
    *,
    exclude: Annotated[
        list[str] | None,
        cyclopts.Parameter(
            name="--exclude",
            help="File paths or glob patterns to exclude from the rename operation. Can be specified multiple times.",
        ),
    ] = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Execute a rename operation using the ID from a previous preview.
    """

    # HACK convert glob to absolute path strings
    exclude = [Path(glob).absolute().as_posix() for glob in (exclude or [])]

    async with connect_server(project or Path.cwd()) as client:
        match await client.post(
            "/capability/rename/execute",
            RootModel[RenameExecuteResponse | None],
            json=RenameExecuteRequest(
                rename_id=rename_id,
                exclude_files=exclude,
            ),
        ):
            case RootModel(root=RenameExecuteResponse() as resp):
                print(resp.format())
            case _:
                raise RuntimeError("Failed to execute rename")
