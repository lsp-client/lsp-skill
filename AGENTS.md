# AGENTS.md

## Common Tasks

### Adding a New Best Practice

1. Run `just new-bp <category> [scenario]` to create from template
2. Edit the generated file in `skills/lsp-code-analysis/references/`
3. Add entry to the appropriate index in `SKILL.md` or domain `bp_*.md` file
4. Verify naming follows convention in `CONTRIBUTING.md`

### Modifying SKILL.md

- **Adhere to RFC 2119**: Use standardized requirement levels (`MUST`, `SHOULD`, `RECOMMENDED`, etc.) to define operational boundaries for agents.
- **Verify via CLI**: ALWAYS run `lsp <cmd> --help` to verify command syntax, options, and aliases before updating. Never assume features exist without verification.
- **Show, Don't Tell**: Use bash examples with inline comments instead of bullet-point lists or verbose text descriptions. Agents learn better from concrete examples than abstract explanations.
- **Actionable Workflows**: Present workflows as sequential code blocks with clear step-by-step comments. Avoid verbose prose descriptions.
- **Keep it Minimal**: Move implementation details to `references/`. `SKILL.md` serves as the high-level semantic interface.
- **Frontmatter**: The `description` in frontmatter MUST contain all relevant trigger conditions for the skill.

### Modifying bp\_\*.md

- Keep agent-facing indices minimal
- Use tables for quick scanning
- Do not add developer instructions here (use CONTRIBUTING.md)

## Quality Checks

Before completing a contribution:

- [ ] CLI commands in examples are valid (`lsp <cmd> --help` to verify)
- [ ] New `bp_*.md` files follow `bp_template.md` structure
- [ ] No developer-facing content in agent-facing files
