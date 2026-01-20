from typing import Annotated, Literal

import typer
from lsap.schema.definition import DefinitionRequest, DefinitionResponse

from lsp_cli.utils.model import Nullable
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("definition")
@cli_syncify
async def get_definition(
    locate_opt: op.LocateOpt,
    mode: Annotated[
        Literal["definition", "declaration", "type_definition"],
        typer.Option(
            "--mode",
            "-m",
            help="Mode to locate symbol: `definition` (default), `declaration`, or `type_definition`.",
            case_sensitive=False,
            show_default=True,
        ),
    ] = "definition",
    project: op.ProjectOpt = None,
) -> None:
    locate = create_locate(locate_opt)

    async with managed_client(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/definition",
            Nullable[DefinitionResponse],
            json=DefinitionRequest(locate=locate, mode=mode),
        ):
            case Nullable(root=DefinitionResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No definition found.")
