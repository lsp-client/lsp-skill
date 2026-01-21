from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from cyclopts import Parameter, Token


@Parameter(name="*")
@dataclass
class GlobalOpts:
    debug: Annotated[
        bool,
        Parameter(
            name=["--debug", "-d"],
            help="Enable verbose debug logging for troubleshooting",
        ),
    ] = False


def file_path_coverter(type_: type, tokens: Iterable[Token]) -> Path:
    match tokens:
        case [token]:
            return Path(token.value).resolve()
        case _:
            raise ValueError("Expected a single file path token")


def file_path_validator(type_: type, value: str) -> None:
    if not Path(value).is_file():
        raise FileNotFoundError(f"File not found or not a file: {value}")


FilePathOpt = Annotated[
    Path,
    Parameter(
        name=["--file-path", "-f"],
        help="Path to the file",
        converter=file_path_coverter,
        validator=file_path_validator,
    ),
]

ScopeOpt = Annotated[
    str | None,
    Parameter(
        name=["--scope", "-s"],
        help="Narrow search to a line, range, or symbol. See 'lsp locate --help' for details.",
    ),
]

FindOpt = Annotated[
    str | None,
    Parameter(
        name=["--find"],
        help="Text pattern to find. See 'lsp locate --help' for details.",
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
