from __future__ import annotations

import re
from pathlib import Path

import networkx as nx

from .core import add_fragment
from .validate import validate_fragment


def _normalize_text(value: str) -> str:
    """Normalize whitespace for evidence matching without changing wording."""
    return re.sub(r"\s+", "", value).strip()


def _same_source(expected: Path, value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    expected_text = expected.as_posix()
    candidate = Path(value).as_posix()
    if candidate == expected_text:
        return True
    # Permit an agent to use a repo-relative path while the caller supplies an
    # absolute path, but never accept a different filename/path suffix.
    return expected_text.endswith("/" + candidate) or candidate.endswith("/" + expected_text)


def chapter_extraction_errors(
    graph: nx.MultiDiGraph,
    fragment: object,
    *,
    chapter_path: Path,
    chapter_index: int,
    chapter_label: str | None = None,
) -> list[str]:
    """Validate both graph shape and grounding against the source chapter."""
    errors = validate_fragment(fragment, existing_node_ids=set(graph.nodes))
    if not isinstance(fragment, dict):
        return errors

    if not chapter_path.exists() or not chapter_path.is_file():
        errors.append(f"Chapter file does not exist: {chapter_path}")
        return errors
    if isinstance(chapter_index, bool) or not isinstance(chapter_index, int) or chapter_index < 0:
        errors.append("chapter_index must be a non-negative integer")
        return errors

    text = chapter_path.read_text(encoding="utf-8")
    normalized_text = _normalize_text(text)

    nodes = fragment.get("nodes")
    if isinstance(nodes, list):
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            source_file = node.get("source_file")
            if source_file is not None and not _same_source(chapter_path, source_file):
                errors.append(f"Node {i} source_file does not match the chapter being read")
            value = node.get("chapter_index")
            if value is not None and value != chapter_index:
                errors.append(f"Node {i} chapter_index must equal {chapter_index}")
            if chapter_label is not None and node.get("chapter") is not None and node.get("chapter") != chapter_label:
                errors.append(f"Node {i} chapter must equal '{chapter_label}'")

    edges = fragment.get("edges")
    if isinstance(edges, list):
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            if not _same_source(chapter_path, edge.get("source_file")):
                errors.append(f"Edge {i} must include source_file for the chapter being read")
            if edge.get("chapter_index") != chapter_index:
                errors.append(f"Edge {i} chapter_index must equal {chapter_index}")
            if chapter_label is not None and edge.get("chapter") != chapter_label:
                errors.append(f"Edge {i} chapter must equal '{chapter_label}'")

            evidence = edge.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(f"Edge {i} must include a non-empty evidence quote")
            elif _normalize_text(evidence) not in normalized_text:
                errors.append(f"Edge {i} evidence was not found in the source chapter")

    return errors


def add_chapter_fragment(
    graph: nx.MultiDiGraph,
    fragment: dict,
    *,
    chapter_path: Path,
    chapter_index: int,
    chapter_label: str | None = None,
) -> dict[str, str]:
    """Reject ungrounded extraction, then merge it into the story graph."""
    errors = chapter_extraction_errors(
        graph,
        fragment,
        chapter_path=chapter_path,
        chapter_index=chapter_index,
        chapter_label=chapter_label,
    )
    if errors:
        message = f"Chapter extraction has {len(errors)} error(s):\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        raise ValueError(message)
    return add_fragment(graph, fragment)
