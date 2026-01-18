"""Shared test fixtures and utilities for LSP CLI tests."""

import os
import subprocess
from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("CI"):
        return

    skip_integration = pytest.mark.skip(
        reason="Skipping integration test in non-CI environment"
    )
    integration_files = {
        "test_cli_integration",
        "test_cli_project",
        "test_server_management",
        "test_language_support",
    }
    for item in items:
        if any(f in item.nodeid for f in integration_files):
            item.add_marker(skip_integration)


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
