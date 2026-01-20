import cyclopts
from lsap.schema.doc import DocRequest, DocResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .shared import create_locate, managed_client

app = cyclopts.App(
    name="doc",
    help="Get documentation and type information for a symbol.",
)


@app.default
async def doc(
    locate: op.LocateOpt,
    opts: op.GlobalOpts = op.GlobalOpts(),
    project: op.ProjectOpt = None,
) -> None:
    """
    Get documentation and type information for a symbol at a specific location.
    """
    main_callback(opts.debug)
    locate_obj = create_locate(locate)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/doc",
            Nullable[DocResponse],
            json=DocRequest(locate=locate_obj),
        ):
            case Nullable(root=DocResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print("No documentation found.")
