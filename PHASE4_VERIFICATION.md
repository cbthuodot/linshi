# Phase 4 verification

Phase 4 scope: add story-time reasoning, current-state queries, unresolved foreshadowing checks, story-group discovery, and strong continuity warnings on top of the grounded graph from Phase 3.

## What was added

- `storygraph timeline <entity>` for relationship history in chapter order.
- `storygraph knowledge <character> <secret> --at <chapter>` for character knowledge state at a chosen point.
- `storygraph state <entity> --at <chapter>` for effective relationships at that point in the story.
- `storygraph unresolved --at <chapter>` for clues/foreshadowing that have not yet paid off.
- `storygraph groups` for graph-based story communities and central entities.
- `storygraph check` for strong consistency warnings.

Current strong checks cover:

- a character revealing a secret before being recorded as learning/knowing it;
- explicit `contradicts` relations;
- simultaneous opposing relationships with overlapping validity;
- an object having multiple active owners at the same point;
- a character having multiple active locations at the same point.

## Transition handling

A later ownership, location, or opposing relationship state normally supersedes an earlier open-ended state. This avoids false warnings for normal story development such as distrust -> trust, moving from one location to another, or an object changing hands.

If the earlier state has an explicit overlapping `valid_to`, the overlap remains authoritative and can be reported as a conflict. Same-chapter competing ownership/location claims are also reported.

## Verification performed

The full reconstructed test suite covering Phases 1-4 passed:

```text
25 passed in 0.17s
```

The Phase 4 tests deliberately planted all of these errors and confirmed they are detected:

- knowledge leak;
- overlapping ownership conflict;
- same-time location conflict;
- overlapping trust/distrust conflict.

Separate tests confirmed that normal open-ended transitions do not create false conflicts.

A regression run on the fixed three-chapter Chinese story produced:

```text
issues= []
chen1= does_not_know
chen2= knows
unresolved2= ['旧地图上的白塔标记', '旧塔门框上的白塔标记']
unresolved3= []
lin2= [('knows', '银色钥匙背面的白塔标记'), ('learns', '银色钥匙背面的白塔标记'), ('located_at', '城北旧塔'), ('trusts', '陈默')]
groups= [(6, '陈默'), (3, '旧塔里的秘密入口')]
```

This confirms that the example story has no strong consistency warnings, 陈默 is correctly unknown/known across chapters 1 and 2, foreshadowing is unresolved at chapter 2 and paid off by chapter 3, and current-state reasoning does not retain the old distrust state after trust begins.

## Skill verification

The updated StoryGraph skill now includes a reasoning reference and the Phase 4 commands. It passed the Skill validator and packaged successfully as `skill.zip`.

## Important limitations

These checks intentionally favor strong, explainable warnings over speculative literary judgment. They do not prove that a story is logically wrong. Unreliable narration, lies, mistaken beliefs, disguise, deliberate ambiguity, or omitted scenes can make an apparent conflict intentional. Agents must inspect the source evidence before treating a warning as an authoring error.

Story-group detection is a graph-navigation aid, not a claim about the literary meaning of the novel.

Phase 4 is complete. Phase 5 adds safe chapter replacement, interactive visualization, and generated reports.
