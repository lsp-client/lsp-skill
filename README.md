# LSP Analysis Skill

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/Protocol-v1.0.0--alpha-blue.svg)](references/lsap.md)

> IntelliSense for Agentic Coding

This [agent skill](https://agentskills.io) equips AI agents with the [Language Server Agent Protocol (LSAP)](https://github.com/lsp-client/LSAP), enabling them to navigate, understand, and analyze codebases with the same fidelity as a human developer using VS Code.

Instead of guessing file paths or grepping for text, agents using this skill can "jump to definition", "find references", and "inspect types" deterministically.

## ⚡ Capabilities

The `lsp-analysis` skill provides the following capabilities to the agent:

- **🗺 Symbol Outline**: Generate a high-level structural map of any file (classes, methods, variables).
- **🔍 Go to Definition**: Jump to the exact definition of a symbol, resolving imports and inheritance.
- **🔗 Find References**: Locate all usages of a function or class across the entire workspace.
- **📄 Hover & Docs**: Read docstrings, type signatures, and parameters for any symbol.
- **🔎 Workspace Search**: Fuzzy find symbols by name project-wide.

## 🚀 Getting Started

### Prerequisites

This skill requires the [lsp-cli](https://github.com/lsp-client/lsp-cli) tool to be installed in the environment where the agent runs.

```bash
uv tool install lsp-cli
```

> Actually you can skip this step since agent will do it for you 😉

### How it Works

This skill wraps the `lsp` command line tool, which acts as a bridge between the agent and standard Language Servers (like Pyright, tsserver, rust-analyzer).

When an agent invokes this skill:

1.  **Intelligent Locating**: The skill converts fuzzy intents (e.g., "find the `process` function") into precise file coordinates using LSAP's anchoring mechanism.
2.  **Server Management**: It automatically manages the lifecycle of background language servers.
3.  **Cognitive Snapshots**: It returns code context in optimized Markdown formats designed for LLM reasoning (Progressive Disclosure).

## 📚 Documentation

- **[Best Practices Index](references/bp.md)**: Decision tree to find the right guide for your task.
- **[LSAP Protocol](references/lsap.md)**: The underlying protocol design.

## 🔌 Extensible Best Practices

This skill uses a modular best practices system that can be extended for specific languages, frameworks, or workflows.

```
references/
├── bp.md                          # Index with decision tree
├── bp_<category>.md               # Category guides (explore, modify, troubleshoot)
├── bp_<category>_<scenario>.md    # Specific scenarios
└── bp_<lang>_<domain>.md          # Language/domain specific
```

**Add your own**:

```bash
just new-bp python django          # -> bp_python_django.md
just new-bp modify api-migration   # -> bp_modify_api-migration.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📦 Components

This repository is a self-contained Agent Skill that bundles:

- **Skill Definition**: [SKILL.md](SKILL.md)
- **Protocol Specs**: [LSAP Reference](lib-references/LSAP/)
- **CLI Engine Docs**: [lsp-cli Reference](lib-references/lsp-cli/)
