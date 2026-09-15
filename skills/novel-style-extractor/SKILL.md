---
name: novel-style-extractor
description: Extract a reusable Chinese-fiction style bundle from a long novel corpus for use by a separate continuation/writing skill. Use when analyzing TXT, Markdown, DOCX, a directory, or ZIP of Chinese fiction; when building an author/novel voice profile; when creating scene-specific style rules and exemplars; or when diagnosing whether a draft matches an existing style bundle. Produces explicit quantitative stylometry plus LLM-synthesized global/scene rules without fine-tuning or external APIs.
---

# Novel Style Extractor

Build a portable `style_bundle` from a Chinese novel corpus. Keep style extraction separate from story continuation: this skill creates the style package; another skill consumes it.

## Workflow

1. Determine the task:
   - New corpus → run the extraction workflow below.
   - Existing `style_bundle` + draft → run the scoring/diagnosis workflow.
   - Existing continuation skill → follow `references/continuation-integration.md` and integrate only through the bundle contract.
2. Keep corpus analysis local unless the user explicitly asks to call an external service. The scripts require no network access.
3. Treat the source corpus as the user's style evidence. Do not infer personal traits from it.

## Extraction workflow

### 1. Analyze the corpus

Accept a `.txt`, `.md`, `.markdown`, `.docx`, a directory containing those files, or a `.zip` containing them.

Run the bundled script from the directory containing this `SKILL.md` (or resolve it to an absolute path first):

```bash
python scripts/analyze_corpus.py <SOURCE> --work-dir <WORK_DIR> --max-samples 8
```

The command emits:

- `analysis.json`: quantitative stylometry.
- `samples.jsonl`: scene-stratified candidate excerpts.
- `normalized_corpus.txt`: normalized analysis source; temporary only.
- `sources.json`: provenance metadata.

For hundreds of thousands of Chinese characters, do not read `normalized_corpus.txt` into the model. Work from `analysis.json` plus selected rows of `samples.jsonl`.

### 2. Synthesize deep style

Read `references/analysis-methodology.md` and `references/deep-style-schema.md`.

Inspect `analysis.json` first. Then inspect representative sample rows across all six categories. Prefer diversity over reading every candidate. For a large corpus, 3–6 samples per category are usually enough for synthesis after the quantitative layer is available.

Create `<WORK_DIR>/deep-style.json` exactly following `references/deep-style-schema.md`.

Requirements:

- Write operational, observable rules.
- Separate global patterns from scene-specific patterns.
- Ground strong rules in multiple excerpts or a statistic plus excerpt evidence.
- Mark uncertain findings with lower confidence.
- Exclude plot facts, character names, place names and lore terms from style rules.
- Do not instruct later models to copy phrases from the source.

### 3. Build the portable bundle

Run:

```bash
python scripts/build_bundle.py \
  --analysis <WORK_DIR>/analysis.json \
  --deep-style <WORK_DIR>/deep-style.json \
  --samples <WORK_DIR>/samples.jsonl \
  --output <OUTPUT_DIR>/style_bundle \
  --profile-name <PROFILE_NAME>
```

Then validate:

```bash
python scripts/validate_bundle.py <OUTPUT_DIR>/style_bundle
```

If validation fails, fix the missing/invalid file and rerun validation before presenting the bundle.

Read `references/style-bundle-spec.md` when changing the output contract.

### 4. Report useful findings

Give the user a concise summary containing:

- corpus size and number of source documents;
- the 5–10 strongest global style findings;
- scene modules that appear especially distinctive;
- any limitations, such as mixed authors, mixed genres, OCR noise or too little dialogue/action material;
- the generated `style_bundle` path.

Do not dump raw metrics unless the user asks.

## Draft scoring and drift diagnosis

For a draft and an existing bundle, run:

```bash
python scripts/score_style.py <DRAFT> --profile <STYLE_BUNDLE>/style-profile.json
```

Use the score as a diagnostic, not a verdict. Also compare the draft against `global-style.md`, `avoid-style.md`, and the relevant scene file. Explain the largest mismatches and propose local revisions rather than blindly forcing every metric to the corpus mean.

## Quality rules

- Prefer a clean-room implementation and explicit measurements over hidden embeddings.
- Never treat stylometry as certain authorship attribution.
- Preserve multiple registers when the novel genuinely has them; do not average away dialogue vs action vs emotion differences.
- Keep the bundle small enough for progressive loading. Normal continuation should not load `style-profile.json` in full.
- Exemplars are for structure and rhythm. Never reuse source sentences or distinctive phrases in generated continuation.
- If corpus composition changes substantially, rerun extraction instead of manually editing many numeric targets.
