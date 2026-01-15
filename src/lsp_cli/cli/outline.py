from pathlib import Path
from typing import Annotated

import typer
from lsap.schema.models import SymbolKind
from lsap.schema.outline import OutlineRequest, OutlineResponse

from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import managed_client

app = typer.Typer()


@app.command("outline")
@cli_syncify
async def get_outline(
    file_path: Annotated[
        Path,
        typer.Argument(help="Path to the file to get the symbol outline for."),
    ],
    all_symbols: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Show all symbols including local variables and parameters.",
        ),
    ] = False,
    project: op.ProjectOpt = None,
):
    """
    Get the hierarchical symbol outline (classes, functions, etc.) for a specific file.
    """
    if not file_path.is_absolute():
        file_path = file_path.absolute()

    async with managed_client(file_path, project_path=project) as client:
        resp_obj = await client.post(
            "/capability/outline",
            OutlineResponse,
            json=OutlineRequest(file_path=file_path),
        )

    if resp_obj and resp_obj.items:
        if not all_symbols:
            filtered_items = [
                item
                for item in resp_obj.items
                if item.kind
                in {
                    SymbolKind.Class,
                    SymbolKind.Function,
                    SymbolKind.Method,
                    SymbolKind.Interface,
                    SymbolKind.Enum,
                    SymbolKind.Module,
                    SymbolKind.Namespace,
                    SymbolKind.Struct,
                }
            ]
            resp_obj.items = filtered_items
            if not filtered_items:
                print("Warning: No symbols found (use --all to show local variables)")
                return
        print(resp_obj.format())
    else:
        print("Warning: No symbols found")
