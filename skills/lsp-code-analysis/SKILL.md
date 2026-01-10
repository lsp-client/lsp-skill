---
name: lsp-code-analysis
description: Semantic code analysis via LSP. Navigate code (definitions, references, implementations), search symbols, preview refactorings, and get file outlines. Use for exploring unfamiliar codebases or performing safe refactoring.
license: LICENSE
---

# LSP Code Analysis

> [!IMPORTANT]
> **Update Required**: You MUST run the installation script to check for updates before using this skill in each session:
>
> ```bash
> curl -sSL https://github.com/lsp-client/lsp-skill/releases/latest/download/install.sh | bash -s -- [tool_name]
> ```

> Replace `<tool_name>` with your own name. Should be one of `claude`, `gemini`, `codex`, or `opencode`.

## Overview

Use `lsp-cli` for semantic code navigation and analysis via Language Server Protocol (LSP).

LSP provides **compiler-accurate** code understanding that surpasses text-based search:

- **Semantic navigation**: Jump to definitions, find references, locate implementations - understands code structure, not just text patterns.
- **Language-aware**: Distinguishes between variables, functions, classes, types - eliminates false positives from text search.
- **Cross-file intelligence**: Trace dependencies, refactor safely across entire codebase - knows what imports what.
- **Type-aware**: Get precise type information, signatures, documentation - without reading implementation code.

**When to use**: Exploring unfamiliar code, refactoring, debugging, understanding dependencies. **Prefer over grep/text search** when you need to understand how code works, not just where text appears.

## Prerequisites

```bash
# if not installed
uv tool install --python 3.13 lsp-cli

# keep up with latest version
uv tool upgrade lsp-cli
```

## Commands

All commands support `-h` or `--help`. Command aliases: `def` (definition), `ref` (reference), `sym` (symbol).

### Locating Symbols

Most commands use a unified **Locate String** syntax via the `-L` or `--locate` option.

**Syntax**: `<file_path>[:<scope>][@<find>]`

- **Scope**: Narrows search area. Supports line (`:42`), range (`:10,20` or `:10-20`), or symbol path (`:User.login`).
- **Find**: Text pattern within scope. Whitespace-insensitive; matches even if code formatting differs. Use `@text` or `@snippet<|>with_marker` for exact cursor positioning.
- **Marker**: `<|>` indicates the exact position for symbol resolution (e.g., `user.<|>name`).

**Examples**:

- `main.py:42` - Exactly line 42 in `main.py`.
- `app.py:User.login` - The `login` method of class `User` in `app.py`.
- `utils.py:DataUtils@process_data(<|>` - Position at the call to `process_data` within the `DataUtils` class in `utils.py`.
- `api.py:10,50@config` - The string `config` within lines 10-50 of `api.py` (also `10-50`).

You may use `lsp locate <string>` to verify a location before running other commands.

```bash
# Verify location exists
lsp locate "main.py:42@process_data" --check
```

### Outline: File Structure

**MUST** use before reading files to get structural overview. **SHOULD** prefer `outline` over full `read` for non-essential code.

```bash
# Main symbols (classes, functions, methods)
lsp outline <file_path>

# All symbols (includes variables, parameters)
lsp outline <file_path> --all
```

### Definition: Navigate to Source

Jump to symbol definitions. **RECOMMENDED** for verifying function signatures without reading full implementation.

```bash
# By locate string (alias: lsp def)
lsp definition -L "models.py:User.get_id"

# Declaration instead of definition
lsp definition -L "models.py:25" --decl

# Type definition
lsp definition -L "models.py:30" --type
```

### Reference: Find All Usages

**REQUIRED** before refactoring or deleting code. Use `--impl` for finding implementations in abstract codebases. Supports pagination for large result sets.

```bash
# Find references (alias: lsp ref)
lsp reference -L "main.py:MyClass.run@logger"

# Find implementations
lsp reference -L "api.py@IDataProvider" --impl

# More context lines
lsp reference -L "app.py:10@TestClass" --context-lines 5

# Limit results and use pagination
lsp reference -L "utils.py:helper" --max-items 50 --start-index 0
```

