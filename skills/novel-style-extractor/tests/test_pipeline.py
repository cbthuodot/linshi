import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

SAMPLE = """第一章 雨夜

雨落得很密。林舟抬头看了一眼屋檐，没说话。

“你还要等？”她问。

林舟笑了笑，把袖口往上卷了一寸。“再等一会儿。”

风从巷口灌进来，灯火轻轻一晃。他忽然听见远处一声闷响，脚下一错，人已经贴到了墙边。

第二章 清晨

天刚亮，院子里的水还没有干。她坐在石阶上，盯着杯口那一点白气，心里并不平静。

他从门里出来，没有问昨夜的事，只把一件外衣搭在她肩上。
""" * 20

DEEP = {
    "narrative_distance": [{"rule": "保持贴近当前人物感知的第三人称", "evidence": "样本", "confidence": 0.8}],
    "sentence_rhythm": [], "paragraph_rhythm": [], "diction_rhetoric": [], "information_flow": [],
    "endings": [], "generative_rules": [], "hard_avoid": [], "soft_avoid": [], "failure_modes": [],
    "scene_profiles": {k: {"rules": [], "rhythm": [], "language": [], "moves": [], "avoid": []}
                       for k in ["dialogue", "action", "emotion", "scenery", "narration", "high_tension"]}
}


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], check=True, text=True, capture_output=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        source = td / "novel.txt"
        source.write_text(SAMPLE, encoding="utf-8")
        work = td / "work"
        run(SCRIPTS / "analyze_corpus.py", source, "--work-dir", work, "--max-samples", "3")
        analysis = json.loads((work / "analysis.json").read_text(encoding="utf-8"))
        assert analysis["corpus"]["cjk_chars"] > 1000
        assert analysis["dialogue"]["quoted_char_ratio"] > 0
        (work / "deep-style.json").write_text(json.dumps(DEEP, ensure_ascii=False), encoding="utf-8")
        bundle = td / "style_bundle"
        run(SCRIPTS / "build_bundle.py", "--analysis", work / "analysis.json", "--deep-style", work / "deep-style.json",
            "--samples", work / "samples.jsonl", "--output", bundle, "--profile-name", "test")
        run(SCRIPTS / "validate_bundle.py", bundle)
        scored = run(SCRIPTS / "score_style.py", source, "--profile", bundle / "style-profile.json", "--json")
        score = json.loads(scored.stdout)["score"]
        assert 0 <= score <= 100
        assert (bundle / "loader-contract.md").is_file()
    print("ok")


if __name__ == "__main__":
    main()
