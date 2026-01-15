from typing import Annotated, Literal

import typer
from lsap.schema.definition import DefinitionRequest, DefinitionResponse

from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client


app = typer.Typer()


@app.command("definition")
@cli_syncify
async def get_definition(
    locate: op.LocateOpt,
    mode: Annotated[
        Literal["definition", "declaration", "type_definition"],
        typer.Option(
            "--mode",
            "-m",
            help="Search mode (default: definition).",
            hidden=True,
        ),
    ] = "definition",
    decl: bool = typer.Option(False, "--decl", help="Search for symbol declaration."),
    type_def: bool = typer.Option(False, "--type", help="Search for type definition."),
):
    """
    Find the definition (default), declaration (--decl), or type definition (--type) of a symbol.
    """
    if decl and type_def:
        raise ValueError("--decl and --type are mutually exclusive")

    if decl:
        mode = "declaration"
    elif type_def:
        mode = "type_definition"

    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path) as client:
        resp_obj = await client.post(
            "/capability/definition",
            DefinitionResponse,
            json=DefinitionRequest(
                locate=locate_obj,
                mode=mode,
            ),
        )

    if resp_obj:
        print(resp_obj.format())
    else:
        print(f"Warning: No {mode.replace('_', ' ')} found")
