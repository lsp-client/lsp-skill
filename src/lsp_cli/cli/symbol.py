import cyclopts
from lsap.schema.symbol import SymbolRequest, SymbolResponse
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(
    name="symbol",
    help="Get detailed symbol information at a specific location.",
)


@app.default
async def symbol(
    file_path: op.FilePathOpt,
    /,
    *,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Get detailed symbol information.
    """

    locate = create_locate(file_path, scope, find)

    async with connect_server(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/symbol",
            RootModel[SymbolResponse | None],
            json=SymbolRequest(locate=locate),
        ):
            case RootModel(root=SymbolResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("Warning: No symbol information found")
