import cyclopts
from lsap.schema.symbol import SymbolRequest, SymbolResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .shared import create_locate, managed_client

app = cyclopts.App(
    name="symbol",
    help="Get detailed symbol information at a specific location.",
)


@app.default
async def symbol(
    locate_opt: op.LocateOpt,
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Get detailed symbol information at a specific location.
    """
    main_callback(opts.debug)
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
