# Design inspirations

This repository is a clean-room implementation. It does not vendor source code from the projects below.

- `ngpepin/stylometric-transfer` — inspiration for explicit, versionable style fingerprints and quantitative style scoring. Its repository uses the PolyForm Noncommercial License 1.0.0, so this project intentionally does not copy or incorporate its implementation.
- `Hiro-Inagawa/write-like-me` — inspiration for separating generative guidance from corrective checks, retaining exemplars, and validating style profiles. MIT licensed.
- `jnoecker/mowen` — inspiration for Chinese-aware stylometry and the usefulness of character n-grams in authorship/style analysis. MIT licensed.

The implementation here was written independently around the `style_bundle` contract described in `skills/novel-style-extractor/references/style-bundle-spec.md`.
