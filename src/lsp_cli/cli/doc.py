import cyclopts
from lsap.schema.doc import DocRequest, DocResponse
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(
    name="doc",
    help="Get documentation and type information for a symbol.",
)


@app.default
async def doc(
    file_path: op.FilePathOpt,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Get documentation and type information for a symbol.
    """

    locate = create_locate(file_path, scope, find)

    async with connect_server(locate.file_path, project_path=project) as client:
        match await client.post(
            "/capability/doc",
            RootModel[DocResponse | None],
            json=DocRequest(locate=locate),
        ):
            case RootModel(root=DocResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("No documentation found.")
