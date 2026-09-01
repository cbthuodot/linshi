import json
from pathlib import Path

import pytest

from storygraph.core import empty_graph
from storygraph.extraction import add_chapter_fragment, chapter_extraction_errors


ROOT = Path(__file__).parent / "fixtures"
CHAPTERS = ROOT / "phase3_chapters"
EXPECTED = ROOT / "phase3_expected"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add_expected_chapters():
    graph = empty_graph()
    for index in (1, 2, 3):
        chapter = CHAPTERS / f"{index:03d}.md"
        fragment = load_json(EXPECTED / f"{index:03d}.json")
        add_chapter_fragment(
            graph,
            fragment,
            chapter_path=chapter,
            chapter_index=index,
            chapter_label=f"第{index}章",
        )
    return graph


def test_three_grounded_chapters_can_be_ingested():
    graph = add_expected_chapters()
    assert "character_lin" in graph
    assert "character_xiaoxia" not in graph
    assert "小夏" in graph.nodes["character_lin"].get("aliases", [])
    assert "secret_white_tower_mark" in graph
    assert "secret_entrance" in graph


def test_character_knowledge_changes_are_preserved():
    graph = add_expected_chapters()
    chen_edges = [
        attrs
        for source, target, attrs in graph.edges(data=True)
        if source == "character_chen" and target == "secret_white_tower_mark"
    ]
    states = {(edge.get("chapter_index"), edge.get("relation")) for edge in chen_edges}
    assert (1, "does_not_know") in states
    assert (2, "learns") in states
    assert (2, "knows") in states


def test_foreshadow_and_clue_receive_payoff():
    graph = add_expected_chapters()
    payoff_sources = {
        source
        for source, target, attrs in graph.edges(data=True)
        if target == "secret_entrance" and attrs.get("relation") == "pays_off"
    }
    assert payoff_sources == {"foreshadow_map_mark", "clue_tower_mark"}


def test_evidence_must_exist_in_source_chapter():
    graph = empty_graph()
    fragment = load_json(EXPECTED / "001.json")
    fragment["edges"][0]["evidence"] = "林夏非常喜欢陈默"
    errors = chapter_extraction_errors(
        graph,
        fragment,
        chapter_path=CHAPTERS / "001.md",
        chapter_index=1,
        chapter_label="第1章",
    )
    assert any("evidence was not found" in error for error in errors)


def test_chapter_number_and_source_file_cannot_drift():
    graph = empty_graph()
    fragment = load_json(EXPECTED / "001.json")
    fragment["edges"][0]["chapter_index"] = 9
    fragment["edges"][1]["source_file"] = "chapters/not-this-chapter.md"
    errors = chapter_extraction_errors(
        graph,
        fragment,
        chapter_path=CHAPTERS / "001.md",
        chapter_index=1,
        chapter_label="第1章",
    )
    assert any("chapter_index must equal 1" in error for error in errors)
    assert any("source_file" in error for error in errors)


def test_invalid_grounding_is_not_added():
    graph = empty_graph()
    fragment = load_json(EXPECTED / "001.json")
    fragment["edges"][0]["evidence"] = "不存在的原文"
    with pytest.raises(ValueError):
        add_chapter_fragment(
            graph,
            fragment,
            chapter_path=CHAPTERS / "001.md",
            chapter_index=1,
            chapter_label="第1章",
        )
    assert graph.number_of_nodes() == 0
