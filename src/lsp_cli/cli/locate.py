import cyclopts
from lsap.schema.locate import LocateRequest, LocateResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
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
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Locate a position or range in the codebase.
    """
    main_callback(opts.debug)
    locate_obj = create_locate(file_path, scope, find)

    async with connect_server(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/locate",
            Nullable[LocateResponse],
            json=LocateRequest(locate=locate_obj),
        ):
            case Nullable(root=LocateResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No location found.")
