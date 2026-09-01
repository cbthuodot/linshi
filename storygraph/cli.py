from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import add_fragment, empty_graph, load_graph, neighbors, save_graph, shortest_path, story_history
from .export import export_all, to_report
from .extraction import chapter_extraction_errors
from .paths import DEFAULT_GRAPH
from .reasoning import (
    active_relationships,
    consistency_issues,
    knowledge_state,
    story_groups,
    unresolved_foreshadowing,
)
from .workspace import ingest_chapter, update_chapter


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
    fragment = _read_fragment(args.fragment)
    ingest_chapter(
        graph_path=path,
        chapter_path=Path(args.chapter),
        fragment=fragment,
        chapter_index=args.index,
        chapter_label=args.label,
    )
    print(f"Added tracked chapter {args.index}: {len(fragment['edges'])} relations")
    return 0


def cmd_update_chapter(args: argparse.Namespace) -> int:
    path = _graph_path(args.graph)
    fragment = _read_fragment(args.fragment)
    update_chapter(
        graph_path=path,
        chapter_path=Path(args.chapter),
        fragment=fragment,
        chapter_index=args.index,
        chapter_label=args.label,
    )
    print(f"Updated tracked chapter {args.index}: {len(fragment['edges'])} relations")
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


def cmd_timeline(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    rows = story_history(graph, args.text)
    if not rows:
        print("No timeline entries found.")
        return 0
    for row in rows:
        chapter = row.get("chapter") or f"第{row.get('chapter_index', '?')}章"
        print(f"{chapter}: {row['from']} --{row['relation']}--> {row['to']}")
    return 0


def cmd_knowledge(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    state = knowledge_state(graph, args.character, args.secret, args.at)
    print(f"第{args.at}章：{args.character} 对『{args.secret}』的状态 = {state['state']}")
    for item in state["evidence"]:
        evidence = f" — {item['evidence']}" if item.get("evidence") else ""
        print(f"  第{item['chapter_index']}章 {item['relation']}{evidence}")
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    rows = active_relationships(graph, args.text, args.at)
    if not rows:
        print("No active relationships found.")
        return 0
    for row in rows:
        print(f"{row['from']} --{row['relation']}--> {row['to']}")
    return 0


def cmd_unresolved(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    rows = unresolved_foreshadowing(graph, args.at)
    if not rows:
        print("No unresolved clues or foreshadowing found.")
        return 0
    for row in rows:
        chapter = f"第{row['chapter_index']}章" if isinstance(row.get("chapter_index"), int) else "未知章节"
        print(f"{chapter}: {row['label']} ({row['type']})")
    return 0


def cmd_groups(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    groups = story_groups(graph)
    if not groups:
        print("No story groups found.")
        return 0
    for index, group in enumerate(groups, start=1):
        members = "、".join(str(item) for item in group["members"])
        print(f"Group {index} ({group['size']}): {members} | central={group['central']}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    graph = load_graph(_graph_path(args.graph))
    issues = consistency_issues(graph)
    if not issues:
        print("No strong consistency issues found.")
        return 0
    for issue in issues:
        chapter = f"第{issue['chapter_index']}章" if isinstance(issue.get("chapter_index"), int) else "未知章节"
        print(f"- [{issue['kind']}] {chapter}: {issue['message']}")
    return 1


def cmd_report(args: argparse.Namespace) -> int:
    graph_path = _graph_path(args.graph)
    report_path = Path(args.output) if args.output else graph_path.parent / "STORY_REPORT.md"
    to_report(load_graph(graph_path), report_path, graph_path=graph_path)
    print(f"Story report written: {report_path}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    graph_path = _graph_path(args.graph)
    html_path = Path(args.html) if args.html else graph_path.parent / "graph.html"
    report_path = Path(args.report) if args.report else graph_path.parent / "STORY_REPORT.md"
    graph = load_graph(graph_path)
    export_all(graph, graph_path, html_path, report_path)
    print(f"Exported: {graph_path}, {html_path}, {report_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="storygraph")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create an empty graph")
    init.add_argument("--graph")
    init.set_defaults(func=cmd_init)

    add = sub.add_parser("add", help="validate and add an untracked graph fragment")
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
        "add-chapter", help="validate, add, and track a chapter for safe future updates"
    )
    add_chapter.add_argument("chapter")
    add_chapter.add_argument("fragment")
    add_chapter.add_argument("--index", type=int, required=True)
    add_chapter.add_argument("--label")
    add_chapter.add_argument("--graph")
    add_chapter.set_defaults(func=cmd_add_chapter)

    update = sub.add_parser(
        "update-chapter", help="replace one tracked chapter without rereading unchanged chapters"
    )
    update.add_argument("chapter")
    update.add_argument("fragment")
    update.add_argument("--index", type=int, required=True)
    update.add_argument("--label")
    update.add_argument("--graph")
    update.set_defaults(func=cmd_update_chapter)

    query = sub.add_parser("query", help="show relationships around an entity")
    query.add_argument("text")
    query.add_argument("--graph")
    query.set_defaults(func=cmd_query)

    path = sub.add_parser("path", help="find how two entities are connected")
    path.add_argument("a")
    path.add_argument("b")
    path.add_argument("--graph")
    path.set_defaults(func=cmd_path)

    timeline = sub.add_parser("timeline", help="show an entity's relationship history in chapter order")
    timeline.add_argument("text")
    timeline.add_argument("--graph")
    timeline.set_defaults(func=cmd_timeline)

    knowledge = sub.add_parser("knowledge", help="ask whether a character knows a secret at a chapter")
    knowledge.add_argument("character")
    knowledge.add_argument("secret")
    knowledge.add_argument("--at", type=int, required=True)
    knowledge.add_argument("--graph")
    knowledge.set_defaults(func=cmd_knowledge)

    state = sub.add_parser("state", help="show effective relationships for an entity at a chapter")
    state.add_argument("text")
    state.add_argument("--at", type=int, required=True)
    state.add_argument("--graph")
    state.set_defaults(func=cmd_state)

    unresolved = sub.add_parser("unresolved", help="show clues/foreshadowing without a payoff")
    unresolved.add_argument("--at", type=int)
    unresolved.add_argument("--graph")
    unresolved.set_defaults(func=cmd_unresolved)

    groups = sub.add_parser("groups", help="show connected story groups")
    groups.add_argument("--graph")
    groups.set_defaults(func=cmd_groups)

    check = sub.add_parser("check", help="detect strong continuity and knowledge conflicts")
    check.add_argument("--graph")
    check.set_defaults(func=cmd_check)

    report = sub.add_parser("report", help="write STORY_REPORT.md")
    report.add_argument("--output")
    report.add_argument("--graph")
    report.set_defaults(func=cmd_report)

    export = sub.add_parser("export", help="write graph.json, clickable graph.html, and STORY_REPORT.md")
    export.add_argument("--html")
    export.add_argument("--report")
    export.add_argument("--graph")
    export.set_defaults(func=cmd_export)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
