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
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
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
