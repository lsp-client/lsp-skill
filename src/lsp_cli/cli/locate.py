from typing import Annotated

import cyclopts
from lsap.schema.locate import LocateRequest, LocateResponse
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(name="locate")


@app.default
async def locate(
    file_path: op.FilePathOpt,
    scope: Annotated[
        str | None,
        cyclopts.Parameter(name=["--scope", "-s"]),
    ] = None,
    find: Annotated[
        str | None,
        cyclopts.Parameter(name=["--find"]),
    ] = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Locate a position or range in the codebase using a string syntax.

    Args:
        file_path:
            Path to the file.
        scope:
            Narrow search to a symbol body or line range.
            If omitted, search the entire file (requires `find`).

            Valid formats:
              - `line`: Single line number (e.g., `42`).
              - `start,end`: Line range (e.g., `10,20`). Use 0 for end to mean till EOF (e.g., `10,0`).
              - `symbol.path`: Dot-separated symbol path (e.g., `MyClass.my_method`).
        find:
            Text pattern to find within scope.
            If omitted, locate the start of the `scope` (requires `scope`).
            For symbol scopes, this points to the symbol declaration.

            Whitespace insensitive (e.g., `int main` matches `int  \\nmain`).

            Marker Detection:
              - An optional position marker `<|>` can be placed for exact location.
              - If not provided, the position defaults to the start of the match.
              - Use `<|>` for single level, `<<|>>` for double level if `<|>` appears in source, etc.

            Examples:
              - `my_variable`
              - `self.<|>`
              - `return <|>result`
              - `x = <|> + y <<|>> z`
        project:
            Path to the project. If specified, start a server in this directory.
    """

    locate = create_locate(file_path, scope, find)

    async with connect_server(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/locate",
            RootModel[LocateResponse | None],
            json=LocateRequest(locate=locate),
        ):
            case RootModel(root=LocateResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("No location found.")
