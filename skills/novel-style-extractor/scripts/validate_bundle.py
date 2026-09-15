#!/usr/bin/env python3
"""Validate the structural contract of a generated style_bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = [
    "manifest.json", "style-profile.json", "global-style.md", "avoid-style.md", "loader-contract.md",
]
SCENES = ["dialogue", "action", "emotion", "scenery", "narration", "high_tension"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bundle")
    args = ap.parse_args()
    root = Path(args.bundle).expanduser().resolve()
    errors = []
    for rel in REQUIRED:
        if not (root / rel).is_file():
            errors.append(f"missing {rel}")
    for scene in SCENES:
        for rel in [f"scenes/{scene}.md", f"exemplars/{scene}.md"]:
            if not (root / rel).is_file():
                errors.append(f"missing {rel}")
    for rel in ["manifest.json", "style-profile.json"]:
        p = root / rel
        if p.is_file():
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid JSON {rel}: {exc}")
    if errors:
        print("INVALID")
        for e in errors:
            print(f"- {e}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
