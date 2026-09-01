from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import add_fragment, basic_conflicts, load_graph, neighbors, save_graph, shortest_path

DEFAULT_GRAPH = Path("storygraph-out/graph.json")


def _graph_path(value: str | None) -> Path:
    return Path(value) if value else DEFAULT_GRAPH


def cmd_init(args: argparse.Namespace) -> int:
    path = _graph_path(args.graph)
    graph = load_graph(path)
    save_graph(graph, path)
    print(f"StoryGraph ready: {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    path = _graph_path(args.graph)
    fragment = json.loads(Path(args.fragment).read_text(encoding="utf-8"))
    graph = load_graph(path)
    add_fragment(graph, fragment)
    save_graph(graph, path)
    print(f"Added {len(fragment.get('nodes', []))} nodes and {len(fragment.get('edges', []))} relations")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    rows = neighbors(graph, args.text)
    if not rows:
        print("No matching relationships found.")
        return 0
    for row in rows:
        suffix = ""
        if row.get("chapter"):
            suffix += f" [{row['chapter']}]"
        if row.get("source"):
            suffix += f" ({row['source']})"
        print(f"{row['from']} --{row['relation']}--> {row['to']}{suffix}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    path = shortest_path(graph, args.a, args.b)
    print(" -> ".join(path) if path else "No path found.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    conflicts = basic_conflicts(graph)
    if not conflicts:
        print("No basic conflicts found.")
        return 0
    for item in conflicts:
        print(f"- {item}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="storygraph")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create an empty story graph")
    p.add_argument("--graph")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add", help="add an extracted story fragment JSON")
    p.add_argument("fragment")
    p.add_argument("--graph")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("query", help="show relationships around a character or concept")
    p.add_argument("text")
    p.add_argument("--graph")
    p.set_defaults(func=cmd_query)

    p = sub.add_parser("path", help="find how two story entities are connected")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--graph")
    p.set_defaults(func=cmd_path)

    p = sub.add_parser("check", help="run simple consistency checks")
    p.add_argument("--graph")
    p.set_defaults(func=cmd_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
