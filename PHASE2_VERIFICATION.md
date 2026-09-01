# Phase 2 verification

Phase 2 scope: make the graph represent basic novel structure reliably before adding automatic AI chapter extraction.

## What Phase 2 added

- A fixed set of narrative entity types: characters, locations, organizations, objects, events, secrets, clues, foreshadowing, chapters, scenes, rules, goals, beliefs, conflicts, relationships, and concepts.
- A fixed vocabulary of common story relationships.
- Chapter order and relationship validity fields (`chapter_index`, `valid_from`, `valid_to`) so old states can remain in history.
- Source and evidence fields so a relationship can point back to the original chapter text.
- Conservative character alias merging. Exact names/aliases are matched only within the same entity type; no fuzzy name guessing is used.
- Alias-aware lookup, so querying an alias can find the canonical character.
- Story-history ordering for relationships around an entity.
- JSON schema version 2 while retaining basic loading support for schema version 1.

## Verification story

Three short Chinese chapter fixtures were added under `tests/fixtures/phase2_chapters/`.

The fixtures deliberately contain these changes:

- Chapter 1: 林夏 is also called 小夏, distrusts 陈默, and owns the silver key.
- Chapter 2: the text calls her 小夏, she begins to trust 陈默, and the silver key changes to 陈默's possession.
- Chapter 3: the text returns to the name 林夏 and places her at the old tower.

## Automated verification

The current Phase 2 source files were fetched from the GitHub development branch and reconstructed in the local verification workspace because that workspace could not resolve github.com directly.

Test result:

```text
12 passed in 0.16s
```

Verified cases include:

- the Phase 1 graph/query tests still pass;
- invalid graph input is still rejected;
- unsupported story entity/relation types are rejected;
- an impossible backwards validity range is rejected;
- 小夏 and 林夏 are merged into one canonical character;
- alias merging does not create extra character nodes;
- distrust in chapter 1 and trust in chapter 2 are both preserved;
- relationship history is returned in chapter order;
- the silver key's ownership history preserves 林夏 in chapter 1 and 陈默 from chapter 2;
- source-file and evidence text survive save/load round-tripping;
- the saved graph uses schema version 2.

Manual smoke output:

```text
alias2 character_lin
alias3 character_lin
characters [('character_chen', '陈默'), ('character_lin', '林夏')]
history [(1, 'distrusts', '林夏', '陈默'),
         (1, 'owns', '林夏', '银色钥匙'),
         (2, 'trusts', '林夏', '陈默'),
         (3, 'located_at', '林夏', '旧塔')]
owners [(1, 'character_lin', 1, 1),
        (2, 'character_chen', 2, None)]
```

## Deliberately deferred

Phase 2 does not make AI automatically read prose and decide these facts. The fixtures use hand-written graph fragments so the data model can be tested independently. Automatic chapter reading, secret-knowledge extraction, foreshadowing extraction, and extraction-accuracy testing belong to Phase 3.
