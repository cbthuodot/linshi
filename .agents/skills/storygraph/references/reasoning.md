# StoryGraph reasoning checks

Use these commands after relevant chapters have been ingested.

`storygraph knowledge "<character>" "<secret>" --at <chapter>` answers the character's recorded knowledge state at that chapter. Treat `unknown` as "the graph has no supported answer", not as proof the character does not know.

`storygraph timeline "<entity>"` shows the entity's recorded relationship history in chapter order.

`storygraph state "<entity>" --at <chapter>` shows relationships considered active at that point in the story. Later ownership/location/opposing relationship states normally supersede earlier open-ended states unless the earlier state has an explicit overlapping `valid_to`.

`storygraph unresolved --at <chapter>` lists clues and foreshadowing planted by that point that do not yet have a recorded `pays_off` relation.

`storygraph groups` identifies tightly connected story groups using graph community structure. Treat this as a navigation aid, not literary truth.

`storygraph check` reports strong consistency warnings. Current checks include:

- a character revealing a secret before being recorded as learning/knowing it;
- explicit `contradicts` relations;
- simultaneous opposing relationships with overlapping validity;
- an object having multiple active owners at the same point;
- a character having multiple active locations at the same point.

Do not call every warning a definite writing error. First inspect the cited graph facts and original chapter evidence. Fiction can intentionally contain lies, unreliable narration, mistaken beliefs, disguises, and apparent contradictions.
