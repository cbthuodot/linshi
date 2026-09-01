# Phase 1 verification

Phase 1 scope: establish the Graphify-based generic graph foundation only. Novel-specific time/history and automatic chapter reading belong to later phases.

## What was verified

Local verification used Python 3.13 with NetworkX 3.6.1 and pytest 9.0.2.

Because the verification container had no network access, editable installation was tested with the already-installed build tools using:

```bash
python -m pip install -e . --no-build-isolation
```

The package built and installed successfully as `storygraph-novel 0.2.0`.

Automated tests:

```text
5 passed in 0.16s
```

Manual smoke test:

```text
StoryGraph ready: test-out/graph.json
Added 3 nodes and 2 relations
林夏 --trusts--> 陈默 [EXTRACTED]
林夏 -> 陈默 -> 银色钥匙
stable-json-ok
```

The smoke test verified that an empty graph can be created, a hand-written fragment can be added, a direct relationship can be queried, a multi-hop path can be found, and the saved JSON contains schema version 1 with the expected nodes and edges.

## Tests included

- valid graph fragment can be added, saved, loaded, and round-tripped without changing its graph data;
- multiple relationships between the same pair of entities are preserved;
- an edge pointing to a nonexistent node is rejected;
- malformed fragments fail loudly instead of being silently skipped;
- confidence labels use the Graphify-style `EXTRACTED`, `INFERRED`, and `AMBIGUOUS` vocabulary.

## Not verified in Phase 1

Novel-specific aliases, timeline changes, secret knowledge, foreshadowing, automatic chapter extraction, consistency reasoning, incremental chapter updates, final HTML visualization, and final agent packaging are intentionally deferred to Phases 2-6.
