# Integrating with an existing continuation skill

Do not merge the extractor into the continuation skill. Keep them as two components joined by the `style_bundle` contract.

Recommended continuation workflow:

1. Locate the active `style_bundle` and read `manifest.json`.
2. Load `global-style.md` and `avoid-style.md`.
3. Classify the current continuation scene into one primary type and optionally one secondary type.
4. Load the matching files under `scenes/`.
5. Load 2–4 corresponding source examples under `exemplars/`.
6. Read story-state files separately: plot, character state, world rules, timeline, unresolved hooks and immediate previous prose.
7. Draft the requested continuation.
8. Run a style-only revision pass using `avoid-style.md` and the active scene module. Preserve story facts and causal logic.
9. Optionally run `score_style.py` against `style-profile.json` when diagnosing drift across many chapters.

Recommended precedence:

1. User's current explicit instruction.
2. Canonical story facts and continuity.
3. Character-specific state and voice.
4. Global style rules.
5. Scene-specific style rules.
6. Exemplars.
7. Numeric targets.

The continuation skill should never load `normalized_corpus.txt`; that file exists only in the extractor's temporary work directory.
