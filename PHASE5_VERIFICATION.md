# Phase 5 verification

Phase 5 scope: make tracked chapters safely replaceable, generate a self-contained clickable relationship map, and generate a deterministic story status report.

## What was added

- `storygraph add-chapter` now records each grounded chapter as a replayable cached fragment plus a SHA-256 file fingerprint in `storygraph-out/manifest.json`.
- `storygraph update-chapter` replaces one tracked chapter fragment, then rebuilds the candidate graph from cached validated fragments without rereading unchanged chapter prose.
- Nothing is committed if the replacement fragment is ungrounded or if replaying later cached chapters becomes invalid.
- `storygraph export` writes `graph.json`, a self-contained `graph.html`, and `STORY_REPORT.md`.
- `storygraph report` writes only the Markdown report.
- `graph.html` contains its data and JavaScript inline. It has no external script or stylesheet dependency and supports search, click-to-focus, relationship highlighting, aliases, and direct relationship details.
- `STORY_REPORT.md` summarizes node/edge counts, tracked chapters, unresolved clues/foreshadowing, strong consistency warnings, and connected story groups.

## Safe update verification

The Phase 5 test creates three Chinese chapters, ingests all three, edits chapter 2, and replaces only its cached fragment. It records the chapter-1 and chapter-3 edges before the update and compares them after the update.

Verified results:

- chapter 1 facts are unchanged;
- chapter 3 facts are unchanged;
- chapter 2 relation changes from `trusts` to `ally_of`;
- chapter 2 SHA-256 changes;
- the manifest still contains exactly three chapters;
- failed replacement with evidence not found in the chapter leaves both `graph.json` and `manifest.json` unchanged;
- all cached chapter fragments remain replayable JSON files.

## Export verification

Tests confirm that:

- the HTML contains the Chinese story nodes and the click-selection JavaScript;
- the HTML does not load external scripts or stylesheets;
- the report contains unresolved foreshadowing and consistency status;
- `export_all` creates all three required outputs.

## Full automated verification

GitHub Actions on Python 3.12 installed the current branch and ran the complete Phase 1-5 suite:

```text
31 passed in 0.23s
```

Workflow run for the successful Phase 5 head: `33495804586`.

## Important limitation

Safe chapter replacement requires chapters to have been ingested with the tracked Phase 5 `add-chapter` workflow. If an existing graph contains older untracked facts and no chapter manifest, StoryGraph refuses to pretend it can safely identify which facts belong to which chapter. The safe migration path is to create a fresh output folder and ingest the chapters with the tracked workflow.

The cached fragments avoid rereading unchanged prose, but the in-memory graph is deliberately reconstructed from those cached validated fragments during an update. This is safer than trying to surgically guess which merged node attributes came from the edited chapter.

Phase 5 is complete. Phase 6 performs final Codex/OpenCode/ZCode packaging, workflow instructions, and end-to-end verification.
