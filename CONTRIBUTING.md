# Contribution Guide

## Core Principles

- **Conciseness**: Only add what an LLM agent needs. Avoid fluff.
- **LSAP Alignment**: Follow Language Server Agent Protocol principles (progressive disclosure, high-density context).
- **Verification**: Test CLI commands before documenting them.

## Best Practices Structure

Best practices are organized in `skills/lsp-code-analysis/references/` with hierarchical naming:

```
skills/lsp-code-analysis/references/
├── bp_<category>.md               # Category guides (explore, modify, troubleshoot)
├── bp_<category>_<scenario>.md    # Specific scenarios
└── bp_<lang>_<domain>.md          # Language/domain specific
```

### Naming Convention

| Pattern                       | Use Case                    | Example                                         |
| ----------------------------- | --------------------------- | ----------------------------------------------- |
| `bp_<category>.md`            | General category guide      | `bp_explore.md`                                 |
| `bp_<category>_<scenario>.md` | Specific scenario           | `bp_modify_refactor.md`                         |
| `bp_<lang>_<domain>.md`       | Language or domain specific | `bp_python_django.md`, `bp_typescript_react.md` |

### Adding a New Best Practice

```bash
# Initialize from template
just new-bp <category> [scenario]

# Examples:
just new-bp explore                  # -> bp_explore.md
just new-bp modify api-migration     # -> bp_modify_api-migration.md
just new-bp python django            # -> bp_python_django.md
```

Then add an entry to the appropriate table in `skills/lsp-code-analysis/SKILL.md` or domain indices.

### Current Categories

- `explore` — Understanding/navigating code
- `modify` — Changing/refactoring code
- `troubleshoot` — Fixing LSP issues

## Adding Reference Material

For complex capabilities (e.g., `call-hierarchy`):

1. Create `skills/lsp-code-analysis/references/<capability>.md`
2. Link from `SKILL.md` if it's a core feature

## Testing Changes

1. Verify `lsp` commands work as described
2. Repackage: `just package`
