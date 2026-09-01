import json
from pathlib import Path

import pytest

from storygraph.core import graph_to_data, load_graph
from storygraph.workspace import ingest_chapter, load_manifest, update_chapter


def write_chapter(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fragment(source: Path, index: int, nodes: list[dict], edges: list[dict]) -> dict:
    source_text = source.as_posix()
    prepared_nodes = []
    for item in nodes:
        row = dict(item)
        row.setdefault("source_file", source_text)
        row.setdefault("chapter", f"第{index}章")
        row.setdefault("chapter_index", index)
        prepared_nodes.append(row)
    prepared_edges = []
    for item in edges:
        row = dict(item)
        row.setdefault("confidence", "EXTRACTED")
        row.setdefault("source_file", source_text)
        row.setdefault("chapter", f"第{index}章")
        row.setdefault("chapter_index", index)
        prepared_edges.append(row)
    return {"nodes": prepared_nodes, "edges": prepared_edges}


def build_three_chapters(tmp_path: Path):
    graph_path = tmp_path / "storygraph-out" / "graph.json"
    c1 = tmp_path / "chapters" / "001.md"
    c2 = tmp_path / "chapters" / "002.md"
    c3 = tmp_path / "chapters" / "003.md"
    write_chapter(c1, "# 第1章\n\n林夏一直不信任陈默。\n")
    write_chapter(c2, "# 第2章\n\n林夏决定相信陈默。\n")
    write_chapter(c3, "# 第3章\n\n陈默带林夏进入旧塔。\n")

    f1 = fragment(
        c1,
        1,
        [
            {"id": "lin", "label": "林夏", "type": "character"},
            {"id": "chen", "label": "陈默", "type": "character"},
        ],
        [
            {
                "source": "lin",
                "target": "chen",
                "relation": "distrusts",
                "evidence": "林夏一直不信任陈默",
                "valid_from": 1,
                "valid_to": 1,
            }
        ],
    )
    f2 = fragment(
        c2,
        2,
        [],
        [
            {
                "source": "lin",
                "target": "chen",
                "relation": "trusts",
                "evidence": "林夏决定相信陈默",
                "valid_from": 2,
            }
        ],
    )
    f3 = fragment(
        c3,
        3,
        [{"id": "tower", "label": "旧塔", "type": "location"}],
        [
            {
                "source": "chen",
                "target": "tower",
                "relation": "located_at",
                "evidence": "陈默带林夏进入旧塔",
                "valid_from": 3,
            }
        ],
    )

    ingest_chapter(graph_path=graph_path, chapter_path=c1, fragment=f1, chapter_index=1, chapter_label="第1章")
    ingest_chapter(graph_path=graph_path, chapter_path=c2, fragment=f2, chapter_index=2, chapter_label="第2章")
    ingest_chapter(graph_path=graph_path, chapter_path=c3, fragment=f3, chapter_index=3, chapter_label="第3章")
    return graph_path, c1, c2, c3


def chapter_edges(data: dict, index: int) -> list[dict]:
    return [edge for edge in data["edges"] if edge.get("chapter_index") == index]


def test_update_replaces_only_changed_chapter(tmp_path: Path):
    graph_path, _, c2, _ = build_three_chapters(tmp_path)
    before = graph_to_data(load_graph(graph_path))
    chapter1_before = chapter_edges(before, 1)
    chapter3_before = chapter_edges(before, 3)
    manifest_before = load_manifest(graph_path)
    old_hash = next(item["sha256"] for item in manifest_before["chapters"] if item["chapter_index"] == 2)

    write_chapter(c2, "# 第2章\n\n林夏决定暂时与陈默合作。\n")
    replacement = fragment(
        c2,
        2,
        [],
        [
            {
                "source": "lin",
                "target": "chen",
                "relation": "ally_of",
                "evidence": "林夏决定暂时与陈默合作",
                "valid_from": 2,
            }
        ],
    )
    update_chapter(
        graph_path=graph_path,
        chapter_path=c2,
        fragment=replacement,
        chapter_index=2,
        chapter_label="第2章",
    )

    after = graph_to_data(load_graph(graph_path))
    assert chapter_edges(after, 1) == chapter1_before
    assert chapter_edges(after, 3) == chapter3_before
    assert [edge["relation"] for edge in chapter_edges(after, 2)] == ["ally_of"]
    manifest_after = load_manifest(graph_path)
    new_hash = next(item["sha256"] for item in manifest_after["chapters"] if item["chapter_index"] == 2)
    assert new_hash != old_hash
    assert len(manifest_after["chapters"]) == 3


def test_failed_update_does_not_change_graph_or_manifest(tmp_path: Path):
    graph_path, _, c2, _ = build_three_chapters(tmp_path)
    graph_before = graph_path.read_text(encoding="utf-8")
    manifest_path = graph_path.parent / "manifest.json"
    manifest_before = manifest_path.read_text(encoding="utf-8")

    bad = fragment(
        c2,
        2,
        [],
        [
            {
                "source": "lin",
                "target": "chen",
                "relation": "trusts",
                "evidence": "原文里根本没有这句话",
            }
        ],
    )
    with pytest.raises(ValueError):
        update_chapter(
            graph_path=graph_path,
            chapter_path=c2,
            fragment=bad,
            chapter_index=2,
            chapter_label="第2章",
        )

    assert graph_path.read_text(encoding="utf-8") == graph_before
    assert manifest_path.read_text(encoding="utf-8") == manifest_before


def test_manifest_keeps_replayable_fragments(tmp_path: Path):
    graph_path, _, _, _ = build_three_chapters(tmp_path)
    manifest = load_manifest(graph_path)
    assert [item["chapter_index"] for item in manifest["chapters"]] == [1, 2, 3]
    for entry in manifest["chapters"]:
        cached = graph_path.parent / entry["fragment_file"]
        assert cached.exists()
        data = json.loads(cached.read_text(encoding="utf-8"))
        assert isinstance(data.get("nodes"), list)
        assert isinstance(data.get("edges"), list)
