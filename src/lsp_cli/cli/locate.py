from typing import Annotated

import typer
from lsap.schema.locate import LocateRequest, LocateResponse

from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("locate")
@cli_syncify
async def get_location(
    locate: Annotated[str, typer.Argument(help="The locate string to parse.")],
    check: bool = typer.Option(
        False,
        "--check",
        "-c",
        help="Verify if the target exists in the file and show its context.",
    ),
    project: op.ProjectOpt = None,
) -> None:
    """
    Locate a position or range in the codebase using a string syntax.
    """
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        resp_obj = await client.post(
            "/capability/locate", LocateResponse, json=LocateRequest(locate=locate_obj)
        )

    if resp_obj:
        print(resp_obj.format())
    elif check:
        raise RuntimeError(f"Target '{locate}' not found")
    else:
        print(locate_obj)
