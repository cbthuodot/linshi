#!/usr/bin/env python3
"""Score a draft against the quantitative portion of a style bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_corpus import build_metrics
from corpus_io import load_corpus, split_chapters


def rel_delta(actual: float, target: float, floor: float = 1.0) -> float:
    return abs(actual - target) / max(abs(target), floor)


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("draft")
    ap.add_argument("--profile", required=True, help="style-profile.json")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    target = profile.get("quantitative", profile)
    docs = load_corpus(args.draft)
    text = "\n\n".join(d.text for d in docs)
    actual = build_metrics(text, [d.metadata() for d in docs], sum((split_chapters(d.text) for d in docs), []))

    checks: list[tuple[str, float, float, float]] = []
    for path, weight, floor in [
        (("sentence_length_cjk", "mean"), 1.3, 4.0),
        (("sentence_length_cjk", "median"), 1.0, 4.0),
        (("paragraph_length_cjk", "mean"), 1.0, 12.0),
        (("rhythm", "short_sentence_rate"), 1.2, 0.08),
        (("rhythm", "one_sentence_paragraph_rate"), 0.8, 0.08),
        (("dialogue", "quoted_char_ratio"), 1.2, 0.08),
        (("dialogue", "dialogue_paragraph_ratio"), 1.0, 0.08),
    ]:
        a = actual[path[0]][path[1]]
        t = target[path[0]][path[1]]
        checks.append((".".join(path), float(a), float(t), rel_delta(float(a), float(t), floor) * weight))

    for ch in ["，", "。", "！", "？", "；", "：", "…", "—"]:
        a = actual["punctuation"][ch]["per_10k_chars"]
        t = target["punctuation"][ch]["per_10k_chars"]
        checks.append((f"punctuation.{ch}", float(a), float(t), rel_delta(float(a), float(t), 2.0) * 0.45))

    penalty = sum(min(1.5, c[3]) for c in checks) / max(sum(1 for _ in checks), 1)
    score = round(100 * clamp01(1 - penalty / 1.25), 1)
    deviations = sorted(checks, key=lambda x: x[3], reverse=True)[:8]
    result = {
        "score": score,
        "interpretation": "quantitative-only; use scene rules and exemplars for final literary judgment",
        "largest_deviations": [
            {"metric": name, "actual": round(a, 4), "target": round(t, 4), "weighted_delta": round(d, 4)}
            for name, a, t, d in deviations
        ],
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Style score: {score}/100")
        for row in result["largest_deviations"]:
            print(f"- {row['metric']}: actual={row['actual']} target={row['target']} delta={row['weighted_delta']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
