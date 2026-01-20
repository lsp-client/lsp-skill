import typer
from lsap.schema.doc import DocRequest, DocResponse

from lsp_cli.utils.model import Nullable
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("doc")
@cli_syncify
async def get_doc(
    locate: op.LocateOpt,
    project: op.ProjectOpt = None,
) -> None:
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/doc",
            Nullable[DocResponse],
            json=DocRequest(locate=locate_obj),
        ):
            case Nullable(root=DocResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No documentation found.")
