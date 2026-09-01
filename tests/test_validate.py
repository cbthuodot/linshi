import pytest

from storygraph.core import add_fragment, empty_graph
from storygraph.validate import validate_fragment


def test_rejects_missing_endpoint():
    fragment = {
        "nodes": [{"id": "a", "label": "A", "type": "character"}],
        "edges": [
            {
                "source": "a",
                "target": "missing",
                "relation": "knows",
                "confidence": "EXTRACTED",
            }
        ],
    }
    errors = validate_fragment(fragment)
    assert any("does not match any node id" in error for error in errors)


def test_add_fragment_fails_loudly_on_invalid_data():
    graph = empty_graph()
    with pytest.raises(ValueError):
        add_fragment(graph, {"nodes": [], "edges": [{"source": "a"}]})


def test_confidence_labels_match_graphify_pattern():
    graph = empty_graph()
    add_fragment(
        graph,
        {
            "nodes": [
                {"id": "a", "label": "A", "type": "character"},
                {"id": "b", "label": "B", "type": "character"},
            ],
            "edges": [
                {
                    "source": "a",
                    "target": "b",
                    "relation": "knows",
                    "confidence": "AMBIGUOUS",
                }
            ],
        },
    )
    assert graph.edges["a", "b", 0]["confidence"] == "AMBIGUOUS"


def test_rejects_unknown_story_type_and_relation():
    fragment = {
        "nodes": [
            {"id": "a", "label": "A", "type": "spaceship"},
            {"id": "b", "label": "B", "type": "character"},
        ],
        "edges": [
            {
                "source": "a",
                "target": "b",
                "relation": "teleports_into",
                "confidence": "EXTRACTED",
            }
        ],
    }
    errors = validate_fragment(fragment)
    assert any("invalid type" in error for error in errors)
    assert any("invalid relation" in error for error in errors)


def test_rejects_time_window_that_runs_backward():
    fragment = {
        "nodes": [
            {"id": "a", "label": "A", "type": "character"},
            {"id": "b", "label": "B", "type": "character"},
        ],
        "edges": [
            {
                "source": "a",
                "target": "b",
                "relation": "trusts",
                "confidence": "EXTRACTED",
                "valid_from": 5,
                "valid_to": 3,
            }
        ],
    }
    errors = validate_fragment(fragment)
    assert any("valid_to cannot be earlier" in error for error in errors)
