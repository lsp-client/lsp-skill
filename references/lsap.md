# LSAP: Language Server Agent Protocol

**LSAP** (Language Server Agent Protocol) is a semantic abstraction layer designed to transform the **Language Server Protocol (LSP)** into an agent-native cognitive framework.

## Core Philosophy: Progressive Disclosure

Standard LSP is chatty and granular, optimized for IDEs updating as a user types. LSAP is optimized for LLM Agents, focusing on **Progressive Disclosure**:

1.  **Noise Reduction**: Delivers high-density "Cognitive Snapshots" instead of fragmented data.
2.  **Semantic Aggregation**: A single request (e.g., "Symbol Info") aggregates definition, signature, documentation, and implementation details.
3.  **Markdown-First**: Responses are formatted in Markdown, leveraging the LLM's natural ability to parse structured text.

## Key Concepts

### 1. The "Locate" Layer
Agents struggle with precise line/column coordinates (`line: 10, character: 15`), which are fragile and change with every edit.

LSAP introduces **LocateText** and **LocateSymbol**:
-   **LocateText**: Anchors a request to a unique text snippet (e.g., `find="class User"`) rather than just a coordinate.
-   **Heuristic Resolution**: Resolves ambiguous or approximate locations using fuzzy matching and AST context.

### 2. High-Density Snapshots
Instead of making five round-trips to get a function's details, LSAP returns a single **SymbolResponse** containing:
-   Full signature and type information.
-   Docstrings and comments.
-   The actual source code of the definition.
-   Related symbols.

### 3. Relational Graphs
For hierarchies (Call Hierarchy, Type Hierarchy), LSAP flattens the recursive tree into a relational graph, allowing the agent to see the full impact of a change in one view without manually expanding nodes.
