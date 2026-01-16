import typer
from lsap.schema.symbol import SymbolRequest, SymbolResponse

from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("symbol")
@cli_syncify
async def get_symbol(
    locate: op.LocateOpt,
    project: op.ProjectOpt = None,
) -> None:
    """
    Get detailed symbol information at a specific location.
    """
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        resp_obj = await client.post(
            "/capability/symbol",
            SymbolResponse,
            json=SymbolRequest(locate=locate_obj),
        )

    if resp_obj:
        print(resp_obj.format())
    else:
        print("Warning: No symbol information found")
