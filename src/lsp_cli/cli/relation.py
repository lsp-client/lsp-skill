from pathlib import Path
from typing import Annotated

import cyclopts
from lsap.schema.relation import RelationRequest, RelationResponse
from pydantic import RootModel

from . import options as op
from .utils import connect_server, create_locate

app = cyclopts.App(name="relation")


@app.default
async def relation(
    *,
    source_file: Annotated[
        Path,
        cyclopts.Parameter(
            name=["--source-file"],
            help="Source file path.",
            converter=op.path_converter,
            validator=op.file_path_validator,
        ),
    ],
    target_file: Annotated[
        Path,
        cyclopts.Parameter(
            name=["--target-file"],
            help="Target file path.",
            converter=op.path_converter,
            validator=op.file_path_validator,
        ),
    ],
    source_symbol: Annotated[
        str,
        cyclopts.Parameter(
            name=["--source-symbol"],
            help="Source symbol path (e.g. MyClass.method).",
        ),
    ],
    target_symbol: Annotated[
        str,
        cyclopts.Parameter(
            name=["--target-symbol"],
            help="Target symbol path (e.g. MyClass.method).",
        ),
    ],
    project: op.ProjectOpt = None,
) -> None:
    """
    Find call chains between two symbols.
    """

    source_locate = create_locate(source_file, source_symbol, None)
    target_locate = create_locate(target_file, target_symbol, None)

    async with connect_server(source_file, project_path=project) as client:
        match await client.post(
            "/capability/relation",
            RootModel[RelationResponse | None],
            json=RelationRequest(
                source=source_locate,
                target=target_locate,
            ),
        ):
            case RootModel(root=RelationResponse() as resp):
                print(resp.format())
            case RootModel(root=None):
                print("No connection found.")
