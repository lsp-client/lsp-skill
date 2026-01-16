import subprocess
from pathlib import Path


class TestCLIProjectOption:
    """Test the --project option in CLI commands."""

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

    def test_outline_with_project(self):
        """Test `lsp outline` with the --project option."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "__init__.py"
        project_dir = root_dir

        # Run outline command with --project
        result = self.run_lsp_command(
            "outline", str(target_file), "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        # If it succeeded, it means the --project option was accepted and the server started correctly.
        # The output should contain some outline information.
        assert len(result.stdout) > 0

    def test_definition_with_project(self):
        """Test `lsp definition` with the --project option."""
        root_dir = Path(__file__).parent.parent
        # A file that has some definitions
        target_file = root_dir / "src" / "lsp_cli" / "cli" / "shared.py"
        project_dir = root_dir

        # We need a location string. Let's use something simple like line 22 (managed_client)
        locate_str = f"{target_file}:22"

        result = self.run_lsp_command(
            "definition", "--locate", locate_str, "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert len(result.stdout) > 0

    def test_locate_with_project(self):
        """Test `lsp locate` with the --project option."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "cli" / "shared.py"
        project_dir = root_dir

        locate_str = f"{target_file}:22"

        result = self.run_lsp_command(
            "locate", locate_str, "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert str(target_file) in result.stdout

    def test_symbol_with_project(self):
        """Test `lsp symbol` with the --project option."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "cli" / "shared.py"
        project_dir = root_dir

        locate_str = f"{target_file}:22"

        result = self.run_lsp_command(
            "symbol", "--locate", locate_str, "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "managed_client" in result.stdout

    def test_search_with_project(self):
        """Test `lsp search` with the --project option."""
        root_dir = Path(__file__).parent.parent
        project_dir = root_dir

        # Search for 'managed_client'
        result = self.run_lsp_command(
            "search", "managed_client", "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "managed_client" in result.stdout

    def test_rename_with_project(self):
        """Test `lsp rename preview` with the --project option."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "cli" / "shared.py"
        project_dir = root_dir

        locate_str = f"{target_file}:22"

        # Preview rename
        result = self.run_lsp_command(
            "rename",
            "preview",
            "new_name",
            "--locate",
            locate_str,
            "--project",
            str(project_dir),
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        # Either it found rename possibilities or it didn't, but both mean the command worked
        assert "new_name" in result.stdout or "No rename possibilities" in result.stdout

    def test_doc_with_project(self):
        """Test `lsp doc` with the --project option."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "cli" / "shared.py"
        project_dir = root_dir

        locate_str = f"{target_file}:22"

        result = self.run_lsp_command(
            "doc", "--locate", locate_str, "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        # Either it found documentation or it didn't, but both mean the command worked
        assert (
            "Warning: No documentation found" in result.stdout or len(result.stdout) > 0
        )

    def test_reference_with_project(self):
        """Test `lsp reference` with the --project option."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "cli" / "shared.py"
        project_dir = root_dir

        locate_str = f"{target_file}:22"

        result = self.run_lsp_command(
            "reference", "--locate", locate_str, "--project", str(project_dir)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert len(result.stdout) > 0

    def test_server_start_stop_with_project(self):
        """Test `lsp server start/stop` with the --project option."""
        root_dir = Path(__file__).parent.parent
        project_dir = root_dir
        # Use a file in the project
        target_file = root_dir / "src" / "lsp_cli" / "__init__.py"

        # Start server with --project
        result_start = self.run_lsp_command(
            "server", "start", str(target_file), "--project", str(project_dir)
        )
        assert result_start.returncode == 0, f"Start failed: {result_start.stderr}"
        assert str(project_dir) in result_start.stdout

        # Stop server with --project
        result_stop = self.run_lsp_command(
            "server", "stop", str(target_file), "--project", str(project_dir)
        )
        assert result_stop.returncode == 0, f"Stop failed: {result_stop.stderr}"
        assert "Stopped server" in result_stop.stdout

    def test_invalid_project_path(self):
        """Test with an invalid project path (not a project root)."""
        root_dir = Path(__file__).parent.parent
        target_file = root_dir / "src" / "lsp_cli" / "__init__.py"

        # Use a directory that is definitely not a project root (e.g. /tmp if it's not a git repo/pyproject.toml)
        # Or just a non-existent directory
        invalid_project = root_dir / "non_existent_dir_xyz"

        result = self.run_lsp_command(
            "outline", str(target_file), "--project", str(invalid_project)
        )

        # It should fail because the project path doesn't exist or isn't a project root
        assert result.returncode != 0
        assert (
            "not found" in result.stderr.lower()
            or "no lsp client found" in result.stderr.lower()
        )
