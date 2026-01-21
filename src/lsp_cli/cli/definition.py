from typing import Annotated, Literal

import cyclopts
from lsap.schema.definition import DefinitionRequest, DefinitionResponse
from lsap.schema.rename import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(
    name="definition",
    help="Find the definition, declaration, or type definition of a symbol.",
)


@app.default
async def definition(
    file_path: op.FilePathOpt,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    mode: Annotated[
        Literal["definition", "declaration", "type_definition"],
        cyclopts.Parameter(
            name=["--mode", "-m"],
            help="Mode to locate symbol: `definition` (default), `declaration`, or `type_definition`.",
            show_default=True,
        ),
    ] = "definition",
    project: op.ProjectOpt = None,
) -> None:
    """
    Find the definition (default), declaration (--mode declaration), or type definition (--mode type_definition) of a symbol.
    """

    locate = create_locate(file_path, scope, find)

    async with connect_server(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/definition",
            RootModel[DefinitionResponse | None],
            json=DefinitionRequest(locate=locate, mode=mode),
        ):
            case RootModel(root=DefinitionResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("No definition found.")
