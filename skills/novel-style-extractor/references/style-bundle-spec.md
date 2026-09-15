# style_bundle specification

`style_bundle` is a portable, model-readable output consumed by a separate fiction continuation skill.

## Required layout

```text
style_bundle/
├── manifest.json
├── style-profile.json
├── global-style.md
├── avoid-style.md
├── loader-contract.md
├── scenes/
│   ├── dialogue.md
│   ├── action.md
│   ├── emotion.md
│   ├── scenery.md
│   ├── narration.md
│   └── high_tension.md
└── exemplars/
    ├── dialogue.md
    ├── action.md
    ├── emotion.md
    ├── scenery.md
    ├── narration.md
    └── high_tension.md
```

## Design principles

- `global-style.md` is always small enough to load for every continuation request.
- `scenes/*.md` are conditional modules. Load one primary module and at most one secondary module.
- `exemplars/*.md` contain a few representative source excerpts. They are references for form, not text to copy.
- `style-profile.json` contains the complete quantitative analysis and qualitative profile. It is for diagnostics and scoring; normal continuation should not load the entire file.
- `avoid-style.md` is corrective guidance and should be checked after drafting.
- `loader-contract.md` is the stable interface between this extractor and any continuation skill.

## Versioning

The current schema version is `1`. Consumers must read `manifest.json` first and should refuse or gracefully degrade on unsupported major versions.

## Context budget

Keep generated Markdown concise. As a default, use 4 exemplars per scene and roughly 350–900 Chinese characters per exemplar. The consumer should load only the modules needed for the current scene.
