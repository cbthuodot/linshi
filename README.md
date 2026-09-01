# StoryGraph

StoryGraph is a novel/story relationship-graph tool adapted from reusable architecture ideas in Graphify.

The project is being rebuilt in phases. The current development branch contains the Phase 1 foundation: validated node/relationship input, a stable JSON graph format, multiple relationships between the same entities, basic relationship queries, and path finding.

## Install for development

```bash
pip install -e .
storygraph init
```

If the machine is offline but already has the build dependencies installed, use:

```bash
pip install -e . --no-build-isolation
```

## Current Phase 1 commands

```bash
storygraph init
storygraph add fragment.json
storygraph query "林夏"
storygraph path "林夏" "银色钥匙"
```

The graph is stored at `storygraph-out/graph.json` by default.

Novel-specific time/history, aliases, secrets, foreshadowing, consistency checks, interactive visualization, automatic chapter updating, and final Codex/OpenCode/ZCode packaging are added in later phases defined in `DEVELOPMENT_PLAN.md`.

See `GRAPHIFY_ADAPTATION.md` for exactly which Graphify ideas are reused and which code-specific parts are deliberately not copied. See `NOTICE` for upstream attribution.
