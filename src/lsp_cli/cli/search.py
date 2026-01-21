from pathlib import Path
from typing import Annotated

import cyclopts
from lsap.schema.models import SymbolKind
from lsap.schema.search import SearchRequest, SearchResponse
from pydantic import RootModel

from lsp_cli.settings import settings

from . import options as op
from .utils import connect_server

app = cyclopts.App(
    name="search",
    help="Search for symbols across the entire workspace.",
)


@app.default
async def search(
    query: Annotated[
        str,
        cyclopts.Parameter(
            help="The name or partial name of the symbol to search for."
        ),
    ],
    opts: op.GlobalOpts = op.GlobalOpts(),
    workspace: op.WorkspaceOpt = None,
    kinds: Annotated[
        list[str] | None,
        cyclopts.Parameter(
            name=["--kind", "-k"],
            help="Filter by symbol kind (e.g., 'class', 'function'). Can be specified multiple times.",
        ),
    ] = None,
    max_items: op.MaxItemsOpt = None,
    start_index: op.StartIndexOpt = 0,
    pagination_id: op.PaginationIdOpt = None,
) -> None:
    """
    Search for symbols across the entire workspace by name query.
    """
    async with connect_server(workspace or Path.cwd()) as client:
        effective_max_items = (
            max_items if max_items is not None else settings.default_max_items
        )

        match await client.post(
            "/capability/search",
            RootModel[SearchResponse | None],
            json=SearchRequest(
                query=query,
                kinds=[SymbolKind(k) for k in kinds] if kinds else None,
                max_items=effective_max_items,
                start_index=start_index,
                pagination_id=pagination_id,
            ),
        ):
            case RootModel(root=SearchResponse() as resp) if resp.items:
                print(resp.format())
                if effective_max_items and len(resp.items) >= effective_max_items:
                    print(
                        f"\nInfo: Showing {effective_max_items} results. Use --max-items to see more."
                    )
            case _:
                print("Warning: No matches found")
