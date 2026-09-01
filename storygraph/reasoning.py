from __future__ import annotations

import networkx as nx

from .model import entity_terms, normalize_name

KNOWLEDGE_RELATIONS = {"does_not_know", "learns", "knows"}
OPPOSING_RELATIONS = {
    "trusts": "distrusts",
    "distrusts": "trusts",
    "loves": "hates",
    "hates": "loves",
    "ally_of": "enemy_of",
    "enemy_of": "ally_of",
}


def resolve_entity(graph: nx.MultiDiGraph, query: str) -> str | None:
    q = normalize_name(query)
    if not q:
        return None
    exact: list[str] = []
    partial: list[str] = []
    for node_id, attrs in graph.nodes(data=True):
        terms = entity_terms(dict(attrs))
        if q in terms:
            exact.append(node_id)
        elif any(q in term for term in terms):
            partial.append(node_id)
    candidates = exact or partial
    return candidates[0] if len(candidates) == 1 else None


def _chapter(attrs: dict) -> int | None:
    value = attrs.get("chapter_index")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _active_at(attrs: dict, chapter: int) -> bool:
    start = attrs.get("valid_from")
    end = attrs.get("valid_to")
    event_chapter = _chapter(attrs)
    if isinstance(start, int) and not isinstance(start, bool) and chapter < start:
        return False
    if isinstance(end, int) and not isinstance(end, bool) and chapter > end:
        return False
    if start is None and event_chapter is not None and event_chapter > chapter:
        return False
    return True


def _successor_chapter(
    edge_rows: list[tuple[str, str, dict]],
    source: str,
    target: str,
    attrs: dict,
) -> int | None:
    """Infer when an open-ended state is replaced by a later state.

    We only infer an end when the old edge has no explicit valid_to. An explicit
    overlapping validity window remains authoritative and can therefore be
    reported as a real conflict.
    """
    if attrs.get("valid_to") is not None:
        return None
    current = _chapter(attrs)
    if current is None:
        return None
    relation = str(attrs.get("relation", ""))
    successors: list[int] = []
    for source2, target2, attrs2 in edge_rows:
        later = _chapter(attrs2)
        if later is None or later <= current:
            continue
        relation2 = str(attrs2.get("relation", ""))
        if relation == "owns" and relation2 == "owns" and target2 == target:
            successors.append(later)
        elif relation == "located_at" and relation2 == "located_at" and source2 == source:
            successors.append(later)
        elif (
            relation in OPPOSING_RELATIONS
            and source2 == source
            and target2 == target
            and relation2 == OPPOSING_RELATIONS[relation]
        ):
            successors.append(later)
    return min(successors) if successors else None


def _effectively_active_edges(
    graph: nx.MultiDiGraph, chapter: int
) -> list[tuple[str, str, dict]]:
    edge_rows = [(source, target, dict(attrs)) for source, target, attrs in graph.edges(data=True)]
    active: list[tuple[str, str, dict]] = []
    for source, target, attrs in edge_rows:
        if not _active_at(attrs, chapter):
            continue
        successor = _successor_chapter(edge_rows, source, target, attrs)
        if successor is not None and chapter >= successor:
            continue
        active.append((source, target, attrs))
    return active


def knowledge_state(
    graph: nx.MultiDiGraph,
    character: str,
    secret: str,
    chapter: int,
) -> dict:
    char_id = resolve_entity(graph, character)
    secret_id = resolve_entity(graph, secret)
    result = {
        "character": character,
        "secret": secret,
        "chapter": chapter,
        "state": "unknown",
        "evidence": [],
    }
    if char_id is None or secret_id is None:
        return result

    events: list[tuple[int, str, dict]] = []
    for _, target, attrs in graph.out_edges(char_id, data=True):
        if target != secret_id:
            continue
        relation = attrs.get("relation")
        event_chapter = _chapter(dict(attrs))
        if relation in KNOWLEDGE_RELATIONS and event_chapter is not None and event_chapter <= chapter:
            events.append((event_chapter, str(relation), dict(attrs)))
    events.sort(key=lambda item: (item[0], 0 if item[1] == "does_not_know" else 1))

    state = "unknown"
    evidence: list[dict] = []
    for event_chapter, relation, attrs in events:
        if relation == "does_not_know":
            state = "does_not_know"
        elif relation in {"learns", "knows"}:
            state = "knows"
        evidence.append(
            {
                "chapter_index": event_chapter,
                "relation": relation,
                "chapter": attrs.get("chapter"),
                "evidence": attrs.get("evidence"),
                "source_file": attrs.get("source_file"),
            }
        )
    result["state"] = state
    result["evidence"] = evidence
    return result


