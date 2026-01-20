from typing import Annotated

import cyclopts
from lsap.schema.locate import LocateRequest, LocateResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .shared import create_locate, managed_client

app = cyclopts.App(
    name="locate",
    help="Locate a position or range in the codebase using a string syntax.",
)


@app.default
async def locate(
    locate_str: Annotated[str, cyclopts.Parameter(help="The locate string to parse.")],
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Locate a position or range in the codebase using a string syntax.

    Syntax: `<file_path>[:<scope>][@<find>]`

    Scope formats:
    - `<line>` - Single line number (e.g., `42`)
    - `<start>,<end>` - Line range with comma (e.g., `10,20`)
    - `<start>-<end>` - Line range with dash (e.g., `10-20`)
    - `<symbol_path>` - Symbol path with dots (e.g., `MyClass.my_method`)

    Examples:
    - `foo.py@self.<|>`
    - `foo.py:42@return <|>result`
    - `foo.py:10,20@if <|>condition`
    - `foo.py:MyClass.my_method@self.<|>`
    - `foo.py:MyClass`
    """
    main_callback(opts.debug)
    locate_obj = create_locate(locate_str)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/locate",
            Nullable[LocateResponse],
            json=LocateRequest(locate=locate_obj),
        ):
            case Nullable(root=LocateResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No location found.")
