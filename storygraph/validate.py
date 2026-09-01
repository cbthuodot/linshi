"""Validation for StoryGraph graph fragments.

Adapted from Graphify's validate-before-build pattern. StoryGraph keeps the
schema deliberately small here; narrative-specific fields are added in Phase 2.
"""
from __future__ import annotations

VALID_CONFIDENCES = {"EXTRACTED", "INFERRED", "AMBIGUOUS"}
REQUIRED_NODE_FIELDS = {"id", "label", "type"}
REQUIRED_EDGE_FIELDS = {"source", "target", "relation", "confidence"}


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_fragment(data: object) -> list[str]:
    """Return validation errors; an empty list means the fragment is valid."""
    if not isinstance(data, dict):
        return ["Graph fragment must be a JSON object"]

    errors: list[str] = []
    node_ids: set[str] = set()

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        errors.append("'nodes' must be a list")
    else:
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                errors.append(f"Node {i} must be an object")
                continue
            for field in REQUIRED_NODE_FIELDS:
                if field not in node:
                    errors.append(f"Node {i} missing required field '{field}'")
            node_id = node.get("id")
            if "id" in node and not _nonempty_string(node_id):
                errors.append(f"Node {i} id must be a non-empty string")
            elif isinstance(node_id, str):
                if node_id in node_ids:
                    errors.append(f"Duplicate node id '{node_id}'")
                node_ids.add(node_id)
            if "label" in node and not _nonempty_string(node.get("label")):
                errors.append(f"Node {i} label must be a non-empty string")
            if "type" in node and not _nonempty_string(node.get("type")):
                errors.append(f"Node {i} type must be a non-empty string")

    edges = data.get("edges")
    if not isinstance(edges, list):
        errors.append("'edges' must be a list")
    else:
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(f"Edge {i} must be an object")
                continue
            for field in REQUIRED_EDGE_FIELDS:
                if field not in edge:
                    errors.append(f"Edge {i} missing required field '{field}'")
            for endpoint in ("source", "target"):
                value = edge.get(endpoint)
                if endpoint in edge and not _nonempty_string(value):
                    errors.append(f"Edge {i} {endpoint} must be a non-empty string")
                elif isinstance(value, str) and node_ids and value not in node_ids:
                    errors.append(f"Edge {i} {endpoint} '{value}' does not match any node id")
            relation = edge.get("relation")
            if "relation" in edge and not _nonempty_string(relation):
                errors.append(f"Edge {i} relation must be a non-empty string")
            confidence = edge.get("confidence")
            if "confidence" in edge and confidence not in VALID_CONFIDENCES:
                errors.append(
                    f"Edge {i} has invalid confidence '{confidence}'; "
                    f"expected one of {sorted(VALID_CONFIDENCES)}"
                )
    return errors


def assert_valid(data: object) -> None:
    errors = validate_fragment(data)
    if errors:
        message = f"StoryGraph fragment has {len(errors)} error(s):\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        raise ValueError(message)
