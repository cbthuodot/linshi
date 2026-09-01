from __future__ import annotations

import hashlib
import json
from pathlib import Path

import networkx as nx

from .core import add_fragment, empty_graph, load_graph, save_graph
from .extraction import add_chapter_fragment

MANIFEST_VERSION = 1


def _manifest_path(graph_path: Path) -> Path:
    return graph_path.parent / "manifest.json"


def _fragments_dir(graph_path: Path) -> Path:
    return graph_path.parent / "fragments"


def _chapter_hash(chapter_path: Path) -> str:
    digest = hashlib.sha256()
    with chapter_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_text(path: Path) -> str:
    return path.as_posix()


def _same_source(a: str, b: str) -> bool:
    left = Path(a).as_posix()
    right = Path(b).as_posix()
    return left == right or left.endswith("/" + right) or right.endswith("/" + left)


def load_manifest(graph_path: Path) -> dict:
    path = _manifest_path(graph_path)
    if not path.exists():
        return {"version": MANIFEST_VERSION, "chapters": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != MANIFEST_VERSION:
        raise ValueError("Unsupported or malformed StoryGraph manifest")
    chapters = data.get("chapters")
    if not isinstance(chapters, list):
        raise ValueError("StoryGraph manifest chapters must be a list")
    return data


def _save_manifest(graph_path: Path, manifest: dict) -> None:
    path = _manifest_path(graph_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fragment_relpath(chapter_index: int, source_file: str) -> str:
    suffix = hashlib.sha1(source_file.encode("utf-8")).hexdigest()[:10]
    return f"fragments/{chapter_index:06d}-{suffix}.json"


def _write_fragment(graph_path: Path, relpath: str, fragment: dict) -> None:
    path = graph_path.parent / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fragment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_fragment(graph_path: Path, entry: dict) -> dict:
    relpath = entry.get("fragment_file")
    if not isinstance(relpath, str) or not relpath:
        raise ValueError("Manifest chapter is missing fragment_file")
    path = graph_path.parent / relpath
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Cached chapter fragment must be a JSON object: {path}")
    return data


def _sorted_entries(entries: list[dict]) -> list[dict]:
    return sorted(
        entries,
        key=lambda item: (
            item.get("chapter_index") if isinstance(item.get("chapter_index"), int) else 10**12,
            str(item.get("source_file", "")),
        ),
    )


def _require_trackable_graph(graph_path: Path, manifest: dict) -> None:
    if manifest.get("chapters"):
        return
    graph = load_graph(graph_path)
    if graph.number_of_nodes() or graph.number_of_edges():
        raise ValueError(
            "This graph contains untracked facts from an older StoryGraph version. "
            "Create a fresh output folder and ingest the chapters with add-chapter before using safe updates."
        )


def ingest_chapter(
    *,
    graph_path: Path,
    chapter_path: Path,
    fragment: dict,
    chapter_index: int,
    chapter_label: str | None = None,
) -> nx.MultiDiGraph:
    """Add a new grounded chapter and persist its replayable fragment."""
    manifest = load_manifest(graph_path)
    _require_trackable_graph(graph_path, manifest)
    source_file = _source_text(chapter_path)
    for entry in manifest["chapters"]:
        if _same_source(str(entry.get("source_file", "")), source_file):
            raise ValueError("This chapter is already tracked; use update-chapter instead")
        if entry.get("chapter_index") == chapter_index:
            raise ValueError(f"Chapter index {chapter_index} is already tracked")

    graph = load_graph(graph_path)
    add_chapter_fragment(
        graph,
        fragment,
        chapter_path=chapter_path,
        chapter_index=chapter_index,
        chapter_label=chapter_label,
    )

    relpath = _fragment_relpath(chapter_index, source_file)
    entry = {
        "source_file": source_file,
        "chapter_index": chapter_index,
        "chapter_label": chapter_label,
        "sha256": _chapter_hash(chapter_path),
        "fragment_file": relpath,
    }
    candidate = {"version": MANIFEST_VERSION, "chapters": _sorted_entries([*manifest["chapters"], entry])}

    _write_fragment(graph_path, relpath, fragment)
    save_graph(graph, graph_path)
    _save_manifest(graph_path, candidate)
    return graph


def update_chapter(
    *,
    graph_path: Path,
    chapter_path: Path,
    fragment: dict,
    chapter_index: int,
    chapter_label: str | None = None,
) -> nx.MultiDiGraph:
    """Replace one tracked chapter, replaying cached facts without rereading other prose."""
    manifest = load_manifest(graph_path)
    source_file = _source_text(chapter_path)
    matches = [
        entry
        for entry in manifest["chapters"]
        if _same_source(str(entry.get("source_file", "")), source_file)
        or entry.get("chapter_index") == chapter_index
    ]
    if len(matches) != 1:
        raise ValueError("update-chapter requires exactly one tracked chapter matching the source or index")
    old_entry = matches[0]

    new_entry = dict(old_entry)
    new_entry.update(
        {
            "source_file": source_file,
            "chapter_index": chapter_index,
            "chapter_label": chapter_label,
            "sha256": _chapter_hash(chapter_path),
        }
    )
    if not isinstance(new_entry.get("fragment_file"), str):
        new_entry["fragment_file"] = _fragment_relpath(chapter_index, source_file)

    entries = [new_entry if entry is old_entry else entry for entry in manifest["chapters"]]
    entries = _sorted_entries(entries)

    # Build a candidate graph entirely in memory. No output file is changed until
    # the replacement and every later cached fragment can be replayed successfully.
    candidate_graph = empty_graph()
    for entry in entries:
        if entry is new_entry:
            add_chapter_fragment(
                candidate_graph,
                fragment,
                chapter_path=chapter_path,
                chapter_index=chapter_index,
                chapter_label=chapter_label,
            )
        else:
            add_fragment(candidate_graph, _read_fragment(graph_path, entry))

    _write_fragment(graph_path, str(new_entry["fragment_file"]), fragment)
    save_graph(candidate_graph, graph_path)
    _save_manifest(graph_path, {"version": MANIFEST_VERSION, "chapters": entries})
    return candidate_graph


def tracked_chapters(graph_path: Path) -> list[dict]:
    return [dict(entry) for entry in _sorted_entries(load_manifest(graph_path)["chapters"])]
