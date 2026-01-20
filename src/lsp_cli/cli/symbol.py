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
    file_path: op.FilePathOpt,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Get detailed symbol information.

    Scope formats:
    - `<line>` - Single line number (e.g., `42`).
    - `<start>,<end>` - Line range (e.g., `10,20`). Use 0 for end to mean till EOF (e.g., `10,0`).
    - `<symbol_path>` - Symbol path (e.g., `MyClass.my_method`).

    Find format:
    - Pattern to search for within the file or scope.
    - Supports markers like `<|>` to specify exact position.
    """
    main_callback(opts.debug)
    locate = create_locate(file_path, scope, find)

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
