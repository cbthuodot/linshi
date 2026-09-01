"""Validation for StoryGraph graph fragments.

The validation-before-build pattern follows Graphify's defensive approach, but
this schema is narrative-specific.
"""
from __future__ import annotations

from .model import CONFIDENCE_LEVELS, NODE_TYPES, RELATION_TYPES

REQUIRED_NODE_FIELDS = {"id", "label", "type"}
REQUIRED_EDGE_FIELDS = {"source", "target", "relation", "confidence"}
CHAPTER_INT_FIELDS = {"chapter_index", "valid_from", "valid_to", "learned_at", "revealed_at"}


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _chapter_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_fragment(data: object, *, existing_node_ids: set[str] | None = None) -> list[str]:
    """Return validation errors; an empty list means the fragment is valid."""
    if not isinstance(data, dict):
        return ["Graph fragment must be a JSON object"]

    errors: list[str] = []
    node_ids: set[str] = set(existing_node_ids or set())
    new_node_ids: set[str] = set()

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
                if node_id in new_node_ids:
                    errors.append(f"Duplicate node id '{node_id}'")
                new_node_ids.add(node_id)
                node_ids.add(node_id)
            if "label" in node and not _nonempty_string(node.get("label")):
                errors.append(f"Node {i} label must be a non-empty string")
            node_type = node.get("type")
            if "type" in node and node_type not in NODE_TYPES:
                errors.append(
                    f"Node {i} has invalid type '{node_type}'; expected one of {sorted(NODE_TYPES)}"
                )
            aliases = node.get("aliases")
            if aliases is not None:
                if not isinstance(aliases, list):
                    errors.append(f"Node {i} aliases must be a list")
                else:
                    for alias in aliases:
                        if not _nonempty_string(alias):
                            errors.append(f"Node {i} aliases must contain only non-empty strings")
                            break
            for field in ("source_file", "chapter", "scene", "evidence"):
                if field in node and node[field] is not None and not _nonempty_string(node[field]):
                    errors.append(f"Node {i} {field} must be a non-empty string when present")
            for field in CHAPTER_INT_FIELDS:
                if field in node and node[field] is not None and not _chapter_int(node[field]):
                    errors.append(f"Node {i} {field} must be a non-negative integer when present")

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
                elif isinstance(value, str) and value not in node_ids:
                    errors.append(f"Edge {i} {endpoint} '{value}' does not match any node id")
            relation = edge.get("relation")
            if "relation" in edge and relation not in RELATION_TYPES:
                errors.append(
                    f"Edge {i} has invalid relation '{relation}'; expected a supported story relation"
                )
            confidence = edge.get("confidence")
            if "confidence" in edge and confidence not in CONFIDENCE_LEVELS:
                errors.append(
                    f"Edge {i} has invalid confidence '{confidence}'; "
                    f"expected one of {sorted(CONFIDENCE_LEVELS)}"
                )
            score = edge.get("confidence_score")
            if score is not None:
                if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 1:
                    errors.append(f"Edge {i} confidence_score must be between 0 and 1")
            for field in ("source_file", "chapter", "scene", "evidence"):
                if field in edge and edge[field] is not None and not _nonempty_string(edge[field]):
                    errors.append(f"Edge {i} {field} must be a non-empty string when present")
            for field in CHAPTER_INT_FIELDS:
                if field in edge and edge[field] is not None and not _chapter_int(edge[field]):
                    errors.append(f"Edge {i} {field} must be a non-negative integer when present")
            start = edge.get("valid_from")
            end = edge.get("valid_to")
            if _chapter_int(start) and _chapter_int(end) and end < start:
                errors.append(f"Edge {i} valid_to cannot be earlier than valid_from")
    return errors


def assert_valid(data: object, *, existing_node_ids: set[str] | None = None) -> None:
    errors = validate_fragment(data, existing_node_ids=existing_node_ids)
    if errors:
        message = f"StoryGraph fragment has {len(errors)} error(s):\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        raise ValueError(message)