### Hover: Get Documentation

**SHOULD** prefer over `read` for understanding API contracts. Returns docstrings and type signatures.

```bash
# By line
lsp hover -L "main.py:42"

# By text search
lsp hover -L "models.py@process_data<|>"
```

### Search: Global Symbol Search

**RECOMMENDED** when symbol location is unknown. Use `--kind` to filter results. Supports pagination for large result sets.

```bash
# Search symbols (defaults to current directory)
lsp search "MyClassName"

# Specific workspace
lsp search "UserModel" --workspace /path/to/project

# Filter by kind (can be specified multiple times)
lsp search "init" --kind function --kind method

# Limit results
lsp search "Config" --max-items 10

# Pagination
lsp search "User" --max-items 20 --start-index 0
```

### Rename: Safe Refactoring

Rename a symbol workspace-wide. Use two-step workflow: preview then execute.

```bash
# Step 1: Preview changes and get rename_id
lsp rename preview new_name -L "models.py:OldName"

# Step 2: Execute changes using the rename_id from preview
lsp rename execute <rename_id>

# Execute with exclusions
lsp rename execute <rename_id> --exclude tests/test_old.py --exclude legacy/
```

### Symbol: Local Symbol Info

Get precise coordinate info for a symbol. **MAY** be used to anchor subsequent `hover` or `definition` calls.

```bash
# By line (alias: lsp sym)
lsp symbol -L "main.py:15"

# By text search
lsp symbol -L "utils.py@UserClass<|>"
```

### Server: Manage Background Servers

Background manager starts automatically. Manual control is **OPTIONAL**. Running `lsp server` without subcommand defaults to `list`.

```bash
# List running servers (default)
lsp server
lsp server list

# Start server for a project
lsp server start <path>

# Stop server for a project
lsp server stop <path>
```

## Best Practices

### General Workflows

#### Understanding Unfamiliar Code

**RECOMMENDED** sequence for exploring new codebases:

1. **Start with outline** - Get file structure without reading implementation.
2. **Inspect signatures** - Use `hover` to understand API contracts.
3. **Navigate dependencies** - Follow `definition` chains.
4. **Map usage** - Find where code is called with `reference`.

#### Refactoring Preparation

**REQUIRED** steps before modifying code:

1. **Find all references** - Identify impact scope.
2. **Check implementations** - For interfaces/abstract classes using `--impl`.
3. **Verify type definitions** - Understand type propagation with `--type`.
4. **Preview Rename** - Use `lsp rename preview` to see workspace-wide impact before executing.

#### Debugging Unknown Behavior

1. **Search for the symbol** - Locate where it's defined with `lsp search`.
2. **Find the definition** - Verify implementation.
3. **Trace all callers** - See where it's invoked using `lsp reference`.

### Performance Tips

- **Use `outline` aggressively** - Avoid reading entire files when possible.
- **Leverage symbol paths** - More precise than line numbers for nested structures.
- **Use `--max-items`** - Limit results in large codebases.
- **Prefer `hover` over `definition`** - For understanding without navigating.
- **Verify with `locate`** - If a command fails, use `lsp locate` to debug the target.

### Common Patterns

#### Finding Interface Implementations

```bash
# Step 1: Locate interface definition
lsp search "IUserService" --kind interface

# Step 2: Find all implementations
lsp reference -L "src/interfaces.py:IUserService" --impl
```

#### Tracing Data Flow

```bash
# Step 1: Find where data is created
lsp search "UserDTO" --kind class

# Step 2: Find where it's used
lsp reference -L "models.py:UserDTO"

# Step 3: Check transformations
lsp hover -L "transform.py:map_to_dto"
```

#### Understanding Type Hierarchies

```bash
# Step 1: Get class outline
lsp outline models.py

# Step 2: Find subclasses (references to base)
lsp reference -L "models.py:BaseModel"

# Step 3: Check type definitions
lsp definition -L "models.py:BaseModel" --type
```

### Domain-Specific Guides

For specialized scenarios, see:

- **Frontend**: [bp_frontend.md](references/bp_frontend.md)
- **Backend**: [bp_backend.md](references/bp_backend.md)
