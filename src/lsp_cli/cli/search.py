from pathlib import Path
from typing import Annotated

import typer
from lsap.schema.models import SymbolKind
from lsap.schema.search import SearchRequest, SearchResponse

from lsp_cli.settings import settings
from lsp_cli.utils.sync import cli_syncify

from . import options as op
from .shared import managed_client

app = typer.Typer()


@app.command("search")
@cli_syncify
async def search(
    query: Annotated[
        str,
        typer.Argument(help="The name or partial name of the symbol to search for."),
    ],
    workspace: op.WorkspaceOpt = None,
    kinds: Annotated[
        list[str] | None,
        typer.Option(
            "--kind",
            "-k",
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

    async with managed_client(workspace or Path.cwd()) as client:
        effective_max_items = (
            max_items if max_items is not None else settings.default_max_items
        )

        resp_obj = await client.post(
            "/capability/search",
            SearchResponse,
            json=SearchRequest(
                query=query,
                kinds=[SymbolKind(k) for k in kinds] if kinds else None,
                max_items=effective_max_items,
                start_index=start_index,
                pagination_id=pagination_id,
            ),
        )

    if resp_obj and resp_obj.items:
        print(resp_obj.format())
        if effective_max_items and len(resp_obj.items) >= effective_max_items:
            print(
                f"\nInfo: Showing {effective_max_items} results. Use --max-items to see more."
            )
    else:
        print("Warning: No matches found")
