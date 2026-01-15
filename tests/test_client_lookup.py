from pathlib import Path
import pytest
from lsp_cli.client import find_client


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


def test_find_python_client(fixtures_dir):
    # Testing with the current project as a python candidate
    project_root = fixtures_dir.parent.parent
    path = project_root / "src" / "lsp_cli" / "client.py"

    target = find_client(path)
    assert target is not None
    # BasedpyrightClient or PyrightClient
    assert "pyright" in target.client_cls.__name__.lower()
    assert target.project_path.resolve() == project_root.resolve()


def test_find_go_client(fixtures_dir):
    go_project = fixtures_dir / "go_project"
    path = go_project / "main.go"

    target = find_client(path)
    assert target is not None
    # GoplsClient
    assert "gopls" in target.client_cls.__name__.lower()
    assert target.project_path.resolve() == go_project.resolve()


def test_find_rust_client(fixtures_dir):
    rust_project = fixtures_dir / "rust_project"
    path = rust_project / "src" / "main.rs"

    target = find_client(path)
    assert target is not None
    # RustAnalyzerClient
    assert "rust" in target.client_cls.__name__.lower()
    assert target.project_path.resolve() == rust_project.resolve()


def test_find_typescript_client(fixtures_dir):
    ts_project = fixtures_dir / "typescript_project"
    path = ts_project / "index.ts"

    target = find_client(path)
    assert target is not None
    # TypescriptClient or TsserverClient
    name = target.client_cls.__name__.lower()
    assert "typescript" in name or "ts" in name
    assert target.project_path.resolve() == ts_project.resolve()


def test_find_deno_client(fixtures_dir):
    deno_project = fixtures_dir / "deno_project"
    path = deno_project / "main.ts"

    target = find_client(path)
    assert target is not None
    assert "deno" in target.client_cls.__name__.lower()
    assert target.project_path.resolve() == deno_project.resolve()


def test_find_java_client(fixtures_dir):
    java_project = fixtures_dir / "java_project"
    path = java_project / "src" / "main" / "java" / "com" / "example" / "Greeter.java"

    target = find_client(path)
    assert target is not None
    # JdtlsClient
    assert "jdt" in target.client_cls.__name__.lower()
    assert target.project_path.resolve() == java_project.resolve()


def test_find_no_client():
    path = Path("/tmp/nonexistent_project_12345/file.txt")
    target = find_client(path)
    assert target is None


def test_find_client_with_cwd(fixtures_dir):
    go_project = fixtures_dir / "go_project"
    path = go_project / "main.go"

    # Constrain search to the project directory itself
    target = find_client(path, cwd=go_project)
    assert target is not None
    assert target.project_path.resolve() == go_project.resolve()

    # Constrain search to a different directory should raise ValueError
    # as the path is not relative to the cwd
    other_dir = fixtures_dir / "rust_project"
    with pytest.raises(
        ValueError, match="is not relative to the specified working directory"
    ):
        find_client(path, cwd=other_dir)
