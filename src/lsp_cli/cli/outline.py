from pathlib import Path
from typing import Annotated

import cyclopts
from lsap.schema.models import SymbolKind
from lsap.schema.outline import OutlineRequest, OutlineResponse
from pydantic import RootModel

from . import options as op
from .main import main_callback
from .utils import connect_server

app = cyclopts.App(
    name="outline",
    help="Get the hierarchical symbol outline for a specific file.",
)


@app.default
async def outline(
    file_path: Annotated[
        Path,
        cyclopts.Parameter(help="Path to the file to get the symbol outline for."),
    ],
    opts: op.GlobalOpts = op.GlobalOpts(),
    all_symbols: Annotated[
        bool,
        cyclopts.Parameter(
            name=["--all", "-a"],
            help="Show all symbols including local variables and parameters.",
        ),
    ] = False,
    project: op.ProjectOpt = None,
) -> None:
    """
    Get the hierarchical symbol outline (classes, functions, etc.) for a specific file.
    """

    main_callback(opts.debug)

    async with connect_server(file_path, project_path=project) as client:
        match await client.post(
            "/capability/outline",
            RootModel[OutlineResponse | None],
            json=OutlineRequest(file_path=file_path.resolve()),
        ):
            case RootModel(root=OutlineResponse() as resp) if resp.items:
                if not all_symbols:
                    filtered_items = [
                        item
                        for item in resp.items
                        if item.kind
                        in {
                            SymbolKind.Class,
                            SymbolKind.Function,
                            SymbolKind.Method,
                            SymbolKind.Interface,
                            SymbolKind.Enum,
                            SymbolKind.Module,
                            SymbolKind.Namespace,
                            SymbolKind.Struct,
                        }
                    ]
                    resp.items = filtered_items
                    if not filtered_items:
                        print(
                            "Warning: No symbols found (use --all to show local variables)"
                        )
                        return
                print(resp.format())
            case _:
                print("Warning: No symbols found")