def active_relationships(graph: nx.MultiDiGraph, query: str, chapter: int) -> list[dict]:
    node_id = resolve_entity(graph, query)
    if node_id is None:
        return []
    rows: list[dict] = []
    for source, target, attrs in _effectively_active_edges(graph, chapter):
        if source != node_id and target != node_id:
            continue
        rows.append(
            {
                "from": graph.nodes[source].get("label", source),
                "relation": attrs.get("relation", "related_to"),
                "to": graph.nodes[target].get("label", target),
                "chapter_index": attrs.get("chapter_index"),
                "valid_from": attrs.get("valid_from"),
                "valid_to": attrs.get("valid_to"),
                "confidence": attrs.get("confidence"),
                "evidence": attrs.get("evidence"),
            }
        )
    rows.sort(key=lambda row: (str(row["relation"]), str(row["from"]), str(row["to"])))
    return rows


def unresolved_foreshadowing(graph: nx.MultiDiGraph, at_chapter: int | None = None) -> list[dict]:
    unresolved: list[dict] = []
    for node_id, attrs in graph.nodes(data=True):
        if attrs.get("type") not in {"foreshadow", "clue"}:
            continue
        planted = attrs.get("chapter_index")
        if at_chapter is not None and isinstance(planted, int) and planted > at_chapter:
            continue
        paid = False
        for _, _, edge_attrs in graph.out_edges(node_id, data=True):
            if edge_attrs.get("relation") != "pays_off":
                continue
            payoff_chapter = _chapter(dict(edge_attrs))
            if at_chapter is None or payoff_chapter is None or payoff_chapter <= at_chapter:
                paid = True
                break
        if not paid:
            unresolved.append(
                {
                    "id": node_id,
                    "label": attrs.get("label", node_id),
                    "type": attrs.get("type"),
                    "chapter_index": planted,
                    "source_file": attrs.get("source_file"),
                }
            )
    unresolved.sort(
        key=lambda item: (
            item["chapter_index"] if isinstance(item["chapter_index"], int) else 10**12,
            item["label"],
        )
    )
    return unresolved


def story_groups(graph: nx.MultiDiGraph) -> list[dict]:
    if graph.number_of_nodes() == 0:
        return []
    simple = nx.Graph()
    simple.add_nodes_from(graph.nodes)
    simple.add_edges_from((source, target) for source, target in graph.edges())
    if simple.number_of_edges() == 0:
        communities = [{node_id} for node_id in simple.nodes]
    else:
        communities = list(nx.community.greedy_modularity_communities(simple))
    groups: list[dict] = []
    for members in communities:
        ordered = sorted(
            members,
            key=lambda node_id: (
                -simple.degree(node_id),
                str(graph.nodes[node_id].get("label", node_id)),
            ),
        )
        groups.append(
            {
                "size": len(ordered),
                "members": [graph.nodes[node_id].get("label", node_id) for node_id in ordered],
                "central": graph.nodes[ordered[0]].get("label", ordered[0]),
            }
        )
    groups.sort(key=lambda item: (-item["size"], item["central"]))
    return groups


