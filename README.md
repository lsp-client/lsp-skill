# LSP Analysis Skill

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/Protocol-v1.0.0--alpha-blue.svg)](references/lsap.md)

> _IntelliSense Designed for Coding Agent_
>
> Check our [website](https://lsp-client.github.io)!

This [agent skill](https://agentskills.io) equips AI agents with the [Language Server Agent Protocol (LSAP)](https://github.com/lsp-client/LSAP), enabling them to navigate, understand, and analyze codebases with the same fidelity as a human developer using VS Code.

## 📦 Installation

😎 Copy the following prompt to your agent and let it do all the heavy lifting for you:

````markdown
Please follow these steps to install this skill:

1. Identify what AI agent tool you are (e.g., Claude Code, Gemini, Codex, OpenCode, etc.).
2. Determine the correct installation directory for your tool:
   - Claude Code: `~/.claude/skills/`
   - Gemini: `~/.gemini/skills/`
   - Codex: `~/.codex/skills/`
   - OpenCode: `~/.config/opencode/skill/`
   - Other tools:
     1. Search online to determine if your tool supports agent skills from `agentskills.io`.
     2. If supported, check your tool's documentation to get the skill directory.
3. Download the latest release and unzip it into that directory.

   For example, if you are Claude Code:

   ```bash
   # Create directory if it doesn't exist
   mkdir -p ~/.claude/skills/lsp-code-analysis

    # Download and unzip the latest release
    TMP_DIR=$(mktemp -d)
    curl -sSL https://github.com/lsp-client/lsp-skill/releases/latest/download/lsp-code-analysis.zip -o "$TMP_DIR/lsp-code-analysis.zip"
    unzip -o "$TMP_DIR/lsp-code-analysis.zip" -d ~/.claude/skills/
    rm -rf "$TMP_DIR"
   ```
````

### Manual Installation

You can also use [skills](https://skills.sh/) for easy installation:

```bash
npx skills add lsp-client/lsp-skill
```

## ⚡ Capabilities

The [`lsp-code-analysis`](skills/lsp-code-analysis/SKILL.md) skill provides **compiler-accurate** code understanding that surpasses text-based search:

- **🔍 Semantic Navigation**: Jump to definitions, find references, locate implementations - understands code structure, not just text patterns.
- **🏷️ Language-Aware**: Distinguishes between variables, functions, classes, types - eliminates false positives from text search.
- **🔗 Cross-File Intelligence**: Trace dependencies, refactor safely across entire codebase - knows what imports what.
- **📘 Type-Aware**: Get precise type information, signatures, documentation - without reading implementation code.
- **🗺️ Symbol Outline**: Generate high-level structural maps of files to understand code without reading full implementations.

## 🚀 Getting Started

### How it Works

This skill wraps the `lsp` command line tool, which acts as a bridge between the agent and standard Language Servers (like `basedpyright`, ``typescript-language-server`, `rust-analyzer`).

When an agent invokes this skill:

1.  **Intelligent Locating**: The skill converts fuzzy intents (e.g., "find the `process` function") into precise file coordinates using LSAP's anchoring mechanism.
2.  **Server Management**: It automatically manages the lifecycle of background language servers.
3.  **Cognitive Snapshots**: It returns code context in optimized Markdown formats designed for LLM reasoning (Progressive Disclosure).

## 🌐 Supported Languages

This skill currently provides out-of-the-box support for the following languages:

| Language                    | Language Server                                                                                        |
| :-------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Python**                  | [basedpyright](https://github.com/detachhead/basedpyright)                                             |
| **Rust**                    | [rust-analyzer](https://rust-analyzer.github.io/)                                                      |
| **TypeScript / JavaScript** | [typescript-language-server](https://github.com/typescript-language-server/typescript-language-server) |
| **Go**                      | [gopls](https://pkg.go.dev/golang.org/x/tools/gopls)                                                   |
| **Deno**                    | [deno lsp](https://deno.land/)                                                                         |
| **Java**                    | [jdtls](https://github.com/eclipse/eclipse.jdt.ls)                                                     |

_More language support coming very very soon!_

## 📚 Documentation

- **[Skill Reference](skills/lsp-code-analysis/SKILL.md)**: Complete command reference and best practices.
- **[Configuration Guide](skills/lsp-code-analysis/references/configuration.md)**: Customizing `lsp-cli` settings and environment variables.
- **[Frontend Best Practices](skills/lsp-code-analysis/references/bp_frontend.md)**: LSP workflows for frontend development.
- **[Backend Best Practices](skills/lsp-code-analysis/references/bp_backend.md)**: LSP workflows for backend development.

## 🔌 Extensible Best Practices

This skill uses a modular best practices system that can be extended for specific languages, frameworks, or workflows.

```
skills/lsp-code-analysis/references/
├── bp_frontend.md                 # Frontend development workflows
├── bp_backend.md                  # Backend development workflows
└── bp_<category>_<scenario>.md    # Custom domain-specific guides
```

**Add your own**:

```bash
just new-bp python django          # -> bp_python_django.md
just new-bp modify api-migration   # -> bp_modify_api-migration.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 🔄 Extensibility

This Agent Skill features a three-tier extensibility design that ensures its capabilities will continue to grow:

### 1. Foundation Expansion - LSP Client

The underlying [lsp-client](https://github.com/lsp-client/lsp-client) library continuously expands support for more language servers and LSP protocol capabilities.

- **Full LSP 3.17 Specification Coverage**: As the LSP protocol evolves, new standard capabilities (Type Hierarchy, Call Hierarchy, Inline Values, etc.) will be continuously integrated

### 2. Tool Capability Expansion - LSP CLI & LSAP Protocol

The integrated **LSP CLI** implements the [LSAP (Language Server Agent Protocol)](https://github.com/lsp-client/LSAP) to provide high-level, agent-optimized capabilities:

- **Advanced Analysis Capabilities**: Upcoming Relation API, Impact Analysis, Code Map, and more
- **Optimized Output Formats**: Continuously improving Markdown rendering templates using the Progressive Disclosure principle, providing code context better suited for LLM reasoning

### 3. Scenario Coverage Expansion - Best Practice System

This skill adopts a modular [Best Practice system](https://github.com/lsp-client/lsp-skill/blob/main/skills/lsp-code-analysis/SKILL.md#best-practices), enabling community contributions of domain-specific workflows:

- **Domain Expert Knowledge**: Specialized workflows for different domains including Frontend ([bp_frontend.md](skills/lsp-code-analysis/references/bp_frontend.md)), Backend ([bp_backend.md](skills/lsp-code-analysis/references/bp_backend.md)), and more
- **Framework/Language Specialization**: Customized LSP usage guides can be added for specific tech stacks (e.g., Django, React, FastAPI)

These three layers of extensibility work together: the **foundation** provides raw tool materials, **composed capabilities** design efficient tool combinations, and **best practices** apply these tools to concrete scenarios. As all three continue to evolve, this skill will become increasingly powerful and user-friendly.

## 📦 Components

This repository is a self-contained Agent Skill that bundles:

- **Skill Definition**: [skills/lsp-code-analysis/SKILL.md](skills/lsp-code-analysis/SKILL.md)
- **Best Practice Guides**: [skills/lsp-code-analysis/references/](skills/lsp-code-analysis/references/)
- **Protocol Specs**: [LSAP Reference](lib-references/LSAP/)
