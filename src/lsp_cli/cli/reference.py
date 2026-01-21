from typing import Annotated

import cyclopts
from lsap.schema.reference import ReferenceRequest, ReferenceResponse
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(
    name="reference",
    help="Find references or implementations of a symbol.",
)


@app.default
async def reference(
    file_path: op.FilePathOpt,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    impl: Annotated[
        bool, cyclopts.Parameter(name="--impl", help="Find concrete implementations.")
    ] = False,
    context_lines: Annotated[
        int,
        cyclopts.Parameter(
            name=["--context-lines", "-C"],
            help="Number of lines of context to show around each match.",
        ),
    ] = 2,
    max_items: op.MaxItemsOpt = None,
    start_index: op.StartIndexOpt = 0,
    pagination_id: op.PaginationIdOpt = None,
    project: op.ProjectOpt = None,
) -> None:
    """
    Find references (default) or implementations (--impl) of a symbol.
    """
    mode = "implementations" if impl else "references"

    locate_obj = create_locate(file_path, scope, find)

    async with connect_server(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/reference",
            RootModel[ReferenceResponse | None],
            json=ReferenceRequest(
                locate=locate_obj,
                mode=mode,
                context_lines=context_lines,
                max_items=max_items,
                start_index=start_index,
                pagination_id=pagination_id,
            ),
        ):
            case RootModel(root=ReferenceResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print(f"Warning: No {mode} found")
