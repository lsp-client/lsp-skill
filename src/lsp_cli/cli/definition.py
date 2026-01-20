from typing import Annotated, Literal

import cyclopts
from lsap.schema.definition import DefinitionRequest, DefinitionResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .shared import create_locate, managed_client

app = cyclopts.App(
    name="definition",
    help="Find the definition, declaration, or type definition of a symbol.",
)


@app.default
async def definition(
    locate_opt: op.LocateOpt,
    opts: op.GlobalOpts = op.GlobalOpts(),
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
    main_callback(opts.debug)
    locate = create_locate(locate_opt)

    async with managed_client(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/definition",
            Nullable[DefinitionResponse],
            json=DefinitionRequest(locate=locate, mode=mode),
        ):
            case Nullable(root=DefinitionResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No definition found.")
