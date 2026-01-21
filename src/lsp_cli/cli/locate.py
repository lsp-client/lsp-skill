from typing import Annotated

import cyclopts
from lsap.schema.locate import LocateRequest, LocateResponse
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(
    name="locate",
    help="Locate a position or range in the codebase using a string syntax.",
)


@app.default
async def locate(
    file_path: op.FilePathOpt,
    scope: Annotated[
        str | None,
        cyclopts.Parameter(
            name=["--scope", "-s"],
            help="""\
Narrow search to a symbol body or line range.

Formats:
  line
    Single line number (e.g., '42').
  start,end
    Line range (e.g., '10,20'). Use 0 for end to mean till EOF (e.g., '10,0').
  symbol.path
    Dot-separated symbol path (e.g., 'MyClass.my_method').""",
        ),
    ] = None,
    find: Annotated[
        str | None,
        cyclopts.Parameter(
            name=["--find"],
            help="""\
Text pattern with an optional position marker '<|>' for exact location.

If no marker is provided, the position defaults to the start of the match.

Marker Detection:
  Use '<|>' for single level, '<<|>>' for double level if '<|>' appears in source, etc.

Examples:
  * "self.<|>"
  * "return <|>result"
  * "x = <|> + y <<|>> z\"""",
        ),
    ] = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Locate a position or range in the codebase.
    """
    locate_obj = create_locate(file_path, scope, find)

    async with connect_server(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/locate",
            RootModel[LocateResponse | None],
            json=LocateRequest(locate=locate_obj),
        ):
            case RootModel(root=LocateResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("No location found.")
