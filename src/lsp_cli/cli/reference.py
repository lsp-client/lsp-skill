from typing import Annotated

import typer
from lsap.schema.reference import ReferenceRequest, ReferenceResponse

from lsp_cli.utils.model import Nullable
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("reference")
@cli_syncify
async def get_reference(
    locate: op.LocateOpt,
    impl: bool = typer.Option(False, "--impl", help="Find concrete implementations."),
    context_lines: Annotated[
        int,
        typer.Option(
            "--context-lines",
            "-C",
            help="Number of lines of context to show around each match.",
        ),
    ] = 2,
    max_items: op.MaxItemsOpt = None,
    start_index: op.StartIndexOpt = 0,
    pagination_id: op.PaginationIdOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    mode = "implementations" if impl else "references"

    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/reference",
            Nullable[ReferenceResponse],
            json=ReferenceRequest(
                locate=locate_obj,
                mode=mode,
                context_lines=context_lines,
                max_items=max_items,
                start_index=start_index,
                pagination_id=pagination_id,
            ),
        ):
            case Nullable(root=ReferenceResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print(f"Warning: No {mode} found")
