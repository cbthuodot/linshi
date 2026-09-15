#!/usr/bin/env python3
"""Build a portable style_bundle from quantitative analysis + LLM deep-style JSON."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

SCENES = ["dialogue", "action", "emotion", "scenery", "narration", "high_tension"]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def bullets(items) -> str:
    if not items:
        return "- （未观察到稳定规则）"
    out = []
    for item in items:
        if isinstance(item, dict):
            rule = item.get("rule") or item.get("pattern") or json.dumps(item, ensure_ascii=False)
            evidence = item.get("evidence")
            confidence = item.get("confidence")
            suffix = []
            if confidence is not None:
                suffix.append(f"置信度 {confidence}")
            if evidence:
                suffix.append(f"依据：{evidence}")
            out.append(f"- {rule}" + ("（" + "；".join(suffix) + "）" if suffix else ""))
        else:
            out.append(f"- {item}")
    return "\n".join(out)


def section(title: str, items) -> str:
    return f"## {title}\n\n{bullets(items)}\n"


def scene_doc(name: str, profile: dict) -> str:
    labels = {
        "dialogue": "对白",
        "action": "动作/战斗",
        "emotion": "情绪/心理",
        "scenery": "环境/景物",
        "narration": "日常叙事/过渡",
        "high_tension": "高压/高潮",
    }
    title = labels.get(name, name)
    parts = [f"# {title}文风\n"]
    parts.append(section("核心规律", profile.get("rules", [])))
    parts.append(section("节奏", profile.get("rhythm", [])))
    parts.append(section("语言与句法", profile.get("language", [])))
    parts.append(section("常见结构动作", profile.get("moves", [])))
    parts.append(section("避免事项", profile.get("avoid", [])))
    return "\n".join(parts).strip() + "\n"


def exemplar_doc(category: str, rows: list[dict], max_items: int) -> str:
    title = f"# {category} 原文范例\n\n仅作为文风参考。续写时学习节奏、句法、叙事动作与对白组织，不复制原句、专名或剧情事实。\n"
    selected = [r for r in rows if r.get("category") == category][:max_items]
    blocks = []
    for i, row in enumerate(selected, 1):
        text = row.get("text", "").strip()
        blocks.append(f"## 范例 {i}\n\n{text}\n")
    return title + "\n".join(blocks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--deep-style", required=True)
    ap.add_argument("--samples", required=True)
    ap.add_argument("--output", default="style_bundle")
    ap.add_argument("--profile-name", default="default")
    ap.add_argument("--exemplars-per-scene", type=int, default=4)
    args = ap.parse_args()

    analysis = load_json(Path(args.analysis))
    deep = load_json(Path(args.deep_style))
    samples = load_jsonl(Path(args.samples))
    out = Path(args.output).expanduser().resolve()
    if out.exists():
        shutil.rmtree(out)
    (out / "scenes").mkdir(parents=True)
    (out / "exemplars").mkdir(parents=True)

    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema_version": 1,
        "bundle_type": "novel-style-bundle",
        "profile_name": args.profile_name,
        "generated_at": now,
        "source_stats": analysis.get("corpus", {}),
        "modules": {
            "global": "global-style.md",
            "avoid": "avoid-style.md",
            "profile": "style-profile.json",
            "router": "loader-contract.md",
            "scenes": {name: f"scenes/{name}.md" for name in SCENES},
            "exemplars": {name: f"exemplars/{name}.md" for name in SCENES},
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    profile = {
        "schema_version": 1,
        "profile_name": args.profile_name,
        "quantitative": analysis,
        "qualitative": deep,
        "usage": {
            "priority": ["global rules", "scene rules", "character/context continuity", "exemplars", "numeric targets"],
            "do_not_copy": "Do not reuse source sentences, names, plot facts, or distinctive phrases merely because they appear in exemplars.",
        },
    }
    (out / "style-profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    global_parts = ["# 全局文风\n"]
    global_parts.append(section("叙事视角与距离", deep.get("narrative_distance", [])))
    global_parts.append(section("句法与节奏", deep.get("sentence_rhythm", [])))
    global_parts.append(section("段落组织", deep.get("paragraph_rhythm", [])))
    global_parts.append(section("词汇与修辞", deep.get("diction_rhetoric", [])))
    global_parts.append(section("信息释放与转场", deep.get("information_flow", [])))
    global_parts.append(section("章末/场景收束", deep.get("endings", [])))
    global_parts.append(section("生成时优先保持", deep.get("generative_rules", [])))
    (out / "global-style.md").write_text("\n".join(global_parts).strip() + "\n", encoding="utf-8")

    avoid_parts = ["# 避免与纠偏\n"]
    avoid_parts.append(section("硬性避免", deep.get("hard_avoid", [])))
    avoid_parts.append(section("软性警报", deep.get("soft_avoid", [])))
    avoid_parts.append(section("常见失真", deep.get("failure_modes", [])))
    (out / "avoid-style.md").write_text("\n".join(avoid_parts).strip() + "\n", encoding="utf-8")

    scene_profiles = deep.get("scene_profiles", {})
    for scene in SCENES:
        (out / "scenes" / f"{scene}.md").write_text(scene_doc(scene, scene_profiles.get(scene, {})), encoding="utf-8")
        (out / "exemplars" / f"{scene}.md").write_text(
            exemplar_doc(scene, samples, max(1, args.exemplars_per_scene)), encoding="utf-8"
        )

    loader = """# 续写 Skill 加载契约

每次续写都先读取 `manifest.json`，再按以下顺序最小化加载：

1. 始终加载 `global-style.md` 与 `avoid-style.md`。
2. 根据当前主要场景，从 `scenes/` 选择 1 个主场景模块；混合场景最多再加 1 个辅助模块。
3. 从对应 `exemplars/` 读取 2–4 个范例，只学习句法、节奏、叙事动作与对白组织；禁止复用原句、专名、剧情事实和可识别的独特措辞。
4. 仅当需要量化校准、风格诊断或自动评分时读取 `style-profile.json`；普通续写不要把完整 JSON 塞进上下文。
5. 风格服从剧情连续性：人物既定性格、世界观事实、时间线和当前情绪状态优先于风格惯例。
6. 初稿完成后，依据 `avoid-style.md` 与当前 `scenes/*.md` 做一次局部纠偏，不要为了追指标整体重写。

建议场景路由：
- 对话密集 → `dialogue`
- 战斗、追逐、强动作 → `action`
- 内心、关系、情绪推进 → `emotion`
- 环境建立、空间展示 → `scenery`
- 日常推进、过场、铺垫 → `narration`
- 冲突顶点、危机、揭示 → `high_tension`
"""
    (out / "loader-contract.md").write_text(loader, encoding="utf-8")
    print(json.dumps({"bundle": str(out), "files": sum(1 for p in out.rglob("*") if p.is_file())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
