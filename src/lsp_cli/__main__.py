import sys
from textwrap import dedent

import cyclopts

from lsp_cli import server
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
from lsp_cli.cli.utils import current_client_id
from lsp_cli.logging import setup_logging
from lsp_cli.settings import MANAGER_LOG_PATH, get_client_log_path

app = cyclopts.App(
    help="LSP CLI: A command-line tool for interacting with Language Server Protocol (LSP) features.",
    help_formatter="plain",
)

# Add sub-apps
app.command(server.app)
app.command(rename.app)
app.command(definition.app)
app.command(doc.app)
app.command(locate.app)
app.command(reference.app)
app.command(outline.app)
app.command(symbol.app)
app.command(search.app)


def run() -> None:
    setup_logging()

    try:
        app()
    except Exception as e:
        client_id = current_client_id.get()
        client_log_path = get_client_log_path(client_id)

        print(
            dedent(
                f"""
                An error occurred: {e}
                For more details, check the logs:
                manager: {MANAGER_LOG_PATH}
                client: {client_log_path}
                """
            ),
            file=sys.stderr,
        )

        raise e


if __name__ == "__main__":
    run()
