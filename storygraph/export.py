from __future__ import annotations

from pathlib import Path

import networkx as nx

from .core import save_graph


def to_json(graph: nx.MultiDiGraph, path: Path) -> None:
    """Write the stable StoryGraph JSON interchange format."""
    save_graph(graph, path)
