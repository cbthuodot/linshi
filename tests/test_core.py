from pathlib import Path

from storygraph.core import add_fragment, basic_conflicts, empty_graph, neighbors, save_graph, load_graph, shortest_path


def sample_fragment():
    return {
        "nodes": [
            {"id": "character_林夏", "label": "林夏", "type": "character"},
            {"id": "character_陈默", "label": "陈默", "type": "character"},
            {"id": "object_银色钥匙", "label": "银色钥匙", "type": "object"},
        ],
        "edges": [
            {"source": "character_林夏", "target": "character_陈默", "relation": "trusts", "confidence": "EXTRACTED", "chapter": "第12章"},
            {"source": "character_陈默", "target": "object_银色钥匙", "relation": "owns", "confidence": "EXTRACTED", "chapter": "第12章"},
        ],
    }


def test_add_query_and_path(tmp_path: Path):
    graph = empty_graph()
    add_fragment(graph, sample_fragment())
    assert neighbors(graph, "林夏")[0]["to"] == "陈默"
    assert shortest_path(graph, "林夏", "银色钥匙") == ["林夏", "陈默", "银色钥匙"]
    path = tmp_path / "graph.json"
    save_graph(graph, path)
    restored = load_graph(path)
    assert len(restored.nodes) == 3
    assert len(restored.edges) == 2


def test_no_false_conflict_in_sample():
    graph = empty_graph()
    add_fragment(graph, sample_fragment())
    assert basic_conflicts(graph) == []
