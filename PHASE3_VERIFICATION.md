# Phase 3 verification

Phase 3 scope: make AI coding agents read novel chapters under a strict, grounded extraction contract before facts are written into StoryGraph.

## What was added

- A compact StoryGraph agent skill with separate extraction/model references.
- `storygraph validate-chapter` to check a candidate chapter extraction without writing it.
- `storygraph add-chapter` to validate against the original chapter and only then merge it into the graph.
- Every extracted relationship must carry chapter number, source file, and a short evidence passage found in the source chapter.
- The skill explicitly separates reader knowledge from character knowledge and requires uncertainty to remain marked as `INFERRED` or `AMBIGUOUS`.
- Fixed three-chapter Chinese fixtures cover aliases, a secret learned at different times, a clue/foreshadowing thread, and payoff.
- Expected extraction JSON is committed for all three fixture chapters.

## Verification performed

The updated skill bundle passed the Skill validator and packaged successfully as `skill.zip`.

The current branch's StoryGraph module contents were reconstructed in the local verification container because direct `git clone` access to GitHub was unavailable in that container. Python compilation succeeded.

A three-chapter smoke run then verified all of the following:

- an alternate name remaps to the existing character instead of creating a duplicate;
- a character can be explicitly `does_not_know` in chapter 1 and then `learns` / `knows` in chapter 2 without losing history;
- a foreshadowing node can receive a later `pays_off` relationship;
- evidence text that does not occur in the source chapter is rejected;
- a wrong chapter index is rejected;
- a wrong source file is rejected;
- a missing evidence quote is rejected.

Smoke output:

```text
phase3-smoke-ok
nodes 5
edges 6
alias-remap character_lin
knowledge-states [(1, 'does_not_know'), (2, 'knows'), (2, 'learns')]
payoffs [('foreshadow_map', 'secret_entrance')]
fake-evidence-rejected True
wrong-chapter-rejected True
wrong-source-rejected True
missing-evidence-rejected True
```

## Chinese fixture coverage

The committed Phase 3 Chinese fixture deliberately tests a nickname (`林夏` / `小夏`), a hidden white-tower mark, when `陈默` learns that information, repeated white-tower clues, and a chapter-3 payoff at a secret entrance. The expected extraction files define the intended graph result and are used by `tests/test_extraction.py`.

## Important limitation

Grounding checks prove that a cited evidence passage exists in the chapter. They do not mathematically prove that the AI interpreted that passage correctly. The skill therefore forbids unsupported certainty and keeps `EXTRACTED`, `INFERRED`, and `AMBIGUOUS` distinct. Broader contradiction/knowledge-leak reasoning is intentionally Phase 4 work.

Phase 3 is complete when used with the extraction contract above. Phase 4 adds story reasoning and consistency checks on top of these grounded facts.
