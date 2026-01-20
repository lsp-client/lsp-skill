from typing import Annotated

import typer
from lsap.schema.locate import LocateRequest, LocateResponse

from lsp_cli.utils.model import Nullable
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("locate")
@cli_syncify
async def get_location(
    locate: Annotated[str, typer.Argument(help="The locate string to parse.")],
    project: op.ProjectOpt = None,
) -> None:
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/locate",
            Nullable[LocateResponse],
            json=LocateRequest(locate=locate_obj),
        ):
            case Nullable(root=LocateResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No location found.")
