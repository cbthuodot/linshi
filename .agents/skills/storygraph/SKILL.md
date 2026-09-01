---
name: storygraph
description: Read novel chapters and story notes, extract grounded characters/events/locations/objects/secrets/clues/foreshadowing and relationships, then maintain and query StoryGraph. Use for long-form fiction memory, relationship tracing, chapter ingestion, timeline reasoning, continuity preparation, secret/knowledge tracking, and gathering established story context before analysis or writing.
---

# StoryGraph workflow

Treat the original novel as the source of truth and the graph as structured story memory. Never replace exact prose, tone, or nuance with graph summaries.

For chapter extraction, read `references/extraction-spec.md`. For entity/relation choices, read `references/story-model.md` only when needed.

## Read a chapter into StoryGraph

Read the whole chapter before extracting facts.

Inspect the existing graph when relevant so recurring entities use stable identities. Preserve nicknames and alternate names as aliases rather than creating duplicate characters.

Extract only story facts supported by the chapter. Keep reader knowledge separate from character knowledge. Preserve old relationship states when a relationship changes.

Attach a short verbatim evidence passage to every relationship. Mark direct facts `EXTRACTED`, strong interpretations `INFERRED`, and unresolved interpretations `AMBIGUOUS`.

Write the candidate fragment to JSON, then run:

`storygraph validate-chapter <chapter-file> <fragment.json> --index <N> --label <chapter-label>`

Fix any validation error. Do not bypass the evidence/source checks.

After validation succeeds, run:

`storygraph add-chapter <chapter-file> <fragment.json> --index <N> --label <chapter-label>`

Query the affected characters/objects afterward to make sure the resulting relationships look consistent with the chapter.

## Answer story questions

Query the graph first for structural facts and relationship paths. Read the cited source chapter when exact wording, literary nuance, or an important disputed detail matters.

Use:

`storygraph query "<entity>"`

`storygraph path "<entity A>" "<entity B>"`

Never present an `INFERRED` or `AMBIGUOUS` relationship as if the novel stated it explicitly.
