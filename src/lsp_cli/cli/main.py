from typing import Annotated

from cyclopts import Parameter

from lsp_cli.logging import setup_logging
from lsp_cli.state import state


def main_callback(
    debug: Annotated[
        bool,
        Parameter(
            name=["--debug", "-d"],
            help="Enable verbose debug logging for troubleshooting.",
        ),
    ] = False,
) -> None:
    if debug:
        state.debug = True

    setup_logging()
