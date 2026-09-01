# StoryGraph

StoryGraph is a novel/story relationship-graph tool adapted from reusable architecture ideas in Graphify.

The project is being rebuilt in phases. Phase 4 is complete on the development branch: coding agents can ingest grounded chapter facts, ask chapter-specific story questions, track unresolved foreshadowing, and run strong continuity checks without treating normal story changes as contradictions.

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
storygraph timeline "林夏"
storygraph knowledge "陈默" "白塔标记" --at 2
storygraph state "银色钥匙" --at 2
storygraph unresolved --at 20
storygraph groups
storygraph check
```

The graph is stored at `storygraph-out/graph.json` by default.

StoryGraph keeps the original novel as the source of truth. Chapter-derived relationships carry source chapter information and evidence passages. The agent workflow separates explicit facts, reasonable interpretation, and uncertainty, and keeps reader knowledge separate from character knowledge.

Phase 4 adds story-time reasoning. Later ownership/location/opposing relationship states normally supersede earlier open-ended states, so ordinary changes such as distrust -> trust, movement, and object transfer are not automatically reported as errors. Explicit overlapping states can still be flagged.

Current strong checks cover character knowledge leaks, explicit contradiction edges, simultaneous opposing relationships, multiple active owners, and multiple active locations. These are warnings to inspect against the original prose, not automatic proof the author made a mistake.

The included StoryGraph skill lives at `.agents/skills/storygraph/` and includes separate extraction, story-model, and reasoning references.

See `DEVELOPMENT_PLAN.md` for the phase plan, `PHASE4_VERIFICATION.md` for verification results, `GRAPHIFY_ADAPTATION.md` for which Graphify ideas are reused, and `NOTICE` for upstream attribution.
