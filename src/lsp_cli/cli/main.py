from typing import Annotated

import typer

from lsp_cli.utils.debug import setup_debug
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
    setup_debug(debug)

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
