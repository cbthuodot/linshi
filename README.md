# StoryGraph

StoryGraph is a local novel/story relationship-graph tool adapted from reusable architecture ideas in Graphify.

Phase 5 is complete on the development branch. StoryGraph can ingest grounded chapter facts, track aliases and changing relationships, reason about story-time state, check strong continuity conflicts, safely replace one tracked chapter, and export a clickable relationship map plus a story status report.

## Install for development

```bash
pip install -e .
storygraph init
```

If the machine is offline but already has the build dependencies installed:

```bash
pip install -e . --no-build-isolation
```

## Normal chapter workflow

```bash
storygraph validate-chapter chapters/001.md fragment.json --index 1 --label "第1章"
storygraph add-chapter chapters/001.md fragment.json --index 1 --label "第1章"
```

`add-chapter` stores the grounded chapter fragment and a SHA-256 file fingerprint so the chapter can be replaced safely later.

After editing an already tracked chapter, extract a new fragment and run:

```bash
storygraph update-chapter chapters/002.md fragment-v2.json --index 2 --label "第2章"
```

StoryGraph replaces that chapter's cached fragment, then reconstructs a candidate graph from the cached validated fragments. It does not reread unchanged chapter prose. If the replacement is invalid or breaks later cached facts, the saved graph and manifest are left unchanged.

## Story queries and checks

```bash
storygraph query "林夏"
storygraph path "林夏" "银色钥匙"
storygraph timeline "林夏"
storygraph knowledge "陈默" "白塔标记" --at 2
storygraph state "银色钥匙" --at 2
storygraph unresolved --at 20
storygraph groups
storygraph check
```

## Export

```bash
storygraph export
```

This creates:

- `storygraph-out/graph.json` — machine-readable story graph;
- `storygraph-out/graph.html` — self-contained clickable relationship map with search and node highlighting;
- `storygraph-out/STORY_REPORT.md` — deterministic story status report.

Use `storygraph report` when only the Markdown report is needed.

## Important rules

The original novel remains the source of truth. Chapter-derived relationships carry chapter/source information and evidence passages. Explicit facts, interpretations, and uncertainty remain separate, and reader knowledge is not automatically treated as character knowledge.

Safe chapter replacement requires the Phase 5 tracked workflow. If an older graph contains untracked facts and no chapter manifest, StoryGraph refuses to guess which facts belong to which chapter. Create a fresh output folder and ingest the chapters with `add-chapter` before using `update-chapter`.

Current strong checks cover character knowledge leaks, explicit contradiction edges, simultaneous opposing relationships, multiple active owners, and multiple active locations. These are warnings to inspect against the prose, not automatic proof the author made a mistake.

The included StoryGraph skill lives at `.agents/skills/storygraph/`. Final Codex/OpenCode/ZCode packaging and end-to-end agent installation are Phase 6.

See `DEVELOPMENT_PLAN.md` for the phase plan, `PHASE5_VERIFICATION.md` for verification results, `GRAPHIFY_ADAPTATION.md` for which Graphify ideas are reused, and `NOTICE` for upstream attribution.
