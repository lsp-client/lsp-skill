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
from lsp_cli.server import app as server_app
from lsp_cli.settings import CLI_LOG_PATH, settings

app = typer.Typer(
    help="LSP CLI: A command-line tool for interacting with Language Server Protocol (LSP) features.",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 1000,
        "terminal_width": 1000,
        "ignore_unknown_options": True,
        "allow_extra_args": True,
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
    try:
        app()
    except Exception:
        if settings.debug:
            raise
        print(f"For more details, check the log at: {CLI_LOG_PATH}", file=sys.stderr)


if __name__ == "__main__":
    run()
