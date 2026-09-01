# StoryGraph

StoryGraph is a novel/story relationship-graph tool adapted from reusable architecture ideas in Graphify.

The project is being rebuilt in phases. Phase 3 is now complete on the development branch: coding agents can read chapters under a strict extraction workflow, attach source evidence to relationships, and validate the extraction against the original chapter before anything is written into the graph.

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
storygraph validate-chapter chapters/001.md fragment.json --index 1 --label "第1章"
storygraph add-chapter chapters/001.md fragment.json --index 1 --label "第1章"
storygraph query "林夏"
storygraph path "林夏" "银色钥匙"
```

The graph is stored at `storygraph-out/graph.json` by default.

Phase 3 keeps the original novel as the source of truth. Every chapter-derived relationship must carry its source chapter and a short evidence passage found in that chapter. The agent workflow separates explicit facts, reasonable interpretation, and uncertainty, and explicitly prevents reader knowledge from automatically becoming character knowledge.

The included StoryGraph skill lives at `.agents/skills/storygraph/`. Its detailed extraction rules are split into reference files so agents only load them when needed.

The current version already supports story entities, conservative aliases, changing relationships, secret/knowledge states, clues/foreshadowing, source evidence, and grounded chapter ingestion. Broader contradiction detection and story reasoning are Phase 4.

See `DEVELOPMENT_PLAN.md` for the phase plan, `PHASE3_VERIFICATION.md` for the current verification results, `GRAPHIFY_ADAPTATION.md` for which Graphify ideas are reused, and `NOTICE` for upstream attribution.
