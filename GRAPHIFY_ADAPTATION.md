# Graphify adaptation map

This file records which Graphify v8 ideas are deliberately reused in StoryGraph and which code-specific parts are not carried over.

## Reused/adapted foundation

- `graphify/validate.py` -> `storygraph/validate.py`: validate untrusted extracted data before adding it to the graph; keep the same confidence vocabulary: `EXTRACTED`, `INFERRED`, `AMBIGUOUS`.
- `graphify/build.py` -> `storygraph/core.py`: assemble plain node/edge dictionaries into a NetworkX graph and preserve graph data in a stable JSON form. StoryGraph uses `MultiDiGraph` because stories can have several relationships between the same two entities and those relationships can later change over time.
- `graphify/paths.py` pattern -> `storygraph/paths.py`: keep output locations centralized and predictable.
- Graphify query/path pattern -> `neighbors()` and `shortest_path()` in `storygraph/core.py`: query a small relevant subgraph instead of rereading everything.
- Graphify export boundary -> `storygraph/export.py`: graph persistence/export is separate from graph construction so later HTML/report exporters can be added without changing the core data model.
- Graphify's deterministic test philosophy -> `tests/`: graph building and validation are tested without network calls or an LLM.

## Deliberately not copied

- Tree-sitter language parsers and code extractors.
- Programming-language symbol resolution, imports, inheritance, call graphs, SQL/Terraform/code-specific logic.
- PR impact analysis, repository call-flow pages, and other source-code-only features.
- Graphify's large CLI surface.
- Any hosted database requirement.

## Why

Graphify's strongest reusable idea for this project is the pipeline boundary: validate structured facts, build a graph, query a relevant part of the graph, and export it for agents/humans. The code-specific parsers are excellent for source code but do not help a novel. Story understanding will be added as a separate narrative extraction layer in later phases.

Upstream project: https://github.com/Graphify-Labs/graphify
Upstream branch studied: `v8`
