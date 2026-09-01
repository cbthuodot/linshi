from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import add_fragment, empty_graph, load_graph, neighbors, save_graph, shortest_path
from .extraction import add_chapter_fragment, chapter_extraction_errors
from .paths import DEFAULT_GRAPH


def _graph_path(value: str | None) -> Path:
    return Path(value) if value else DEFAULT_GRAPH


def _read_fragment(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Fragment JSON must contain an object")
    return data


def cmd_init(args: argparse.Namespace) -> int:
    path = _graph_path(args.graph)
    save_graph(empty_graph(), path)
    print(f"StoryGraph ready: {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    path = _graph_path(args.graph)
    fragment = _read_fragment(args.fragment)
    graph = load_graph(path)
    add_fragment(graph, fragment)
    save_graph(graph, path)
    print(f"Added {len(fragment['nodes'])} nodes and {len(fragment['edges'])} relations")
    return 0


def cmd_validate_chapter(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    fragment = _read_fragment(args.fragment)
    errors = chapter_extraction_errors(
        graph,
        fragment,
        chapter_path=Path(args.chapter),
        chapter_index=args.index,
        chapter_label=args.label,
    )
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print("Chapter extraction is grounded and valid.")
    return 0


def cmd_add_chapter(args: argparse.Namespace) -> int:
    path = _graph_path(args.graph)
    graph = load_graph(path)
    fragment = _read_fragment(args.fragment)
    add_chapter_fragment(
        graph,
        fragment,
        chapter_path=Path(args.chapter),
        chapter_index=args.index,
        chapter_label=args.label,
    )
    save_graph(graph, path)
    print(f"Added grounded chapter {args.index}: {len(fragment['edges'])} relations")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    rows = neighbors(graph, args.text)
    if not rows:
        print("No matching relationships found.")
        return 0
    for row in rows:
        confidence = f" [{row['confidence']}]" if row.get("confidence") else ""
        chapter = f" [{row['chapter']}]" if row.get("chapter") else ""
        print(f"{row['from']} --{row['relation']}--> {row['to']}{chapter}{confidence}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    result = shortest_path(graph, args.a, args.b)
    print(" -> ".join(result) if result else "No path found.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="storygraph")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create an empty graph")
    init.add_argument("--graph")
    init.set_defaults(func=cmd_init)

    add = sub.add_parser("add", help="validate and add a graph fragment")
    add.add_argument("fragment")
    add.add_argument("--graph")
    add.set_defaults(func=cmd_add)

    validate_chapter = sub.add_parser(
        "validate-chapter", help="check that extracted relations are grounded in a chapter"
    )
    validate_chapter.add_argument("chapter")
    validate_chapter.add_argument("fragment")
    validate_chapter.add_argument("--index", type=int, required=True)
    validate_chapter.add_argument("--label")
    validate_chapter.add_argument("--graph")
    validate_chapter.set_defaults(func=cmd_validate_chapter)

    add_chapter = sub.add_parser(
        "add-chapter", help="validate a chapter extraction against its text, then add it"
    )
    add_chapter.add_argument("chapter")
    add_chapter.add_argument("fragment")
    add_chapter.add_argument("--index", type=int, required=True)
    add_chapter.add_argument("--label")
    add_chapter.add_argument("--graph")
    add_chapter.set_defaults(func=cmd_add_chapter)

    query = sub.add_parser("query", help="show relationships around an entity")
    query.add_argument("text")
    query.add_argument("--graph")
    query.set_defaults(func=cmd_query)

    path = sub.add_parser("path", help="find how two entities are connected")
    path.add_argument("a")
    path.add_argument("b")
    path.add_argument("--graph")
    path.set_defaults(func=cmd_path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
