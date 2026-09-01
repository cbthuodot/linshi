# StoryGraph narrative model

Use this reference when choosing entities and relationships.

Keep the graph focused on story logic rather than prose style.

Important entity categories include characters, places, organizations, objects, events, secrets, clues, foreshadowing, goals, beliefs, conflicts, chapters, scenes, and world rules.

Prefer specific relationships over vague `related_to` links. Useful relationships include:

`knows`, `does_not_know`, `knows_person`, `trusts`, `distrusts`, `loves`, `hates`, `ally_of`, `enemy_of`, `parent_of`, `sibling_of`, `married_to`, `owns`, `gives_to`, `receives_from`, `located_at`, `member_of`, `wants`, `fears`, `believes`, `causes`, `witnesses`, `learns`, `reveals`, `hides_from`, `appears_in`, `participates_in`, `foreshadows`, `pays_off`, `contradicts`, `occurs_before`, `occurs_after`.

Treat chapter numbers as the story's observation order unless the text clearly gives another internal chronology. Use numeric `chapter_index` for sorting even when the displayed chapter name is not numeric.

Keep original prose outside the graph. Store only short evidence snippets needed to trace a fact back to its source.
