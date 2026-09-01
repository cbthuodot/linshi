from storygraph.core import add_fragment, empty_graph
from storygraph.reasoning import (
    active_relationships,
    consistency_issues,
    knowledge_state,
    story_groups,
    unresolved_foreshadowing,
)


def node(node_id: str, label: str, kind: str, chapter: int = 1):
    return {"id": node_id, "label": label, "type": kind, "chapter_index": chapter}


def edge(source: str, target: str, relation: str, chapter: int, **extra):
    data = {
        "source": source,
        "target": target,
        "relation": relation,
        "confidence": "EXTRACTED",
        "chapter_index": chapter,
    }
    data.update(extra)
    return data


def test_knowledge_state_changes_by_chapter():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                node("chen", "陈默", "character"),
                node("secret", "白塔印记", "secret"),
            ],
            "edges": [
                edge("chen", "secret", "does_not_know", 1),
                edge("chen", "secret", "learns", 2, learned_at=2),
                edge("chen", "secret", "knows", 2, valid_from=2),
            ],
        },
    )
    assert knowledge_state(graph, "陈默", "白塔印记", 1)["state"] == "does_not_know"
    assert knowledge_state(graph, "陈默", "白塔印记", 2)["state"] == "knows"


def test_active_state_respects_validity_window():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                node("lin", "林夏", "character"),
                node("key", "银色钥匙", "object"),
                node("tower", "旧塔", "location"),
            ],
            "edges": [
                edge("lin", "key", "owns", 1, valid_from=1, valid_to=1),
                edge("lin", "tower", "located_at", 2, valid_from=2),
            ],
        },
    )
    at_one = active_relationships(graph, "林夏", 1)
    at_two = active_relationships(graph, "林夏", 2)
    assert any(row["relation"] == "owns" for row in at_one)
    assert not any(row["relation"] == "owns" for row in at_two)
    assert any(row["relation"] == "located_at" for row in at_two)


def test_unresolved_foreshadowing_changes_after_payoff():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                node("foreshadow", "地图上的白塔符号", "foreshadow", 1),
                node("entrance", "旧塔密门", "secret", 3),
            ],
            "edges": [
                edge("foreshadow", "entrance", "pays_off", 3),
            ],
        },
    )
    assert [item["id"] for item in unresolved_foreshadowing(graph, 2)] == ["foreshadow"]
    assert unresolved_foreshadowing(graph, 3) == []


def test_checker_catches_planted_errors():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                node("lin", "林夏", "character"),
                node("chen", "陈默", "character"),
                node("secret", "王家秘密", "secret"),
                node("key", "银色钥匙", "object"),
                node("north", "北港", "location"),
                node("tower", "旧塔", "location"),
            ],
            "edges": [
                edge("lin", "secret", "reveals", 1),
                edge("lin", "secret", "learns", 2, learned_at=2),
                edge("lin", "secret", "knows", 2, valid_from=2),
                edge("lin", "key", "owns", 1, valid_from=1),
                edge("chen", "key", "owns", 2, valid_from=2),
                edge("lin", "north", "located_at", 2, valid_from=2),
                edge("lin", "tower", "located_at", 2, valid_from=2),
                edge("lin", "chen", "trusts", 1, valid_from=1, valid_to=3),
                edge("lin", "chen", "distrusts", 2, valid_from=2, valid_to=2),
            ],
        },
    )
    kinds = {issue["kind"] for issue in consistency_issues(graph)}
    assert "knowledge_leak" in kinds
    assert "ownership_conflict" in kinds
    assert "location_conflict" in kinds
    assert "relationship_conflict" in kinds


def test_checker_does_not_flag_correct_transitions():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                node("lin", "林夏", "character"),
                node("chen", "陈默", "character"),
                node("secret", "王家秘密", "secret"),
                node("key", "银色钥匙", "object"),
                node("north", "北港", "location"),
                node("tower", "旧塔", "location"),
            ],
            "edges": [
                edge("lin", "secret", "learns", 1, learned_at=1),
                edge("lin", "secret", "knows", 1, valid_from=1),
                edge("lin", "secret", "reveals", 2),
                edge("lin", "key", "owns", 1, valid_from=1, valid_to=1),
                edge("chen", "key", "owns", 2, valid_from=2),
                edge("lin", "north", "located_at", 1, valid_from=1, valid_to=1),
                edge("lin", "tower", "located_at", 2, valid_from=2),
                edge("lin", "chen", "distrusts", 1, valid_from=1, valid_to=1),
                edge("lin", "chen", "trusts", 2, valid_from=2),
            ],
        },
    )
    assert consistency_issues(graph) == []


def test_story_groups_find_separate_story_clusters():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                node("a", "林夏", "character"),
                node("b", "陈默", "character"),
                node("key", "银色钥匙", "object"),
                node("x", "王五", "character"),
                node("org", "白塔组织", "organization"),
            ],
            "edges": [
                edge("a", "b", "trusts", 1),
                edge("b", "key", "owns", 1),
                edge("x", "org", "member_of", 1),
            ],
        },
    )
    groups = story_groups(graph)
    assert [group["size"] for group in groups] == [3, 2]
