import logging
import sys

import typer

from lsp_cli.cli import (
    definition,
    doc,
    locate,
    outline,
    reference,
    rename,
    search,
    symbol,
)
from lsp_cli.cli.main import main_callback
from lsp_cli.cli.shared import get_msg
from lsp_cli.server import app as server_app
from lsp_cli.settings import settings

app = typer.Typer(
    help="LSP CLI: A command-line tool for interacting with Language Server Protocol (LSP) features.",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 1000,
        "terminal_width": 1000,
    },
    add_completion=False,
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
)

# Set callback
app.callback(invoke_without_command=True)(main_callback)

# Add sub-typers
app.add_typer(server_app)
app.add_typer(rename.app)
app.add_typer(definition.app)
app.add_typer(doc.app)
app.add_typer(locate.app)
app.add_typer(reference.app)
app.add_typer(outline.app)
app.add_typer(symbol.app)
app.add_typer(search.app)


def run() -> None:
    # Suppress httpx INFO logs in CLI (unless debug mode)
    if not settings.debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        app()
    except (typer.Exit, typer.Abort):
        pass
    except Exception as e:
        if settings.debug:
            raise
        print(f"Error: {get_msg(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
