"""
Integration tests for CLI commands to ensure server connectivity.

This tests actual CLI command execution to verify that the server
management system works correctly in real-world usage scenarios.
"""

import subprocess
import time
from pathlib import Path

import pytest
from conftest import BaseLSPTest


@pytest.fixture(scope="module")
def test_project_file():
    """Get a test Python file from the project."""
    return Path(__file__).parent.parent / "src" / "lsp_cli" / "__init__.py"


class TestCLIIntegration:
    """Test real CLI command execution."""

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

    def test_server_list(self):
        """Test `lsp server list` command."""
        result = self.run_lsp_command("server", "list")
        assert result.returncode == 0, f"Command failed: {result.stderr}"

    def test_server_start(self, test_project_file):
        """Test `lsp server start` command."""
        result = self.run_lsp_command("server", "start", str(test_project_file))
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "Success" in result.stdout or result.returncode == 0

    def test_server_start_twice(self, test_project_file):
        """Test starting the same server twice (should reuse)."""
        # Start first time
        result1 = self.run_lsp_command("server", "start", str(test_project_file))
        assert result1.returncode == 0

        # Start second time (should reuse)
        result2 = self.run_lsp_command("server", "start", str(test_project_file))
        assert result2.returncode == 0

    def test_server_stop(self, test_project_file):
        """Test `lsp server stop` command."""
        # Start server first
        self.run_lsp_command("server", "start", str(test_project_file))

        # Stop server
        result = self.run_lsp_command("server", "stop", str(test_project_file))
        assert result.returncode == 0, f"Command failed: {result.stderr}"


class TestRapidCLICommands:
    """Test rapid execution of multiple CLI commands."""

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

    def test_rapid_server_list(self):
        """Test rapid execution of server list commands."""
        failures = []
        for i in range(5):
            result = self.run_lsp_command("server", "list")
            if result.returncode != 0:
                failures.append(f"Attempt {i + 1} failed: {result.stderr}")
            time.sleep(0.1)

        assert not failures, f"Some commands failed: {failures}"

    def test_rapid_server_operations(self, test_project_file):
        """Test rapid start/list operations."""
        failures = []

        # Start server
        result = self.run_lsp_command("server", "start", str(test_project_file))
        if result.returncode != 0:
            failures.append(f"Start failed: {result.stderr}")

        # Rapid list commands
        for i in range(3):
            result = self.run_lsp_command("server", "list")
            if result.returncode != 0:
                failures.append(f"List {i + 1} failed: {result.stderr}")
            time.sleep(0.05)

        # Stop server
        result = self.run_lsp_command("server", "stop", str(test_project_file))
        if result.returncode != 0:
            failures.append(f"Stop failed: {result.stderr}")

        assert not failures, f"Some commands failed: {failures}"

    def test_concurrent_cli_commands(self, test_project_file):
        """Test that concurrent CLI commands don't interfere."""
        # This simulates a user running multiple commands in rapid succession
        # in different terminals

        import concurrent.futures

        def run_command(cmd_args):
            result = self.run_lsp_command(*cmd_args)
            return result.returncode == 0, result.stderr

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []

            # Submit multiple commands concurrently
            futures.append(
                executor.submit(
                    run_command, ["server", "start", str(test_project_file)]
                )
            )
            futures.append(executor.submit(run_command, ["server", "list"]))
            futures.append(executor.submit(run_command, ["server", "list"]))

            # Wait for all to complete
            results = [f.result() for f in futures]

        # All commands should succeed
        failures = [stderr for success, stderr in results if not success]
        assert not failures, f"Some concurrent commands failed: {failures}"


class TestPathNormalization(BaseLSPTest):
    """Test that relative paths are correctly normalized to absolute paths."""

    def test_server_start_relative_path_from_subdir(self):
        """Test that starting a server with a relative path from a subdirectory works."""
        root_dir = Path(__file__).parent.parent
        # Use Python project as it's more reliable in this environment
        project_dir = root_dir / "src" / "lsp_cli"
        target_file_rel = Path("__init__.py")

        try:
            result = subprocess.run(
                ["uv", "run", "lsp", "server", "start", str(target_file_rel)],
                capture_output=True,
                text=True,
                cwd=str(project_dir),
                timeout=30,
            )

            assert result.returncode == 0, f"Command failed: {result.stderr}"
            assert str(project_dir / target_file_rel) in result.stdout
            assert "Success" in result.stdout

        finally:
            subprocess.run(
                ["uv", "run", "lsp", "server", "stop", str(target_file_rel)],
                cwd=str(project_dir),
                capture_output=True,
                timeout=30,
            )

    def test_outline_relative_path_normalization(self):
        """Test that outline command normalizes relative paths."""
        root_dir = Path(__file__).parent.parent
        project_dir = root_dir / "src" / "lsp_cli"
        target_file_rel = Path("__init__.py")

        # Start server first to ensure it's running
        subprocess.run(
            ["uv", "run", "lsp", "server", "start", str(target_file_rel)],
            cwd=str(project_dir),
            capture_output=True,
            timeout=30,
        )
        time.sleep(2)

        try:
            result = subprocess.run(
                ["uv", "run", "lsp", "outline", str(target_file_rel)],
                capture_output=True,
                text=True,
                cwd=str(project_dir),
                timeout=30,
            )

            assert result.returncode == 0, f"Outline failed: {result.stderr}"

        finally:
            subprocess.run(
                ["uv", "run", "lsp", "server", "stop", str(target_file_rel)],
                cwd=str(project_dir),
                capture_output=True,
                timeout=30,
            )


class TestConnectionReliability:
    """Test that connections remain stable."""

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

    def test_no_connection_errors(self, test_project_file):
        """Test that we don't get connection errors during normal usage."""
        # Start server
        result = self.run_lsp_command("server", "start", str(test_project_file))
        assert result.returncode == 0
        assert "connection" not in result.stderr.lower()
        assert "failed to connect" not in result.stderr.lower()

        # List servers
        result = self.run_lsp_command("server", "list")
        assert result.returncode == 0
        assert "connection" not in result.stderr.lower()
        assert "failed to connect" not in result.stderr.lower()

        # List again
        result = self.run_lsp_command("server", "list")
        assert result.returncode == 0
        assert "connection" not in result.stderr.lower()
        assert "failed to connect" not in result.stderr.lower()

    def test_manager_auto_start_reliability(self):
        """Test that manager auto-starts reliably."""
        # Kill any existing manager
        subprocess.run(
            ["pkill", "-f", "lsp_cli.manager"],
            capture_output=True,
        )
        time.sleep(0.5)

        # First command should auto-start manager
        result = self.run_lsp_command("server", "list")
        assert result.returncode == 0, f"Failed to auto-start manager: {result.stderr}"

        # Subsequent commands should work
        result = self.run_lsp_command("server", "list")
        assert result.returncode == 0, f"Manager not responding: {result.stderr}"
