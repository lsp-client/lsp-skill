from typing import Annotated, Literal

import typer
from lsap.schema.reference import ReferenceRequest, ReferenceResponse

from lsp_cli.settings import settings
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("reference")
@cli_syncify
async def get_reference(
    locate: op.LocateOpt,
    mode: Annotated[
        Literal["references", "implementations"],
        typer.Option(
            "--mode",
            "-m",
            help="Search mode (default: references).",
            hidden=True,
        ),
    ] = "references",
    impl: bool = typer.Option(False, "--impl", help="Find concrete implementations."),
    references: bool = typer.Option(False, "--ref", help="Find all usages."),
    context_lines: Annotated[
        int | None,
        typer.Option(
            "--context-lines",
            "-C",
            help="Number of lines of context to show around each match.",
        ),
    ] = None,
    max_items: op.MaxItemsOpt = None,
    start_index: op.StartIndexOpt = 0,
    pagination_id: op.PaginationIdOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Find references (default) or implementations (--impl) of a symbol.
    """
    if impl and references:
        raise ValueError("--impl and --ref are mutually exclusive")

    if impl:
        mode = "implementations"
    elif references:
        mode = "references"

    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        effective_context_lines = (
            context_lines
            if context_lines is not None
            else settings.default_context_lines
        )

        resp_obj = await client.post(
            "/capability/reference",
            ReferenceResponse,
            json=ReferenceRequest(
                locate=locate_obj,
                mode=mode,
                context_lines=effective_context_lines,
                max_items=max_items,
                start_index=start_index,
                pagination_id=pagination_id,
            ),
        )

    if resp_obj:
        print(resp_obj.format())
    else:
        print(f"Warning: No {mode} found")
