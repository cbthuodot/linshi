from pathlib import Path

from storygraph.core import add_fragment, empty_graph, save_graph
from storygraph.export import export_all, to_html, to_report


def sample_graph():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                {"id": "lin", "label": "林夏", "type": "character", "aliases": ["小夏"]},
                {"id": "chen", "label": "陈默", "type": "character"},
                {"id": "clue", "label": "旧地图上的白塔标记", "type": "foreshadow", "chapter_index": 1},
            ],
            "edges": [
                {
                    "source": "lin",
                    "target": "chen",
                    "relation": "trusts",
                    "confidence": "EXTRACTED",
                    "chapter": "第2章",
                    "chapter_index": 2,
                    "valid_from": 2,
                }
            ],
        },
    )
    return graph


def test_html_is_self_contained_and_clickable(tmp_path: Path):
    path = tmp_path / "graph.html"
    to_html(sample_graph(), path)
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "StoryGraph 小说关系图" in text
    assert "林夏" in text
    assert "陈默" in text
    assert "function select(id)" in text
    assert "storygraph-data" in text
    assert '<script src="http' not in lowered
    assert "<script src='http" not in lowered
    assert '<link href="http' not in lowered
    assert "<link href='http" not in lowered


def test_report_contains_story_status(tmp_path: Path):
    graph = sample_graph()
    graph_path = tmp_path / "storygraph-out" / "graph.json"
    save_graph(graph, graph_path)
    report = tmp_path / "storygraph-out" / "STORY_REPORT.md"
    to_report(graph, report, graph_path=graph_path)
    text = report.read_text(encoding="utf-8")
    assert "# STORY REPORT" in text
    assert "未回收线索/伏笔：1" in text
    assert "旧地图上的白塔标记" in text
    assert "没有发现强一致性问题" in text


def test_export_all_writes_three_outputs(tmp_path: Path):
    graph = sample_graph()
    graph_path = tmp_path / "graph.json"
    html_path = tmp_path / "graph.html"
    report_path = tmp_path / "STORY_REPORT.md"
    export_all(graph, graph_path, html_path, report_path)
    assert graph_path.exists()
    assert html_path.exists()
    assert report_path.exists()
