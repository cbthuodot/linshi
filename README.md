# StoryGraph

StoryGraph is an experimental novel/story knowledge-graph tool adapted from the architecture and ideas of Graphify.

It turns story material into a relationship map that AI agents can query. Instead of functions and classes, it focuses on characters, events, locations, objects, organizations, secrets, clues, foreshadowing, goals, beliefs, and chapters.

## Install

```bash
pip install -e .
storygraph init
```

The repository includes an agent skill at `.agents/skills/storygraph/SKILL.md`. Codex/OpenCode-compatible agents can use that workflow to read chapters and turn story facts into graph fragments.

## Basic use

After an agent has extracted a chapter fragment:

```bash
storygraph add chapter-fragment.json
storygraph query "林夏"
storygraph path "林夏" "银色钥匙"
storygraph check
storygraph export
```

`storygraph export` creates `storygraph-out/graph.html`, an interactive relationship map.

The first version deliberately keeps the original prose and the graph separate: the graph stores story logic and relationships, while the original chapters remain the source for exact wording, style, and nuance.

## Status

This is an early novel-oriented adaptation, not yet a finished replacement for Graphify. The current version has the graph core, relationship queries, path finding, basic consistency checks, interactive graph export, and the novel extraction workflow. The next work is stronger time-aware relationship handling, character knowledge boundaries, foreshadowing tracking, and automatic chapter update handling.

See `NOTICE` for upstream attribution.
