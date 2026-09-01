# StoryGraph Rebuild Plan

This file is the execution checklist for converting the current prototype into a novel-oriented adaptation that deliberately reuses the strongest general architecture ideas from Graphify while replacing code-specific extraction with story understanding.

## Goal

Build a local, installable tool for Codex/OpenCode/ZCode that turns novel chapters and story notes into a queryable story graph without losing the original prose.

The tool must support: characters, events, locations, organizations, objects, secrets, clues, foreshadowing, goals, beliefs, conflicts, chapters/scenes, relationships, timeline changes, and character knowledge boundaries.

## Approach

Do not copy the full Graphify repository blindly. Keep the original Apache-2.0 attribution, study Graphify v8 as the upstream reference, and selectively adapt the general parts that are useful for narrative graphs: graph construction, validation, confidence labels, clustering, graph analysis, JSON/HTML export, incremental updates, query/path operations, and agent integration patterns.

Replace code-only parsing and code-only concepts with a narrative extraction layer. Novel facts are not deterministic like code syntax, so every extracted relation must keep source evidence and a confidence label. The original prose remains the source of truth.

## Implementation order

1. Repository foundation
   - Preserve Apache-2.0 license and upstream attribution.
   - Rename/package the project as StoryGraph.
   - Keep output under `storygraph-out/`.

2. Stable narrative data model
   - Define supported node types and relation types.
   - Store source file, chapter, scene, evidence text/range when available, confidence, valid-from/valid-to, learned-at/revealed-at fields.
   - Support aliases so the same character is not duplicated because of nicknames.

3. Graph core
   - Build a directed multi-edge graph so the same two entities can have multiple changing relationships over time.
   - Deduplicate entities conservatively.
   - Preserve history instead of overwriting older relationships.
   - Add query, neighborhood, path, timeline, unresolved-foreshadowing, and character-knowledge queries.

4. Narrative extraction
   - Provide a strict extraction contract for AI agents reading chapters.
   - Extract only facts grounded in the chapter.
   - Separate explicit facts, reasonable inference, and uncertainty.
   - Track who knows a secret and from which chapter.
   - Track relationship/state changes over time.
   - Track foreshadowing placement and payoff.

5. Incremental updates
   - Re-read only changed chapter files where possible.
   - Remove/rebuild facts sourced from a changed chapter without deleting facts from other chapters.
   - Maintain a small source manifest/hash file.

6. Analysis
   - Detect obvious contradictions.
   - Detect character knowledge leaks.
   - Detect impossible ownership/location conflicts when evidence is strong.
   - Detect unresolved foreshadowing.
   - Identify central characters/events and tightly connected story groups.

7. Output
   - Export `graph.json` as the machine-readable source.
   - Export a self-contained interactive `graph.html` for human browsing.
   - Export a readable `STORY_REPORT.md` summary.

8. Agent integration
   - Ship a reusable skill/instruction file for Codex/OpenCode/ZCode.
   - Make the normal workflow: read chapter -> extract fragment -> add/update graph -> query before analysis/writing.
   - Keep commands simple: init, add/update, query, path, timeline, check, report, export.

9. Installation
   - Make `pip install -e .` work locally.
   - Provide a `storygraph` command.
   - Avoid requiring a hosted database for the first usable version.

## Definition of done

The first complete version is done only when all of these work on a small Chinese test novel:

- Ingest at least three chapters.
- Recognize recurring characters without duplicating them unnecessarily.
- Preserve changing relationships across chapters.
- Answer a multi-hop relationship question.
- Answer who knows a secret at a given point in the story.
- Report at least one intentionally planted continuity error.
- Track a planted foreshadowing clue and its later payoff.
- Generate `graph.json`, `graph.html`, and `STORY_REPORT.md`.
- Re-process one edited chapter without corrupting facts from the other chapters.
- Run unit tests successfully.

## Verification plan

Create a deterministic test fixture with three short Chinese chapters containing:

- two main characters and one secondary character;
- an object that changes owner;
- a secret learned at different times by different characters;
- a relationship that changes from distrust to trust;
- a clue planted in chapter 1 and paid off in chapter 3;
- one deliberate contradiction for the checker to catch.

Verify the graph contents directly, verify CLI output, verify incremental replacement by source chapter, and open/inspect the generated HTML structure. Run the full automated test suite after every major core change and once again before declaring completion.

## Non-goals for v1

Do not attempt perfect literary interpretation, automatic prose generation, or fully automatic extraction from every file format. Do not hide uncertainty. Do not replace the novel text with summaries. Do not introduce a server/database dependency unless required later.
