#!/usr/bin/env python3
"""Install the bundled skill into ZCode globally or into a project."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SKILL_NAME = "novel-style-extractor"
SOURCE = Path(__file__).resolve().parent / "skills" / SKILL_NAME


def main() -> int:
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--global", action="store_true", dest="global_install", help="Install into ~/.zcode/skills")
    group.add_argument("--project", help="Install into <project>/.zcode/skills")
    ap.add_argument("--force", action="store_true", help="Replace an existing installed copy")
    args = ap.parse_args()

    if args.global_install:
        root = Path.home() / ".zcode" / "skills"
    else:
        root = Path(args.project).expanduser().resolve() / ".zcode" / "skills"
    target = root / SKILL_NAME
    root.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if not args.force:
            raise SystemExit(f"Already exists: {target}. Re-run with --force to replace it.")
        shutil.rmtree(target)
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
