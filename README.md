# LSP Analysis Skill

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/Protocol-v1.0.0--alpha-blue.svg)](references/lsap.md)

> IntelliSense Designed for Coding Agent

This [agent skill](https://agentskills.io) equips AI agents with the [Language Server Agent Protocol (LSAP)](https://github.com/lsp-client/LSAP), enabling them to navigate, understand, and analyze codebases with the same fidelity as a human developer using VS Code.

Instead of guessing file paths or grepping for text, agents using this skill can "jump to definition", "find references", and "inspect types" deterministically.

## ⚡ Capabilities

The [`lsp-code-analysis`](skills/lsp-code-analysis/SKILL.md) skill provides **compiler-accurate** code understanding that surpasses text-based search:

- **🔍 Semantic Navigation**: Jump to definitions, find references, locate implementations - understands code structure, not just text patterns.
- **🏷️ Language-Aware**: Distinguishes between variables, functions, classes, types - eliminates false positives from text search.
- **🔗 Cross-File Intelligence**: Trace dependencies, refactor safely across entire codebase - knows what imports what.
- **📘 Type-Aware**: Get precise type information, signatures, documentation - without reading implementation code.
- **🗺️ Symbol Outline**: Generate high-level structural maps of files to understand code without reading full implementations.

**Use cases**: Exploring unfamiliar code, refactoring, debugging, understanding dependencies. **Prefer over grep/text search** when you need to understand how code works, not just where text appears.

## 🚀 Getting Started

### Prerequisites

This skill requires the [lsp-cli](https://github.com/lsp-client/lsp-cli) tool to be installed in the environment where the agent runs.

```bash
uv tool install --python 3.13 lsp-cli
```

> Actually you can skip this step since agent will do it for you 😉

### How it Works

This skill wraps the `lsp` command line tool, which acts as a bridge between the agent and standard Language Servers (like Pyright, tsserver, rust-analyzer).

When an agent invokes this skill:

1.  **Intelligent Locating**: The skill converts fuzzy intents (e.g., "find the `process` function") into precise file coordinates using LSAP's anchoring mechanism.
2.  **Server Management**: It automatically manages the lifecycle of background language servers.
3.  **Cognitive Snapshots**: It returns code context in optimized Markdown formats designed for LLM reasoning (Progressive Disclosure).

## 📚 Documentation

- **[Skill Reference](skills/lsp-code-analysis/SKILL.md)**: Complete command reference and best practices.
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

The underlying [lsp-client](https://github.com/lsp-client/lsp-client) library continuously expands support for more language servers and LSP protocol capabilities:

- **Broader Language Server Support**: Currently supports Python, Rust, TypeScript, Go, etc., with continuous additions for more language ecosystems
- **Full LSP 3.17 Specification Coverage**: As the LSP protocol evolves, new standard capabilities (Type Hierarchy, Call Hierarchy, Inline Values, etc.) will be continuously integrated

### 2. Tool Capability Expansion - LSAP Protocol

The [LSAP (Language Server Agent Protocol)](https://github.com/lsp-client/LSAP) continuously designs and releases new composed capabilities:

- **Advanced Analysis Capabilities**: Upcoming Relation API, Impact Analysis, Code Map, and more
- **Optimized Output Formats**: Continuously improving Markdown rendering templates using the Progressive Disclosure principle, providing code context better suited for LLM reasoning

### 3. Scenario Coverage Expansion - Best Practice System

This skill adopts a modular [Best Practice system](https://github.com/lsp-client/lsp-skill/blob/main/skills/lsp-code-analysis/SKILL.md#best-practices), enabling community contributions of domain-specific workflows:

- **Domain Expert Knowledge**: Specialized workflows for different domains including Frontend ([bp_frontend.md](https://github.com/lsp-client/lsp-skill/blob/main/skills/lsp-code-analysis/references/bp_frontend.md)), Backend ([bp_backend.md](https://github.com/lsp-client/lsp-skill/blob/main/skills/lsp-code-analysis/references/bp_backend.md)), and more
- **Framework/Language Specialization**: Customized LSP usage guides can be added for specific tech stacks (e.g., Django, React, FastAPI)

These three layers of extensibility work together: the **foundation** provides raw tool materials, **composed capabilities** design efficient tool combinations, and **best practices** apply these tools to concrete scenarios. As all three continue to evolve, this skill will become increasingly powerful and user-friendly.

## 📦 Components

This repository is a self-contained Agent Skill that bundles:

- **Skill Definition**: [skills/lsp-code-analysis/SKILL.md](skills/lsp-code-analysis/SKILL.md)
- **Best Practice Guides**: [skills/lsp-code-analysis/references/](skills/lsp-code-analysis/references/)
- **Protocol Specs**: [LSAP Reference](lib-references/LSAP/)
- **CLI Engine Docs**: [lsp-cli Reference](lib-references/lsp-cli/)
