import typer
from lsap.schema.doc import DocRequest, DocResponse

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
    """
    Get documentation and type information for a symbol at a specific location.
    """
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        resp_obj = await client.post(
            "/capability/hover", DocResponse, json=DocRequest(locate=locate_obj)
        )

    if resp_obj:
        print(resp_obj.format())
    else:
        print("Warning: No documentation found")