def consistency_issues(graph: nx.MultiDiGraph) -> list[dict]:
    issues: list[dict] = []

    # Explicit contradiction edges are always surfaced.
    for source, target, attrs in graph.edges(data=True):
        if attrs.get("relation") == "contradicts":
            issues.append(
                {
                    "kind": "explicit_contradiction",
                    "chapter_index": _chapter(dict(attrs)),
                    "message": f"{graph.nodes[source].get('label', source)} 与 {graph.nodes[target].get('label', target)} 被标记为互相矛盾",
                }
            )

    # Revealing a secret requires a known/learned state by that chapter.
    for source, target, attrs in graph.edges(data=True):
        if attrs.get("relation") != "reveals":
            continue
        if graph.nodes[source].get("type") != "character" or graph.nodes[target].get("type") != "secret":
            continue
        chapter = _chapter(dict(attrs))
        if chapter is None:
            continue
        state = knowledge_state(
            graph,
            str(graph.nodes[source].get("label", source)),
            str(graph.nodes[target].get("label", target)),
            chapter,
        )
        if state["state"] != "knows":
            issues.append(
                {
                    "kind": "knowledge_leak",
                    "chapter_index": chapter,
                    "message": f"{graph.nodes[source].get('label', source)} 在第{chapter}章透露了自己尚未被记录为知道的秘密：{graph.nodes[target].get('label', target)}",
                }
            )

    edge_rows = [(source, target, dict(attrs)) for source, target, attrs in graph.edges(data=True)]
    chapter_candidates = {
        ch
        for _, _, attrs in edge_rows
        for ch in [_chapter(attrs), attrs.get("valid_from"), attrs.get("valid_to")]
        if isinstance(ch, int) and not isinstance(ch, bool)
    }

    if chapter_candidates:
        for chapter in range(min(chapter_candidates), max(chapter_candidates) + 1):
            active = _effectively_active_edges(graph, chapter)

            # Opposing relationships only conflict if both remain effectively active.
            active_keys = {(source, target, str(attrs.get("relation", ""))) for source, target, attrs in active}
            seen_relationship_pairs: set[tuple[str, str, str, str]] = set()
            for source, target, attrs in active:
                relation = str(attrs.get("relation", ""))
                opposite = OPPOSING_RELATIONS.get(relation)
                if not opposite or (source, target, opposite) not in active_keys:
                    continue
                pair = (source, target, *sorted((relation, opposite)))
                if pair in seen_relationship_pairs:
                    continue
                seen_relationship_pairs.add(pair)
                issues.append(
                    {
                        "kind": "relationship_conflict",
                        "chapter_index": chapter,
                        "message": f"{graph.nodes[source].get('label', source)} 对 {graph.nodes[target].get('label', target)} 在第{chapter}章存在同时有效的 {relation}/{opposite} 关系",
                    }
                )

            owners: dict[str, set[str]] = {}
            locations: dict[str, set[str]] = {}
            for source, target, attrs in active:
                relation = attrs.get("relation")
                if relation == "owns":
                    owners.setdefault(target, set()).add(source)
                elif relation == "located_at":
                    locations.setdefault(source, set()).add(target)
            for obj, owner_ids in owners.items():
                if len(owner_ids) > 1:
                    labels = ", ".join(sorted(str(graph.nodes[x].get("label", x)) for x in owner_ids))
                    issues.append(
                        {
                            "kind": "ownership_conflict",
                            "chapter_index": chapter,
                            "message": f"{graph.nodes[obj].get('label', obj)} 在第{chapter}章同时有多个主人：{labels}",
                        }
                    )
            for person, place_ids in locations.items():
                if len(place_ids) > 1:
                    labels = ", ".join(sorted(str(graph.nodes[x].get("label", x)) for x in place_ids))
                    issues.append(
                        {
                            "kind": "location_conflict",
                            "chapter_index": chapter,
                            "message": f"{graph.nodes[person].get('label', person)} 在第{chapter}章同时处于多个地点：{labels}",
                        }
                    )

    unique: dict[tuple[str, int | None, str], dict] = {}
    for issue in issues:
        key = (str(issue["kind"]), issue.get("chapter_index"), str(issue["message"]))
        unique[key] = issue
    return sorted(
        unique.values(),
        key=lambda item: (
            item.get("chapter_index") if isinstance(item.get("chapter_index"), int) else 10**12,
            str(item.get("kind")),
            str(item.get("message")),
        ),
    )
