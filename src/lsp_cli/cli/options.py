from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from cyclopts import Parameter


@Parameter(name="*")
@dataclass
class GlobalOpts:
    debug: Annotated[
        bool,
        Parameter(
            name=["--debug", "-d"],
            help="Enable verbose debug logging for troubleshooting.",
        ),
    ] = False


LocateOpt = Annotated[
    str,
    Parameter(
        name=["--locate", "-L"],
        help="Location string (see 'lsp locate --help' for syntax).",
    ),
]

WorkspaceOpt = Annotated[
    Path | None,
    Parameter(
        name=["--workspace", "-w"],
        help="Path to workspace. Defaults to current directory.",
    ),
]

MaxItemsOpt = Annotated[
    int | None,
    Parameter(
        name=["--max-items", "-n"],
        help="Max items to return",
    ),
]

StartIndexOpt = Annotated[
    int,
    Parameter(
        name=["--start-index", "-i"],
        help="Pagination offset",
    ),
]

PaginationIdOpt = Annotated[
    str | None,
    Parameter(
        name=["--pagination-id", "-p"],
        help="Pagination token",
    ),
]

ProjectOpt = Annotated[
    Path | None,
    Parameter(
        name=["--project"],
        help="Path to the project. If specified, start a server in this directory.",
    ),
]
