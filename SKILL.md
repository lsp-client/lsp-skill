---
name: lsp-code-analysis
description: Code navigation and analysis via LSP. Use when you need to:(1) Navigate to definitions/declarations/implementations, (2) Find all references before refactoring, (3) Get file structure outline, (4) Search symbols by name, (5) Get type signatures and documentation. Language-aware, more accurate than text search.
license: LICENSE
---

# LSP Code Analysis

Use `lsp-cli` for code navigation via Language Server Protocol.

## Prerequisites

```bash
uv tool install lsp-cli
```

## Commands

All commands support `-h` or `--help`. Command aliases: `def` (definition), `ref` (reference), `sym` (symbol).

### Locating Symbols

Most commands require specifying a location in the file. Use `--scope` and `--find` together or separately.

#### `--scope` (or `-s`)

Narrows down the search area:

**Line Number** (1-based):

```bash
lsp definition main.py --scope 42
```

Use when you know the exact line number.

**Line Range**:

```bash
lsp reference utils.py --scope 10,50
```

Searches between lines 10-50. Useful for targeting specific functions or classes.

**Symbol Path**:

```bash
lsp definition models.py --scope User.profile.update
lsp hover api.py --scope AuthService.login
```

Navigate nested symbols. Language server resolves the path to exact location.

#### `--find` (or `-f`)

Text-based search within the file (or within `--scope` if specified):

**Basic text search**:

```bash
lsp definition main.py --find "process_data"
```

Finds first occurrence of the text.

**Exact position with `<HERE>` marker**:

```bash
lsp hover app.py --find "user<HERE>.name"
lsp definition main.py --find "calculate<HERE>(x, y)"
```

The `<HERE>` marker indicates cursor position for symbol resolution. Useful when multiple symbols share the same name.

#### Combining `--scope` and `--find`

**RECOMMENDED**: Combine both for precise targeting:

```bash
# Find symbol within a specific function
lsp reference main.py --scope MyClass.process --find "logger"

# Search within line range
lsp definition utils.py --scope 100,200 --find "validate"

# Find within symbol path
lsp hover models.py --scope User --find "email"
```

This narrows the search space, improving accuracy in large files.

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
# By symbol path (alias: lsp def)
lsp definition src/models.py --scope User.get_id

# By line and text
lsp definition src/main.py --scope 10 --find "process_data"

# Declaration instead of definition
lsp definition models.py --scope 25 --decl

# Type definition
lsp definition models.py --scope 30 --type
```

### Reference: Find All Usages

**REQUIRED** before refactoring or deleting code. Use `--impl` for finding implementations in abstract codebases.

```bash
# Find references (alias: lsp ref)
lsp reference src/main.py --scope MyClass.run --find "logger"

# Find implementations
lsp reference src/api.py --find "IDataProvider" --impl

# More context lines
lsp reference app.py --scope 10 --context-lines 5
```

### Search: Global Symbol Search

**RECOMMENDED** when symbol location is unknown. Use `--kind` to filter results.

```bash
# Search symbols (defaults to current directory)
lsp search "MyClassName"

# Specific workspace
lsp search "UserModel" --workspace /path/to/project

# Filter by kind
lsp search "init" --kind function --kind method

# Limit results
lsp search "Config" --max-items 10
```

### Symbol: Local Symbol Info

Get precise symbol location. **MAY** be used to anchor subsequent `hover` or `definition` calls.

```bash
# By line (alias: lsp sym)
lsp symbol src/main.py --scope 15

# By text search
lsp symbol utils.py --find "UserClass<HERE>"
```

### Hover: Get Documentation

**SHOULD** prefer over `read` for understanding API contracts. Returns docstrings and type signatures.

```bash
# By line
lsp hover src/main.py --scope 42

# By text search
lsp hover models.py --find "process_data<HERE>"

# Markdown output
lsp hover main.py --scope 10 --markdown
```

### Server: Manage Background Servers

Background manager starts automatically. Manual control is **OPTIONAL**.

```bash
# List running servers
lsp server list

# Start server
lsp server start <path>

# Stop server
lsp server stop <path>
```

## Best Practices

### General Workflows

#### Understanding Unfamiliar Code

**RECOMMENDED** sequence for exploring new codebases:

1. **Start with outline** - Get file structure without reading implementation

   ```bash
   lsp outline src/main.py
   ```

2. **Inspect signatures** - Use `hover` to understand API contracts

   ```bash
   lsp hover src/main.py --scope process_request
   ```

3. **Navigate dependencies** - Follow `definition` chains

   ```bash
   lsp definition src/main.py --scope 15 --find "validate"
   ```

4. **Map usage** - Find where code is called
   ```bash
   lsp reference src/validators.py --scope validate_input
   ```

#### Refactoring Preparation

**REQUIRED** steps before modifying code:

1. **Find all references** - Identify impact scope

   ```bash
   lsp reference models.py --scope User.email
   ```

2. **Check implementations** - For interfaces/abstract classes

   ```bash
   lsp reference interfaces.py --scope IRepository --impl
   ```

3. **Verify type definitions** - Understand type propagation
   ```bash
   lsp definition types.py --scope UserType --type
   ```

#### Debugging Unknown Behavior

When tracking down unexpected behavior:

1. **Search for the symbol** - Locate where it's defined

   ```bash
   lsp search "handle_error" --kind function
   ```

2. **Find the definition** - Verify implementation

   ```bash
   lsp definition app.py --find "handle_error<HERE>"
   ```

3. **Trace all callers** - See where it's invoked
   ```bash
   lsp reference app.py --scope handle_error --context-lines 5
   ```

### Performance Tips

- **Use `outline` aggressively** - Avoid reading entire files when possible
- **Combine `--scope` and `--find`** - Narrow search space in large files
- **Leverage symbol paths** - More precise than line numbers for nested structures
- **Use `--max-items`** - Limit results in large codebases
- **Prefer `hover` over `definition`** - For understanding without navigating

### Common Patterns

#### Finding Interface Implementations

```bash
# Step 1: Locate interface definition
lsp search "IUserService" --kind interface

# Step 2: Find all implementations
lsp reference src/interfaces.py --scope IUserService --impl
```

#### Tracing Data Flow

```bash
# Step 1: Find where data is created
lsp search "UserDTO" --kind class

# Step 2: Find where it's used
lsp reference models.py --scope UserDTO

# Step 3: Check transformations
lsp hover transform.py --scope map_to_dto
```

#### Understanding Type Hierarchies

```bash
# Step 1: Get class outline
lsp outline models.py --scope BaseModel

# Step 2: Find subclasses (references to base)
lsp reference models.py --scope BaseModel

# Step 3: Check type definitions
lsp definition models.py --scope BaseModel --type
```

### Domain-Specific Guides

For specialized scenarios, see:

- **Frontend**: [bp_frontend.md](references/bp_frontend.md)
- **Backend**: [bp_backend.md](references/bp_backend.md)
