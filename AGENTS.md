# AGENTS.md

## Project Structure

```
├── SKILL.md              # Skill definition (for agents using this skill)
├── CONTRIBUTING.md       # Contribution guide (for developers)
├── references/
│   ├── bp_*.md           # Domain indices and best practice guides
│   ├── bp_template.md    # Template for new best practices
│   └── lsap.md           # Protocol reference
└── justfile              # Developer commands
```

## Common Tasks

### Adding a New Best Practice

1. Run `just new-bp <category> [scenario]` to create from template
2. Edit the generated file in `references/`
3. Add entry to the appropriate index in `SKILL.md` or domain `bp_*.md` file
4. Verify naming follows convention in `CONTRIBUTING.md`

### Modifying SKILL.md

- Keep under 100 lines; move details to `references/`
- `description` in frontmatter must contain all trigger conditions

### Modifying bp_*.md

- Keep agent-facing indices minimal
- Use tables for quick scanning
- Do not add developer instructions here (use CONTRIBUTING.md)

## Quality Checks

Before completing a contribution:

- [ ] CLI commands in examples are valid (`lsp <cmd> --help` to verify)
- [ ] New `bp_*.md` files follow `bp_template.md` structure
- [ ] `references/bp.md` updated if adding new best practice (Note: Index is now in `SKILL.md`)
- [ ] No developer-facing content in agent-facing files
