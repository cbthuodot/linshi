from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

import networkx as nx

ALLOWED_TYPES = {
    "character", "location", "organization", "object", "event", "secret",
    "clue", "foreshadow", "chapter", "scene", "rule", "goal", "belief",
    "conflict", "relationship", "concept",
}


def make_id(kind: str, label: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "_", label.strip().lower()).strip("_")
    return f"{kind}_{text}" if text else kind


def empty_graph() -> nx.MultiDiGraph:
    return nx.MultiDiGraph()


def add_fragment(graph: nx.MultiDiGraph, fragment: dict) -> None:
    for node in fragment.get("nodes", []):
        kind = node.get("type", "concept")
        if kind not in ALLOWED_TYPES:
            kind = "concept"
        node_id = node.get("id") or make_id(kind, node.get("label", "unknown"))
        attrs = dict(node)
        attrs["type"] = kind
        attrs["label"] = node.get("label", node_id)
        graph.add_node(node_id, **attrs)

    for edge in fragment.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target or source not in graph or target not in graph:
            continue
        attrs = dict(edge)
        attrs.setdefault("relation", "related_to")
        attrs.setdefault("confidence", "INFERRED")
        graph.add_edge(source, target, **attrs)


def load_graph(path: Path) -> nx.MultiDiGraph:
    if not path.exists():
        return empty_graph()
    data = json.loads(path.read_text(encoding="utf-8"))
    graph = empty_graph()
    add_fragment(graph, data)
    return graph


def save_graph(graph: nx.MultiDiGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nodes = []
    for node_id, attrs in graph.nodes(data=True):
        item = dict(attrs)
        item["id"] = node_id
        nodes.append(item)
    edges = []
    for source, target, attrs in graph.edges(data=True):
        item = dict(attrs)
        item["source"] = source
        item["target"] = target
        edges.append(item)
    path.write_text(json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2), encoding="utf-8")


def neighbors(graph: nx.MultiDiGraph, query: str) -> list[dict]:
    q = query.casefold()
    matched = [n for n, a in graph.nodes(data=True) if q in str(a.get("label", n)).casefold()]
    results: list[dict] = []
    for node in matched:
        for _, target, attrs in graph.out_edges(node, data=True):
            results.append({
                "from": graph.nodes[node].get("label", node),
                "relation": attrs.get("relation", "related_to"),
                "to": graph.nodes[target].get("label", target),
                "chapter": attrs.get("chapter"),
                "source": attrs.get("source_file"),
            })
        for source, _, attrs in graph.in_edges(node, data=True):
            results.append({
                "from": graph.nodes[source].get("label", source),
                "relation": attrs.get("relation", "related_to"),
                "to": graph.nodes[node].get("label", node),
                "chapter": attrs.get("chapter"),
                "source": attrs.get("source_file"),
            })
    return results


def shortest_path(graph: nx.MultiDiGraph, a: str, b: str) -> list[str]:
    def find(label: str) -> str | None:
        q = label.casefold()
        for node, attrs in graph.nodes(data=True):
            if q in str(attrs.get("label", node)).casefold():
                return node
        return None

    source, target = find(a), find(b)
    if not source or not target:
        return []
    try:
        path = nx.shortest_path(graph.to_undirected(), source, target)
    except nx.NetworkXNoPath:
        return []
    return [str(graph.nodes[n].get("label", n)) for n in path]


def basic_conflicts(graph: nx.MultiDiGraph) -> list[str]:
    conflicts: list[str] = []
    ownership: dict[str, set[str]] = {}
    locations: dict[str, set[str]] = {}
    for source, target, attrs in graph.edges(data=True):
        relation = str(attrs.get("relation", "")).lower()
        if relation in {"owns", "owned_by", "possesses"}:
            ownership.setdefault(target, set()).add(source)
        if relation in {"located_at", "is_at"}:
            locations.setdefault(source, set()).add(target)
    for obj, owners in ownership.items():
        if len(owners) > 1:
            conflicts.append(f"{graph.nodes[obj].get('label', obj)} 同时有多个当前拥有者")
    for person, places in locations.items():
        if len(places) > 1:
            conflicts.append(f"{graph.nodes[person].get('label', person)} 同时出现在多个当前地点")
    return conflicts


def chapter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() in {".md", ".txt"} and path.is_file():
            yield path
