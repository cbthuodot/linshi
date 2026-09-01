from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from .model import entity_terms, normalize_name
from .validate import assert_valid

SCHEMA_VERSION = 2


def empty_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.graph.update({"schema_version": SCHEMA_VERSION, "kind": "storygraph"})
    return graph


def _alias_index(graph: nx.MultiDiGraph) -> dict[tuple[str, str], set[str]]:
    index: dict[tuple[str, str], set[str]] = {}
    for node_id, attrs in graph.nodes(data=True):
        node_type = str(attrs.get("type", "concept"))
        for term in entity_terms(dict(attrs)):
            index.setdefault((node_type, term), set()).add(node_id)
    return index


def _merge_node(graph: nx.MultiDiGraph, node_id: str, incoming: dict) -> None:
    attrs = {k: v for k, v in incoming.items() if k != "id" and v is not None}
    if node_id not in graph:
        graph.add_node(node_id, **attrs)
        return

    existing = dict(graph.nodes[node_id])
    old_type = existing.get("type")
    new_type = attrs.get("type")
    if old_type and new_type and old_type != new_type:
        raise ValueError(
            f"Entity '{node_id}' cannot change type from '{old_type}' to '{new_type}'"
        )

    canonical_label = existing.get("label") or attrs.get("label") or node_id
    alias_values: list[str] = []
    for source in (existing.get("aliases", []), attrs.get("aliases", [])):
        if isinstance(source, list):
            alias_values.extend(str(value) for value in source if str(value).strip())
    incoming_label = attrs.get("label")
    if isinstance(incoming_label, str) and incoming_label != canonical_label:
        alias_values.append(incoming_label)
    old_label = existing.get("label")
    if isinstance(old_label, str) and old_label != canonical_label:
        alias_values.append(old_label)

    aliases: list[str] = []
    seen_terms: set[str] = {normalize_name(str(canonical_label))}
    for alias in alias_values:
        term = normalize_name(alias)
        if term and term not in seen_terms:
            aliases.append(alias)
            seen_terms.add(term)

    source_files: list[str] = []
    for source in (
        existing.get("source_files", []),
        [existing.get("source_file")] if existing.get("source_file") else [],
        attrs.get("source_files", []),
        [attrs.get("source_file")] if attrs.get("source_file") else [],
    ):
        if isinstance(source, list):
            for item in source:
                if isinstance(item, str) and item and item not in source_files:
                    source_files.append(item)

    merged = dict(existing)
    for key, value in attrs.items():
        if key in {"label", "aliases", "source_file", "source_files", "first_chapter_index"}:
            continue
        merged[key] = value
    merged["label"] = canonical_label
    if aliases:
        merged["aliases"] = aliases
    if source_files:
        merged["source_files"] = source_files
        merged.setdefault("source_file", source_files[0])

    chapter_values: list[int] = []
    for value in (
        existing.get("first_chapter_index"),
        existing.get("chapter_index"),
        attrs.get("first_chapter_index"),
        attrs.get("chapter_index"),
    ):
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            chapter_values.append(value)
    if chapter_values:
        merged["first_chapter_index"] = min(chapter_values)

    graph.nodes[node_id].clear()
    graph.nodes[node_id].update(merged)


def add_fragment(graph: nx.MultiDiGraph, fragment: dict) -> dict[str, str]:
    """Validate and merge a narrative fragment, returning incoming-id remaps."""
    assert_valid(fragment, existing_node_ids=set(graph.nodes))
    index = _alias_index(graph)
    id_map: dict[str, str] = {}

    for node in fragment["nodes"]:
        incoming_id = node["id"]
        node_type = node["type"]
        canonical_id = incoming_id

        if incoming_id not in graph:
            candidates: set[str] = set()
            for term in entity_terms(node):
                candidates.update(index.get((node_type, term), set()))
            if len(candidates) == 1:
                canonical_id = next(iter(candidates))
            elif len(candidates) > 1:
                raise ValueError(
                    f"Alias for '{node.get('label', incoming_id)}' matches multiple existing entities: "
                    + ", ".join(sorted(candidates))
                )

        id_map[incoming_id] = canonical_id
        _merge_node(graph, canonical_id, node)
        for term in entity_terms(dict(graph.nodes[canonical_id])):
            index.setdefault((node_type, term), set()).add(canonical_id)

    for edge in fragment["edges"]:
        source = id_map.get(edge["source"], edge["source"])
        target = id_map.get(edge["target"], edge["target"])
        attrs = {k: v for k, v in edge.items() if k not in {"source", "target", "key"}}
        key = edge.get("key")
        if key is None:
            graph.add_edge(source, target, **attrs)
        else:
            graph.add_edge(source, target, key=str(key), **attrs)
    return id_map


def graph_to_data(graph: nx.MultiDiGraph) -> dict:
    nodes = []
    for node_id, attrs in sorted(graph.nodes(data=True), key=lambda item: str(item[0])):
        nodes.append({"id": node_id, **dict(attrs)})

    edges = []
    for source, target, key, attrs in graph.edges(keys=True, data=True):
        edges.append({"source": source, "target": target, "key": str(key), **dict(attrs)})
    edges.sort(
        key=lambda item: (
            item.get("chapter_index") if isinstance(item.get("chapter_index"), int) else 10**12,
            str(item["source"]),
            str(item["target"]),
            str(item["key"]),
        )
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "graph": {"kind": graph.graph.get("kind", "storygraph")},
        "nodes": nodes,
        "edges": edges,
    }


def graph_from_data(data: dict) -> nx.MultiDiGraph:
    version = data.get("schema_version", 1)
    if version not in {1, SCHEMA_VERSION}:
        raise ValueError(f"Unsupported StoryGraph schema version: {version}")
    fragment = {"nodes": data.get("nodes", []), "edges": data.get("edges", [])}
    graph = empty_graph()
    graph_meta = data.get("graph")
    if isinstance(graph_meta, dict):
        graph.graph.update(graph_meta)
    add_fragment(graph, fragment)
    graph.graph["schema_version"] = SCHEMA_VERSION
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
    q = normalize_name(query)
    if not q:
        return []
    matches: list[str] = []
    for node_id, attrs in graph.nodes(data=True):
        terms = entity_terms(dict(attrs))
        if any(q in term for term in terms):
            matches.append(node_id)
    return matches


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
                    "chapter": attrs.get("chapter"),
                    "chapter_index": attrs.get("chapter_index"),
                    "valid_from": attrs.get("valid_from"),
                    "valid_to": attrs.get("valid_to"),
                    "source_file": attrs.get("source_file"),
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
                    "chapter": attrs.get("chapter"),
                    "chapter_index": attrs.get("chapter_index"),
                    "valid_from": attrs.get("valid_from"),
                    "valid_to": attrs.get("valid_to"),
                    "source_file": attrs.get("source_file"),
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


def story_history(graph: nx.MultiDiGraph, query: str) -> list[dict]:
    """Return all known relationships around an entity in story order."""
    rows = neighbors(graph, query)
    rows.sort(
        key=lambda row: (
            row["chapter_index"] if isinstance(row.get("chapter_index"), int) else 10**12,
            row["relation"],
            row["from"],
            row["to"],
        )
    )
    return rows
