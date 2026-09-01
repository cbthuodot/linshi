# StoryGraph Rebuild Plan

This is the fixed execution plan for turning Graphify's strongest reusable ideas into a novel-oriented tool. Work stops after every phase and continues only after the user says to continue.

## Goal

Build a local, installable tool for Codex, OpenCode, and ZCode that turns novel chapters and story notes into a queryable story relationship graph while keeping the original prose as the source of truth.

## Core rule

Do not blindly rewrite Graphify from scratch and do not blindly copy everything. Reuse/adapt the parts that are already strong and general: graph construction, validation, confidence labels, clustering, graph analysis, JSON/HTML export, incremental updates, query/path operations, and agent integration patterns. Replace code-only parsing and code-only concepts with novel understanding.

## Phase 0 — Lock the plan

Write this plan, create a separate development branch, preserve the upstream license/attribution, and define what counts as finished.

Status: DONE.

STOP after this phase and wait for user approval.

## Phase 1 — Build the Graphify-based foundation

Study and map the exact Graphify modules we want to reuse. Bring/adapt only the reusable graph foundation into StoryGraph. Make the project installable and keep the graph output format stable.

Verification: install locally, create an empty graph, add a few hand-written entities/relations, query them, and run basic tests.

Status: DONE.

Result: StoryGraph now has validate-before-build input checks, a versioned JSON graph format, a NetworkX MultiDiGraph foundation that preserves multiple relationships, basic neighbor/path queries, centralized output paths, installable package metadata, upstream licensing/attribution, and regression tests. Local verification passed 5 tests plus a manual three-entity smoke test. See `GRAPHIFY_ADAPTATION.md` and `PHASE1_VERIFICATION.md`.

STOP here until the user approves Phase 2.

## Phase 2 — Make the graph understand stories

Define the novel model: characters, events, places, organizations, objects, secrets, clues, foreshadowing, goals, beliefs, conflicts, chapters/scenes, and changing relationships.

Add time/history fields so old relationships are preserved instead of overwritten. Add aliases so one character is not duplicated because of nicknames. Add source/evidence information and confidence labels.

Verification: use three hand-written chapters and confirm changing relationships, object ownership, aliases, and story order are represented correctly.

Status: DONE.

Result: StoryGraph now has a narrative entity/relation model, conservative alias merging, chapter/time validity fields, source/evidence tracking, alias-aware lookup, ordered relationship history, and schema version 2. Verification used three fixed Chinese chapters and passed 12 automated tests. It correctly merged 林夏/小夏, preserved distrust→trust history, preserved the silver key's ownership change, and retained evidence through save/load. See `PHASE2_VERIFICATION.md`.

STOP here until the user approves Phase 3.

## Phase 3 — Make AI read chapters into the graph

Create the strict novel-reading instructions used by Codex/OpenCode/ZCode. The AI must read a chapter, identify supported facts, and write them into the graph while marking explicit facts, reasonable interpretations, and uncertainty separately.

Track especially: who knows which secret and when, relationship changes, clues, foreshadowing, and payoff.

Verification: feed the fixed three-chapter Chinese test story and compare the produced graph against an expected answer prepared in the tests.

Status: DONE.

Result: StoryGraph now ships a grounded chapter-reading workflow for coding agents, separate extraction/model references, and `validate-chapter` / `add-chapter` commands. Every written relationship must carry source chapter information and an evidence passage present in the original chapter. The fixed three-chapter Chinese fixture covers aliases, secret knowledge changes, clues/foreshadowing, and payoff. Local smoke verification confirmed alias remapping, `does_not_know`→`learns`/`knows` history, payoff tracking, and rejection of fake evidence, wrong chapter numbers, wrong source files, and missing evidence. The skill bundle itself also passed validation and packaged successfully. See `PHASE3_VERIFICATION.md`.

STOP here until the user approves Phase 4.

## Phase 4 — Add novel reasoning and consistency checks

Add queries for: who knows what at a given chapter, how two characters are connected, timeline/history, unresolved foreshadowing, current ownership/location, and important story groups.

Add checks for obvious contradictions, character knowledge leaks, impossible ownership/location conflicts when evidence is strong, and forgotten foreshadowing.

Verification: deliberately plant errors in the test novel and require StoryGraph to detect them without falsely flagging the correct cases.

STOP and report what it catches and what it cannot reliably catch.

## Phase 5 — Add updates, visual graph, and reports

When one chapter changes, replace only facts sourced from that chapter instead of rebuilding/corrupting everything. Generate `graph.json`, a clickable `graph.html`, and `STORY_REPORT.md`.

Verification: edit chapter 2, update the graph, confirm chapters 1 and 3 remain correct, then inspect the generated outputs.

STOP and report results.

## Phase 6 — Package for Codex / OpenCode / ZCode and final verification

Finish the install instructions and reusable agent skill/instructions. Make the normal workflow simple: read/update chapters, query story memory, check consistency, then write/analyze.

Final verification must pass all of these:

- ingest at least three Chinese chapters;
- recurring characters are not duplicated unnecessarily;
- changing relationships keep their history;
- multi-hop relationship questions work;
- the system can answer who knows a secret at a chosen point in the story;
- an intentionally planted continuity error is detected;
- a clue planted in chapter 1 and paid off in chapter 3 is tracked;
- `graph.json`, `graph.html`, and `STORY_REPORT.md` are generated;
- editing one chapter does not corrupt facts from other chapters;
- automated tests pass;
- installation/use instructions work for the target agents.

Only after all verification passes is v1 considered complete.

## Non-goals for v1

Do not attempt perfect literary interpretation. Do not replace the novel with summaries. Do not hide uncertainty. Do not add a hosted database unless it becomes genuinely necessary. Do not claim completion just because the demo looks good; the verification cases above must pass.
