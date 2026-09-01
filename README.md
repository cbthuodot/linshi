# StoryGraph

StoryGraph is a novel/story relationship-graph tool adapted from reusable architecture ideas in Graphify.

The project is being rebuilt in phases. Phase 2 is now complete on the development branch: the graph can represent story-specific entities and relationships, preserve relationship history by chapter, merge explicit character aliases conservatively, and keep source/evidence information with facts.

## Install for development

```bash
pip install -e .
storygraph init
```

If the machine is offline but already has the build dependencies installed, use:

```bash
pip install -e . --no-build-isolation
```

## Current commands

```bash
storygraph init
storygraph add fragment.json
storygraph query "林夏"
storygraph path "林夏" "银色钥匙"
```

The graph is stored at `storygraph-out/graph.json` by default.

Phase 2 supports characters, locations, organizations, objects, events, secrets, clues, foreshadowing, chapters/scenes, rules, goals, beliefs, conflicts, and related story concepts. Relationships can carry chapter order, validity range, source file, evidence text, and confidence. Exact aliases such as `林夏` / `小夏` can resolve to one canonical character without fuzzy name guessing.

Automatic AI reading of chapter prose is intentionally not part of Phase 2. That is Phase 3: Codex/OpenCode/ZCode will read chapters and produce these story facts under strict extraction rules.

See `DEVELOPMENT_PLAN.md` for the phase plan, `PHASE2_VERIFICATION.md` for the Phase 2 test results, `GRAPHIFY_ADAPTATION.md` for which Graphify ideas are reused, and `NOTICE` for upstream attribution.
