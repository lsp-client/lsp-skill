import sys

import typer
from loguru import logger

from lsp_cli.settings import CLI_LOG_PATH, settings


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

    CLI_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        CLI_LOG_PATH,
        rotation="10 MB",
        retention="1 day",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True,
    )

    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit
