from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from .validate import assert_valid

SCHEMA_VERSION = 1


def empty_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.graph.update({"schema_version": SCHEMA_VERSION, "kind": "storygraph"})
    return graph


def add_fragment(graph: nx.MultiDiGraph, fragment: dict) -> None:
    """Validate and merge a graph fragment. Invalid data fails loudly."""
    assert_valid(fragment)
    for node in fragment["nodes"]:
        node_id = node["id"]
        attrs = {k: v for k, v in node.items() if k != "id"}
        if node_id in graph:
            existing = dict(graph.nodes[node_id])
            existing.update({k: v for k, v in attrs.items() if v is not None})
            graph.nodes[node_id].update(existing)
        else:
            graph.add_node(node_id, **attrs)

    for edge in fragment["edges"]:
        source = edge["source"]
        target = edge["target"]
        attrs = {k: v for k, v in edge.items() if k not in {"source", "target", "key"}}
        key = edge.get("key")
        if key is None:
            graph.add_edge(source, target, **attrs)
        else:
            graph.add_edge(source, target, key=str(key), **attrs)


def graph_to_data(graph: nx.MultiDiGraph) -> dict:
    nodes = []
    for node_id, attrs in sorted(graph.nodes(data=True), key=lambda item: str(item[0])):
        nodes.append({"id": node_id, **dict(attrs)})

    edges = []
    for source, target, key, attrs in graph.edges(keys=True, data=True):
        edges.append({"source": source, "target": target, "key": str(key), **dict(attrs)})
    edges.sort(key=lambda item: (str(item["source"]), str(item["target"]), str(item["key"])))

    return {
        "schema_version": SCHEMA_VERSION,
        "graph": {"kind": graph.graph.get("kind", "storygraph")},
        "nodes": nodes,
        "edges": edges,
    }


def graph_from_data(data: dict) -> nx.MultiDiGraph:
    # Backward-compatible with the early prototype, which had no schema_version.
    version = data.get("schema_version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported StoryGraph schema version: {version}")
    fragment = {"nodes": data.get("nodes", []), "edges": data.get("edges", [])}
    graph = empty_graph()
    graph_meta = data.get("graph")
    if isinstance(graph_meta, dict):
        graph.graph.update(graph_meta)
    add_fragment(graph, fragment)
    return graph


def load_graph(path: Path) -> nx.MultiDiGraph:
    if not path.exists():
        return empty_graph()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("StoryGraph file must contain a JSON object")
    return graph_from_data(data)


def save_graph(graph: nx.MultiDiGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(graph_to_data(graph), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _find_nodes(graph: nx.MultiDiGraph, query: str) -> list[str]:
    q = query.casefold().strip()
    if not q:
        return []
    return [
        node_id
        for node_id, attrs in graph.nodes(data=True)
        if q in str(attrs.get("label", node_id)).casefold()
    ]


def neighbors(graph: nx.MultiDiGraph, query: str) -> list[dict]:
    results: list[dict] = []
    for node in _find_nodes(graph, query):
        for _, target, key, attrs in graph.out_edges(node, keys=True, data=True):
            results.append(
                {
                    "from": graph.nodes[node].get("label", node),
                    "relation": attrs.get("relation", "related_to"),
                    "to": graph.nodes[target].get("label", target),
                    "confidence": attrs.get("confidence"),
                    "key": str(key),
                }
            )
        for source, _, key, attrs in graph.in_edges(node, keys=True, data=True):
            results.append(
                {
                    "from": graph.nodes[source].get("label", source),
                    "relation": attrs.get("relation", "related_to"),
                    "to": graph.nodes[node].get("label", node),
                    "confidence": attrs.get("confidence"),
                    "key": str(key),
                }
            )
    return results


def shortest_path(graph: nx.MultiDiGraph, a: str, b: str) -> list[str]:
    source_matches = _find_nodes(graph, a)
    target_matches = _find_nodes(graph, b)
    if not source_matches or not target_matches:
        return []
    try:
        path = nx.shortest_path(graph.to_undirected(), source_matches[0], target_matches[0])
    except nx.NetworkXNoPath:
        return []
    return [str(graph.nodes[node].get("label", node)) for node in path]
