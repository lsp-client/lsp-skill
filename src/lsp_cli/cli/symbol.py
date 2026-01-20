import typer
from lsap.schema.symbol import SymbolRequest, SymbolResponse

from lsp_cli.utils.model import Nullable
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import create_locate, managed_client

app = typer.Typer()


@app.command("symbol")
@cli_syncify
async def get_symbol(
    locate_opt: op.LocateOpt,
    project: op.ProjectOpt = None,
) -> None:
    """
    Get detailed symbol information at a specific location.
    """
    locate = create_locate(locate_opt)

    async with managed_client(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/symbol",
            Nullable[SymbolResponse],
            json=SymbolRequest(locate=locate),
        ):
            case Nullable(root=SymbolResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("Warning: No symbol information found")
