from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

from cyclopts import Parameter, Token


def path_converter(type_: type, tokens: Iterable[Token]) -> Path:
    match tokens:
        case [token]:
            return Path(token.value).resolve()
        case _:
            raise ValueError("Expected a single path token")


def file_path_validator(type_: type, value: str) -> None:
    if not Path(value).is_file():
        raise FileNotFoundError(f"File not found or not a file: {value}")


def project_path_validator(type_: type, value: str) -> None:
    if value is None:
        return
    if not Path(value).is_dir():
        raise NotADirectoryError(f"Project path not found or not a directory: {value}")


def positive_int_validator(type_: type, value: int) -> None:
    if value is not None and value < 1:
        raise ValueError("Value must be at least 1")


def non_negative_int_validator(type_: type, value: int) -> None:
    if value is not None and value < 0:
        raise ValueError("Value must be non-negative")


FilePathOpt = Annotated[
    Path,
    Parameter(
        name=["--file-path"],
        help="Path to the file",
        converter=path_converter,
        validator=file_path_validator,
    ),
]

ScopeOpt = Annotated[
    str | None,
    Parameter(
        name=["--scope"],
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

MaxItemsOpt = Annotated[
    int | None,
    Parameter(
        name=["--max-items"],
        help="Max items to return",
        validator=positive_int_validator,
    ),
]

StartIndexOpt = Annotated[
    int,
    Parameter(
        name=["--start-index"],
        help="Pagination offset",
        validator=non_negative_int_validator,
    ),
]

PaginationIdOpt = Annotated[
    str | None,
    Parameter(
        name=["--pagination-id"],
        help="Pagination token",
    ),
]

ProjectOpt = Annotated[
    Path | None,
    Parameter(
        name=["--project"],
        help="Path to the project. If specified, start a server in this directory.",
        converter=path_converter,
        validator=project_path_validator,
    ),
]
