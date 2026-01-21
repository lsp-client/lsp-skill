import sys
from textwrap import dedent
from typing import Annotated

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
from lsp_cli.settings import CLI_LOG_PATH, MANAGER_LOG_PATH
from lsp_cli.state import State
from lsp_cli.state import state as global_state

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


@app.default
def main(
    state: Annotated[State, cyclopts.Parameter(name="*")] = State(),
) -> None:
    global_state.debug = state.debug


def run() -> None:
    try:
        app()
    except Exception as e:
        print(
            dedent(
                f"""
                An error occurred: {e}
                For more details, check the log:
                    - cli: {CLI_LOG_PATH}
                    - manager: {MANAGER_LOG_PATH}
                """
            ),
            file=sys.stderr,
        )


if __name__ == "__main__":
    run()
