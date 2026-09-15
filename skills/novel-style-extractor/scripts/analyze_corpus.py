#!/usr/bin/env python3
"""Deterministic Chinese-fiction stylometry + representative sample extraction."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from corpus_io import load_corpus, split_chapters

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
CJK_RUN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
SENTENCE_RE = re.compile(r".*?(?:……+|[。！？!?]+[”’」』】]?|$)", re.S)
QUOTE_RE = re.compile(r"[“「『](.*?)[”」』]", re.S)
SOURCE_MARKER_RE = re.compile(r"^<<<SOURCE:.*?>>>$", re.M)

PUNCT = ["，", "。", "！", "？", "；", "：", "、", "…", "—", "“", "”", "（", "）"]
FUNCTION_WORDS = [
    "的", "了", "着", "过", "地", "得", "而", "但", "却", "也", "都", "又", "还", "就", "才", "便",
    "只", "仍", "并", "并且", "而且", "如果", "那么", "因为", "所以", "虽然", "但是", "不过", "于是",
    "然后", "已经", "正在", "曾经", "似乎", "仿佛", "几乎", "或许", "大概", "竟", "竟然", "居然",
    "他", "她", "它", "他们", "她们", "自己", "这", "那", "这里", "那里", "什么", "怎么", "为什么",
]
MARKER_GROUPS = {
    "simile": ["仿佛", "似乎", "宛如", "好像", "如同", "恍若", "犹如", "宛若"],
    "psychology": ["心中", "心里", "暗想", "心想", "意识到", "忽然明白", "不由得", "忍不住", "情绪", "念头"],
    "speech_tags": ["说道", "问道", "答道", "笑道", "冷笑", "低声", "沉声", "喝道", "喃喃", "开口"],
    "action": ["猛地", "骤然", "倏地", "一把", "抬手", "转身", "后退", "冲去", "扑向", "掠过", "斩", "砸", "撞"],
    "scenery": ["夜色", "月光", "阳光", "云海", "天空", "风声", "雨", "雪", "山", "河", "湖", "街道", "殿", "院", "林"],
    "transition": ["片刻后", "半晌", "与此同时", "另一边", "次日", "翌日", "不久后", "就在这时", "然而", "随后"],
}


def cjk_len(text: str) -> int:
    return len(CJK_RE.findall(text))


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return float(xs[lo])
    return float(xs[lo] * (hi - k) + xs[hi] * (k - lo))


def dist(values: Iterable[int | float]) -> dict:
    xs = [float(x) for x in values if x is not None]
    if not xs:
        return {"count": 0, "mean": 0, "median": 0, "std": 0, "p25": 0, "p75": 0, "p90": 0}
    return {
        "count": len(xs),
        "mean": round(statistics.mean(xs), 3),
        "median": round(statistics.median(xs), 3),
        "std": round(statistics.pstdev(xs), 3),
        "p25": round(percentile(xs, 0.25), 3),
        "p75": round(percentile(xs, 0.75), 3),
        "p90": round(percentile(xs, 0.90), 3),
    }


def paragraphs(text: str) -> list[str]:
    text = SOURCE_MARKER_RE.sub("", text)
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


def sentences(text: str) -> list[str]:
    out = []
    for raw in SENTENCE_RE.findall(text):
        s = raw.strip()
        if cjk_len(s) >= 2:
            out.append(s)
    return out


def rate(count: int, denominator: int, scale: int = 10000) -> float:
    return round((count / denominator * scale), 4) if denominator else 0.0


def char_ngrams(text: str, n: int, limit: int = 60) -> list[dict]:
    counter: Counter[str] = Counter()
    for run in CJK_RUN_RE.findall(text):
        if len(run) < n:
            continue
        counter.update(run[i:i+n] for i in range(len(run)-n+1))
    common = [(gram, count) for gram, count in counter.most_common(limit * 4) if count >= 2]
    return [{"gram": g, "count": c} for g, c in common[:limit]]


def opener_counter(items: list[str], n: int = 4, limit: int = 25) -> list[dict]:
    c: Counter[str] = Counter()
    for item in items:
        chars = "".join(CJK_RE.findall(item))
        if len(chars) >= 2:
            c[chars[: min(n, len(chars))]] += 1
    return [{"text": k, "count": v} for k, v in c.most_common(limit)]


def ending_counter(items: list[str], n: int = 4, limit: int = 25) -> list[dict]:
    c: Counter[str] = Counter()
    for item in items:
        chars = "".join(CJK_RE.findall(item))
        if len(chars) >= 2:
            c[chars[-min(n, len(chars)):]] += 1
    return [{"text": k, "count": v} for k, v in c.most_common(limit)]


def build_metrics(text: str, docs_meta: list[dict], chapters: list[str]) -> dict:
    ps = paragraphs(text)
    ss = sentences(text)
    total_cjk = cjk_len(text)
    p_lens = [cjk_len(p) for p in ps]
    s_lens = [cjk_len(s) for s in ss]

    quote_segments = QUOTE_RE.findall(text)
    quote_chars = sum(cjk_len(q) for q in quote_segments)
    dialogue_ps = [p for p in ps if QUOTE_RE.search(p)]
    sentence_counts_by_p = [len(sentences(p)) for p in ps]

    punctuation = {ch: {"count": text.count(ch), "per_10k_chars": rate(text.count(ch), total_cjk)} for ch in PUNCT}
    function_words = {}
    for word in FUNCTION_WORDS:
        count = text.count(word)
        function_words[word] = {"count": count, "per_10k_chars": rate(count, total_cjk)}

    marker_rates = {}
    for group, words in MARKER_GROUPS.items():
        hits = {w: text.count(w) for w in words}
        marker_rates[group] = {
            "total": sum(hits.values()),
            "per_10k_chars": rate(sum(hits.values()), total_cjk),
            "items": hits,
        }

    short_sentences = sum(1 for x in s_lens if x <= 8)
    long_sentences = sum(1 for x in s_lens if x >= 30)
    one_sentence_ps = sum(1 for n in sentence_counts_by_p if n == 1)
    very_short_ps = sum(1 for x in p_lens if x <= 20)
    exclaim_question = sum(text.count(x) for x in ["！", "？", "!", "?"])

    chapter_endings = []
    for ch in chapters[:500]:
        body = ch.strip()
        if not body:
            continue
        chapter_endings.append(body[-240:])

    return {
        "schema_version": 1,
        "corpus": {
            "documents": docs_meta,
            "document_count": len(docs_meta),
            "chapter_count": len(chapters),
            "cjk_chars": total_cjk,
            "paragraph_count": len(ps),
            "sentence_count": len(ss),
        },
        "sentence_length_cjk": dist(s_lens),
        "paragraph_length_cjk": dist(p_lens),
        "rhythm": {
            "short_sentence_rate": round(short_sentences / len(s_lens), 4) if s_lens else 0,
            "long_sentence_rate": round(long_sentences / len(s_lens), 4) if s_lens else 0,
            "one_sentence_paragraph_rate": round(one_sentence_ps / len(ps), 4) if ps else 0,
            "very_short_paragraph_rate": round(very_short_ps / len(ps), 4) if ps else 0,
            "exclaim_question_per_10k_chars": rate(exclaim_question, total_cjk),
        },
        "dialogue": {
            "quoted_cjk_chars": quote_chars,
            "quoted_char_ratio": round(quote_chars / total_cjk, 4) if total_cjk else 0,
            "dialogue_paragraph_ratio": round(len(dialogue_ps) / len(ps), 4) if ps else 0,
            "quote_style": {
                "curly_cn": text.count("“") + text.count("”"),
                "corner": text.count("「") + text.count("」"),
                "double_corner": text.count("『") + text.count("』"),
            },
        },
        "punctuation": punctuation,
        "function_words": function_words,
        "markers": marker_rates,
        "sentence_openers": opener_counter(ss),
        "sentence_endings": ending_counter(ss),
        "paragraph_openers": opener_counter(ps),
        "char_ngrams": {
            "2": char_ngrams(text, 2),
            "3": char_ngrams(text, 3),
            "4": char_ngrams(text, 4),
        },
        "chapter_ending_samples": chapter_endings[:80],
    }


def chunk_paragraphs(ps: list[str], min_chars: int = 350, max_chars: int = 900) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for p in ps:
        plen = cjk_len(p)
        if plen > max_chars:
            for s in sentences(p):
                if size + cjk_len(s) > max_chars and size >= min_chars:
                    chunks.append("\n\n".join(buf).strip())
                    buf, size = [], 0
                buf.append(s)
                size += cjk_len(s)
            continue
        if size + plen > max_chars and size >= min_chars:
            chunks.append("\n\n".join(buf).strip())
            buf, size = [], 0
        buf.append(p)
        size += plen
    if buf and size >= max(120, min_chars // 2):
        chunks.append("\n\n".join(buf).strip())
    return chunks


def category_scores(chunk: str) -> dict[str, float]:
    length = max(cjk_len(chunk), 1)
    sents = sentences(chunk)
    lens = [cjk_len(s) for s in sents] or [length]
    quoted = sum(cjk_len(q) for q in QUOTE_RE.findall(chunk)) / length

    def hits(group: str) -> float:
        return sum(chunk.count(w) for w in MARKER_GROUPS[group]) / length * 1000

    punctuation_burst = sum(chunk.count(x) for x in ["！", "？", "!", "?"]) / length * 1000
    short_rate = sum(1 for x in lens if x <= 10) / len(lens)
    return {
        "dialogue": quoted * 10 + hits("speech_tags") * 0.8,
        "action": hits("action") * 1.4 + short_rate * 3 + punctuation_burst * 0.15,
        "emotion": hits("psychology") * 1.4 + hits("simile") * 0.4,
        "scenery": hits("scenery") * 1.3 + hits("simile") * 0.5,
        "narration": max(0.0, 2.0 - quoted * 3) + hits("transition") * 0.4,
        "high_tension": short_rate * 4 + punctuation_burst * 0.35 + hits("action") * 0.6,
    }


def choose_samples(text: str, max_per_category: int = 8) -> list[dict]:
    chunks = chunk_paragraphs(paragraphs(text))
    by_cat: dict[str, list[tuple[float, int, str]]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        scores = category_scores(chunk)
        for cat, score in scores.items():
            by_cat[cat].append((score, i, chunk))

    chosen: list[dict] = []
    for cat, rows in by_cat.items():
        rows.sort(key=lambda x: (-x[0], x[1]))
        selected: list[tuple[float, int, str]] = []
        seen: set[str] = set()
        for row in rows:
            digest = hashlib.sha1(row[2].encode("utf-8")).hexdigest()
            if digest in seen:
                continue
            if any(abs(row[1] - old[1]) < 3 for old in selected) and len(rows) > max_per_category * 2:
                continue
            selected.append(row)
            seen.add(digest)
            if len(selected) >= max_per_category:
                break
        for rank, (score, idx, chunk) in enumerate(selected, 1):
            chosen.append({
                "category": cat,
                "rank": rank,
                "score": round(score, 4),
                "chunk_index": idx,
                "cjk_chars": cjk_len(chunk),
                "text": chunk,
            })
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="TXT/MD/DOCX file, directory, or ZIP corpus")
    ap.add_argument("--work-dir", default=".style-work", help="Output work directory")
    ap.add_argument("--max-samples", type=int, default=8, help="Maximum candidates per category")
    args = ap.parse_args()

    docs = load_corpus(args.source)
    out = Path(args.work_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    combined_parts = []
    chapters = []
    for doc in docs:
        combined_parts.append(doc.text)
        chapters.extend(split_chapters(doc.text))
    text = "\n\n".join(combined_parts)
    docs_meta = [d.metadata() for d in docs]
    metrics = build_metrics(text, docs_meta, chapters)
    samples = choose_samples(text, max_per_category=max(2, args.max_samples))

    (out / "normalized_corpus.txt").write_text(text, encoding="utf-8")
    (out / "analysis.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "samples.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in samples) + "\n",
        encoding="utf-8",
    )
    (out / "sources.json").write_text(json.dumps(docs_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "documents": len(docs),
        "cjk_chars": metrics["corpus"]["cjk_chars"],
        "paragraphs": metrics["corpus"]["paragraph_count"],
        "sentences": metrics["corpus"]["sentence_count"],
        "samples": len(samples),
        "work_dir": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
