# Analysis methodology

This skill uses a clean-room hybrid design inspired by three families of tools:

- Explicit stylometric fingerprints: measurable sentence, paragraph, punctuation, lexical and structural signals represented in a reusable profile.
- Voice-profile workflows: separate generative rules from corrective rules, preserve provenance, keep representative exemplars, and validate generated prose after drafting.
- Chinese authorship stylometry: favor character n-grams and Chinese-specific segmentation/markers rather than relying on English-only function words and readability formulas.

The deterministic scripts intentionally avoid copying implementation code from upstream projects. The base pipeline uses only Python standard-library modules.

## Quantitative layer

The analyzer measures:

- CJK sentence-length and paragraph-length distributions.
- Short-sentence, long-sentence, one-sentence-paragraph and very-short-paragraph rates.
- Chinese punctuation rates per 10,000 CJK characters.
- Dialogue character ratio, dialogue paragraph ratio, and quote convention.
- A compact Chinese function-word profile.
- Marker families for simile, psychology, speech tags, action, scenery and transitions.
- Common character 2/3/4-grams.
- Sentence and paragraph openers, sentence endings, and chapter-ending samples.

These features are intentionally interpretable. They are not proof of authorship and should not be used as forensic certainty.

## Qualitative layer

The Agent reads the measurements together with stratified representative samples and creates `deep-style.json`. It should extract operational patterns such as:

- narrative distance and point-of-view stability;
- whether emotion is named directly or externalized through action/sensation;
- dialogue staging and action beats;
- escalation patterns in action scenes;
- scenery-to-character coupling;
- paragraph cadence and transitions;
- information-release rhythm and scene/chapter endings;
- recurring failure modes when an imitation becomes too generic or too "AI-like".

## Sampling layer

The script produces candidates for dialogue, action, emotion, scenery, narration and high-tension scenes. The categories are heuristic, not semantic ground truth. The Agent must inspect samples before elevating a candidate pattern into a rule.

## Validation

`score_style.py` provides a quantitative similarity score for drafts. It is deliberately only one signal. Literary fidelity also requires checking the active scene rules and exemplars. A high numeric score can still be a poor imitation if narrative stance or information flow is wrong.
