# Deep style schema

Write `deep-style.json` as valid UTF-8 JSON. Do not add prose outside the JSON file.

Use this top-level shape:

```json
{
  "narrative_distance": [],
  "sentence_rhythm": [],
  "paragraph_rhythm": [],
  "diction_rhetoric": [],
  "information_flow": [],
  "endings": [],
  "generative_rules": [],
  "hard_avoid": [],
  "soft_avoid": [],
  "failure_modes": [],
  "scene_profiles": {
    "dialogue": {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []},
    "action": {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []},
    "emotion": {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []},
    "scenery": {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []},
    "narration": {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []},
    "high_tension": {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []}
  }
}
```

Each array item should normally be an object:

```json
{
  "rule": "可执行、可观察的文风规律",
  "evidence": "来自统计或多个样本的简短依据",
  "confidence": 0.82
}
```

Rules:

1. Describe style, not plot. Never turn character names, place names, magic-system nouns, or one-off events into style rules.
2. Prefer operational rules: say what to do at generation time, not merely adjectives such as “细腻”“有画面感”.
3. Separate stable global patterns from scene-specific patterns. A battle-only habit does not belong in global rules.
4. Treat numeric analysis as evidence, not as a target to game. Convert useful measurements into natural-language guidance.
5. Use negative space carefully. Only create an avoidance rule when the absence is stable across enough material or supported by multiple samples.
6. Do not infer biography, personality, demographics, ideology, or hidden intent from writing style.
7. Keep 5–12 strong rules per global section and 4–10 per scene subsection. Fewer strong rules are better than many vague rules.
8. Mark uncertain findings below 0.65 confidence instead of presenting them as hard rules.
9. Never instruct the continuation model to copy distinctive phrases. Exemplars teach rhythm, syntax, transitions, dialogue staging, and information release.
