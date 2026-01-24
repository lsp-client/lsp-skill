import cyclopts
from lsap.schema.outline import OutlineRequest, OutlineResponse
from pydantic import RootModel

from lsp_cli.cli.options import FilePathOpt
from lsp_cli.utils.locate import parse_symbol_scope

from . import options as op
from .utils import connect_server

app = cyclopts.App(
    name="outline",
    help="Get the hierarchical symbol outline for a specific file.",
)


@app.default
async def outline(
    file_path: FilePathOpt,
    /,
    *,
    symbol: op.SymbolOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Get the hierarchical symbol outline (classes, functions, etc.) for a specific file.

    If --symbol is provided, it must be a symbol path (e.g. MyClass or MyClass.my_method).
    """

    parsed_scope = parse_symbol_scope(symbol) if symbol else None

    async with connect_server(file_path, project_path=project) as client:
        match await client.post(
            "/capability/outline",
            RootModel[OutlineResponse | None],
            json=OutlineRequest(
                file_path=file_path.resolve(),
                scope=parsed_scope,
            ),
        ):
            case RootModel(root=OutlineResponse() as resp):
                print(resp.format())
            case _:
                print("Warning: No symbols found")
