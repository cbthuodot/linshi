# StoryGraph chapter extraction specification

Use this reference when turning one novel chapter into graph JSON.

## Core rule

Extract only facts supported by the chapter. Never promote reader knowledge into character knowledge. Never convert mood, metaphor, or suspicion into a factual relationship unless the text supports that relationship.

Every edge must include:

- `source`, `target`, `relation`, `confidence`
- `chapter` and numeric `chapter_index`
- `source_file`
- `evidence`: a short verbatim passage that occurs in the chapter

Use `EXTRACTED` when the relationship is stated directly. Use `INFERRED` only when the evidence strongly supports the interpretation. Use `AMBIGUOUS` when multiple readings remain plausible.

## Entity rules

Use stable entity IDs where known. When the chapter uses a nickname or alternate name, include the alternate name in `aliases`; StoryGraph will merge only an exact name/alias match of the same type.

Use these types:

`character`, `location`, `organization`, `object`, `event`, `secret`, `clue`, `foreshadow`, `chapter`, `scene`, `rule`, `goal`, `belief`, `conflict`, `relationship`, `concept`.

Do not create a new node for every sentence. Create nodes only for story entities or ideas that are likely to matter across scenes/chapters.

## Knowledge rules

Represent a piece of hidden information as a `secret` node when it matters to the story.

Use `knows` from character to secret when the text establishes that the character knows it. Use `does_not_know` only when ignorance is explicitly supported. Use `learns` when the chapter shows the moment the character acquires the information. Set `learned_at` to the chapter index when appropriate.

Do not assume that a character knows something merely because the narrator or reader knows it.

## Relationship changes

Preserve history. If chapter 1 says A distrusts B and chapter 4 says A trusts B, write both facts with their own chapter/time information. Do not delete the earlier relationship.

Use `valid_from` and `valid_to` when the chapter clearly establishes the period. Do not invent a `valid_to` merely because a later state exists unless the transition is clear.

## Objects and locations

Use `owns` for current possession/custody when supported. If an object changes hands, write the new ownership fact and keep the old one as history.

Use `located_at` only for a location that matters to story state. Do not record every incidental movement unless it matters for continuity.

## Clues and foreshadowing

Use a `clue` node for evidence that characters can investigate or reason from. Use a `foreshadow` node for a planted detail whose later significance is not yet resolved.

Use `foreshadows` to connect the planted detail to the later event/secret/object it points toward when that target is reasonably identifiable. Use `pays_off` when a later chapter clearly resolves the planted detail.

If the target is genuinely unknown, keep the clue/foreshadow node without inventing a target.

## Output

Return one JSON object with `nodes` and `edges`. Do not return prose around the JSON when the workflow asks for a fragment file.

After writing the fragment, validate and add it with:

`storygraph add-chapter <chapter-file> <fragment.json> --index <N> --label <chapter-label>`

If validation fails, fix the extraction instead of bypassing validation.
