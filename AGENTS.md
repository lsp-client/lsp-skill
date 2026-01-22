# AGENTS.md

## Development Commands

- Lint & format: `ruff check --fix && ruff format`
- Type checking: `ty check <dir_or_file>`
- Run tests: `uv run pytest`
- Sync latest deps: `uv sync --upgrade`

## Release Workflow

1. Update version in `pyproject.toml` and `skills/lsp-code-analysis/.version`
2. Run `just check` and `just test`
3. Commit: `git add . && git commit -m "Bump version to x.y.z"`
4. Release: `just release x.y.z` (creates tag and pushes)
5. GitHub Actions will automatically:
   - Stable (`v*.*.*`): Publish to PyPI + GitHub Release
   - Beta (`v*.*.*-beta.*`): Publish to TestPyPI + Pre-release

## Submodule Management

- This repository contains submodules in `packages/LSAP` and `packages/lsp-client`.
- **Pull Requests**: When modifying code within these submodules, always create the PR in the submodule's own repository.

## Code Style Guidelines

- Python: 3.13+ required
- `attrs` for class definitions
- `anyio` and `asyncer` for async programming
- `cyclopts` for cli, `rich` for printing
- Output: Use plain text without colors or special formatting for all CLI messages
