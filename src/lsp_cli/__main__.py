import signal
import sys
from textwrap import dedent

import cyclopts
from loguru import logger

from lsp_cli.cli import (
    definition,
    locate,
    outline,
    reference,
    relation,
    rename,
    search,
    server,
    symbol,
)
from lsp_cli.exceptions import CapabilityCommandException
from lsp_cli.logging import setup_logging
from lsp_cli.settings import MANAGER_LOG_PATH, get_client_log_path
from lsp_cli.state import env_state

app = cyclopts.App(
    help="LSP CLI: A command-line tool for interacting with Language Server Protocol (LSP) features.",
    help_format="markdown",
    help_formatter="plain",
    print_error=False,
    exit_on_error=False,
)

# Add sub-apps
app.command(server.app)
app.command(rename.app)
app.command(definition.app)
app.command(locate.app)
app.command(reference.app)
app.command(relation.app)
app.command(outline.app)
app.command(symbol.app)
app.command(search.app)


@logger.catch
def run() -> None:
    if sys.platform != "win32":
        # Restore default SIGPIPE behavior to prevent BrokenPipeError when piping to tools like `head`.
        # This allows the OS to terminate the process immediately when the pipe closes, avoiding
        # tracebacks and "Exception ignored" messages during Python's interpreter shutdown.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    setup_logging()

    try:
        app()
    except Exception as e:  # noqa: BLE001
        match e:
            case CapabilityCommandException() as cce:
                client_log_path = get_client_log_path(cce.client_id)
            case _:
                client_log_path = get_client_log_path(None)

        print(f"An error occurred: {e}", file=sys.stderr)
        if env_state.debug:
            print(
                dedent(
                    f"""\
                    For more details, check the logs:
                    manager: {MANAGER_LOG_PATH}
                    client: {client_log_path}"""
                ),
                file=sys.stderr,
            )


if __name__ == "__main__":
    run()
