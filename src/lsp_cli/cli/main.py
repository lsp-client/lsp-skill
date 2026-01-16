import sys

import typer
from loguru import logger

from lsp_cli.settings import settings


def main_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable verbose debug logging for troubleshooting.",
    ),
) -> None:
    if debug:
        settings.debug = True

    logger.remove()
    logger.add(sys.stderr, level=settings.effective_log_level)

    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit
