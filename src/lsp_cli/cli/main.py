from typing import Annotated

import typer

from lsp_cli.logging import setup_logging
from lsp_cli.settings import CLI_LOG_PATH, settings


def main_callback(
    ctx: typer.Context,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help="Enable verbose debug logging for troubleshooting.",
        ),
    ] = False,
) -> None:
    if debug:
        settings.debug = True

    setup_logging(log_file=CLI_LOG_PATH)

    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit
