from pathlib import Path

from storygraph.core import add_fragment, empty_graph, graph_to_data, load_graph, neighbors, save_graph, shortest_path


def sample_fragment():
    return {
        "nodes": [
            {"id": "character_lin", "label": "林夏", "type": "character"},
            {"id": "character_chen", "label": "陈默", "type": "character"},
            {"id": "object_key", "label": "银色钥匙", "type": "object"},
        ],
        "edges": [
            {"source": "character_lin", "target": "character_chen", "relation": "trusts", "confidence": "EXTRACTED"},
            {"source": "character_chen", "target": "object_key", "relation": "owns", "confidence": "EXTRACTED"},
        ],
    }


def test_add_query_path_and_roundtrip(tmp_path: Path):
    graph = empty_graph()
    add_fragment(graph, sample_fragment())
    assert neighbors(graph, "林夏")[0]["to"] == "陈默"
    assert shortest_path(graph, "林夏", "银色钥匙") == ["林夏", "陈默", "银色钥匙"]

    path = tmp_path / "graph.json"
    save_graph(graph, path)
    restored = load_graph(path)
    assert graph_to_data(restored) == graph_to_data(graph)


def test_multiple_edges_are_preserved():
    graph = empty_graph()
    fragment = sample_fragment()
    fragment["edges"].append(
        {"source": "character_lin", "target": "character_chen", "relation": "distrusts", "confidence": "INFERRED"}
    )
    add_fragment(graph, fragment)
    assert graph.number_of_edges("character_lin", "character_chen") == 2
