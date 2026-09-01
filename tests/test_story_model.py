from pathlib import Path

from storygraph.core import add_fragment, empty_graph, load_graph, save_graph, story_history


CHAPTER_ROOT = Path(__file__).parent / "fixtures" / "phase2_chapters"


def chapter1_fragment():
    return {
        "nodes": [
            {
                "id": "character_lin",
                "label": "林夏",
                "type": "character",
                "aliases": ["小夏"],
                "source_file": "tests/fixtures/phase2_chapters/001.md",
                "chapter": "第1章",
                "chapter_index": 1,
            },
            {"id": "character_chen", "label": "陈默", "type": "character"},
            {"id": "object_key", "label": "银色钥匙", "type": "object"},
        ],
        "edges": [
            {
                "source": "character_lin",
                "target": "character_chen",
                "relation": "distrusts",
                "confidence": "EXTRACTED",
                "chapter": "第1章",
                "chapter_index": 1,
                "valid_from": 1,
                "valid_to": 1,
                "source_file": "tests/fixtures/phase2_chapters/001.md",
                "evidence": "她一直不信任陈默",
            },
            {
                "source": "character_lin",
                "target": "object_key",
                "relation": "owns",
                "confidence": "EXTRACTED",
                "chapter": "第1章",
                "chapter_index": 1,
                "valid_from": 1,
                "valid_to": 1,
                "source_file": "tests/fixtures/phase2_chapters/001.md",
                "evidence": "银色钥匙由林夏保管",
            },
        ],
    }


def chapter2_fragment():
    return {
        "nodes": [
            {
                "id": "character_xiaoxia",
                "label": "小夏",
                "type": "character",
                "aliases": ["林夏"],
                "source_file": "tests/fixtures/phase2_chapters/002.md",
                "chapter": "第2章",
                "chapter_index": 2,
            }
        ],
        "edges": [
            {
                "source": "character_xiaoxia",
                "target": "character_chen",
                "relation": "trusts",
                "confidence": "EXTRACTED",
                "chapter": "第2章",
                "chapter_index": 2,
                "valid_from": 2,
                "source_file": "tests/fixtures/phase2_chapters/002.md",
                "evidence": "小夏决定相信陈默",
            },
            {
                "source": "character_chen",
                "target": "object_key",
                "relation": "owns",
                "confidence": "EXTRACTED",
                "chapter": "第2章",
                "chapter_index": 2,
                "valid_from": 2,
                "source_file": "tests/fixtures/phase2_chapters/002.md",
                "evidence": "她把银色钥匙交给陈默保管",
            },
        ],
    }


def chapter3_fragment():
    return {
        "nodes": [
            {
                "id": "character_lin_again",
                "label": "林夏",
                "type": "character",
                "aliases": ["小夏"],
                "source_file": "tests/fixtures/phase2_chapters/003.md",
                "chapter": "第3章",
                "chapter_index": 3,
            },
            {
                "id": "location_old_tower",
                "label": "旧塔",
                "type": "location",
                "source_file": "tests/fixtures/phase2_chapters/003.md",
                "chapter": "第3章",
                "chapter_index": 3,
            },
        ],
        "edges": [
            {
                "source": "character_lin_again",
                "target": "location_old_tower",
                "relation": "located_at",
                "confidence": "EXTRACTED",
                "chapter": "第3章",
                "chapter_index": 3,
                "valid_from": 3,
                "source_file": "tests/fixtures/phase2_chapters/003.md",
                "evidence": "林夏和陈默带着银色钥匙进入旧塔",
            }
        ],
    }


def build_three_chapter_graph():
    graph = empty_graph()
    add_fragment(graph, chapter1_fragment())
    remap2 = add_fragment(graph, chapter2_fragment())
    remap3 = add_fragment(graph, chapter3_fragment())
    return graph, remap2, remap3


def test_phase2_fixture_files_exist():
    for name in ("001.md", "002.md", "003.md"):
        assert (CHAPTER_ROOT / name).exists()


def test_aliases_merge_into_one_character():
    graph, remap2, remap3 = build_three_chapter_graph()
    assert remap2["character_xiaoxia"] == "character_lin"
    assert remap3["character_lin_again"] == "character_lin"
    assert "character_xiaoxia" not in graph
    assert "character_lin_again" not in graph
    characters = [node for node, attrs in graph.nodes(data=True) if attrs.get("type") == "character"]
    assert sorted(characters) == ["character_chen", "character_lin"]
    assert "小夏" in graph.nodes["character_lin"]["aliases"]


def test_relationship_change_keeps_history_in_story_order():
    graph, _, _ = build_three_chapter_graph()
    history = story_history(graph, "小夏")
    relations = [(row["chapter_index"], row["relation"]) for row in history]
    assert relations == sorted(relations, key=lambda item: (item[0], item[1]))
    assert (1, "distrusts") in relations
    assert (2, "trusts") in relations
    assert graph.number_of_edges("character_lin", "character_chen") == 2


def test_object_ownership_change_is_preserved():
    graph, _, _ = build_three_chapter_graph()
    owners = []
    for source, _, attrs in graph.in_edges("object_key", data=True):
        if attrs.get("relation") == "owns":
            owners.append((attrs.get("chapter_index"), source, attrs.get("valid_from"), attrs.get("valid_to")))
    assert sorted(owners) == [
        (1, "character_lin", 1, 1),
        (2, "character_chen", 2, None),
    ]


def test_sources_evidence_and_roundtrip_are_preserved(tmp_path: Path):
    graph, _, _ = build_three_chapter_graph()
    distrust = next(
        attrs
        for source, target, attrs in graph.edges(data=True)
        if source == "character_lin" and target == "character_chen" and attrs.get("relation") == "distrusts"
    )
    assert distrust["source_file"].endswith("001.md")
    assert distrust["evidence"] == "她一直不信任陈默"

    graph_path = tmp_path / "graph.json"
    save_graph(graph, graph_path)
    restored = load_graph(graph_path)
    assert restored.graph["schema_version"] == 2
    assert story_history(restored, "林夏") == story_history(graph, "林夏")
