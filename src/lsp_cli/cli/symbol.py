import cyclopts
from lsap.schema.symbol import SymbolRequest, SymbolResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .utils import connect_server, create_locate

app = cyclopts.App(
    name="symbol",
    help="Get detailed symbol information at a specific location.",
)


@app.default
async def symbol(
    file_path: op.FilePathOpt,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Get detailed symbol information.
    """
    main_callback(opts.debug)
    locate = create_locate(file_path, scope, find)

    async with connect_server(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/symbol",
            Nullable[SymbolResponse],
            json=SymbolRequest(locate=locate),
        ):
            case Nullable(root=SymbolResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("Warning: No symbol information found")
