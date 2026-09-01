---
name: storygraph
description: Read novels and story notes, extract characters/events/locations/objects/secrets/clues/foreshadowing and their relationships, then maintain and query storygraph-out/graph.json. Use for novel understanding, continuity checking, relationship tracing, timeline reasoning, and preparing context before writing new chapters.
---

# StoryGraph novel workflow

When working on a novel, treat the story graph as a second memory beside the original prose. Never replace the prose with the graph.

Before writing or answering a story question, query the graph when relevant, then read the exact source chapter for important details.

When a chapter is added or changed, read it carefully and extract a JSON fragment containing only information supported by the text.

Use these node types: character, location, organization, object, event, secret, clue, foreshadow, chapter, scene, rule, goal, belief, conflict, relationship, concept.

Prefer clear relations such as knows, does_not_know, loves, hates, trusts, distrusts, owns, gives_to, located_at, member_of, wants, fears, causes, witnesses, learns, reveals, hides_from, appears_in, foreshadows, pays_off, contradicts, occurs_before, occurs_after.

Every important relation should include the chapter and source file. If the text states it directly, use confidence EXTRACTED. If it is a reasonable interpretation, use INFERRED. If uncertain, use AMBIGUOUS rather than pretending certainty.

For secrets, track who knows them and when they learned them. For changing relationships, do not delete history; include chapter information so earlier and later states can both exist.

Write the extracted fragment to a temporary JSON file, then run:

`storygraph add <fragment.json>`

Useful commands:

`storygraph query "林夏"`

`storygraph path "林夏" "银色钥匙"`

`storygraph check`

Before continuing a chapter, first check the current characters, locations, important objects, secrets known by each present character, unresolved clues/foreshadowing, and recent relationship changes. If the proposed writing conflicts with established facts, tell the author before writing.

Fragment shape:

```json
{
  "nodes": [
    {"id": "character_林夏", "label": "林夏", "type": "character", "source_file": "chapters/012.md"},
    {"id": "object_银色钥匙", "label": "银色钥匙", "type": "object", "source_file": "chapters/012.md"}
  ],
  "edges": [
    {"source": "character_林夏", "target": "object_银色钥匙", "relation": "owns", "confidence": "EXTRACTED", "chapter": "第12章", "source_file": "chapters/012.md"}
  ]
}
```
