from typing import Annotated

import cyclopts
from lsap.schema.reference import ReferenceRequest, ReferenceResponse

from lsp_cli.utils.model import Nullable

from . import options as op
from .main import main_callback
from .shared import create_locate, managed_client

app = cyclopts.App(
    name="reference",
    help="Find references or implementations of a symbol.",
)


@app.default
async def reference(
    file_path: op.FilePathOpt,
    scope: op.ScopeOpt = None,
    find: op.FindOpt = None,
    opts: op.GlobalOpts = op.GlobalOpts(),
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

    Scope formats:
    - `<line>` - Single line number (e.g., `42`).
    - `<start>,<end>` - Line range (e.g., `10,20`). Use 0 for end to mean till EOF (e.g., `10,0`).
    - `<symbol_path>` - Symbol path (e.g., `MyClass.my_method`).

    Find format:
    - Pattern to search for within the file or scope.
    - Supports markers like `<|>` to specify exact position.
    """
    main_callback(opts.debug)
    mode = "implementations" if impl else "references"

    locate_obj = create_locate(file_path, scope, find)

    async with managed_client(locate_obj.file_path, project_path=project) as client:
        match await client.post(
            "/capability/reference",
            Nullable[ReferenceResponse],
            json=ReferenceRequest(
                locate=locate_obj,
                mode=mode,
                context_lines=context_lines,
                max_items=max_items,
                start_index=start_index,
                pagination_id=pagination_id,
            ),
        ):
            case Nullable(root=ReferenceResponse() as resp):
                print(resp.format())
            case Nullable(root=None):
                print(f"Warning: No {mode} found")
