"""Shared test fixtures and utilities for LSP CLI tests."""

import subprocess
from pathlib import Path


class BaseLSPTest:
    """Base class for LSP CLI tests with common helper methods."""

    def run_lsp_command(self, *args, timeout=30):
        """Run an lsp command and return the result."""
        result = subprocess.run(
            ["uv", "run", "lsp", *list(args)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent,
        )
        return result
