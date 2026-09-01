from __future__ import annotations

import html
import json
from pathlib import Path

import networkx as nx


def to_html(graph: nx.MultiDiGraph, path: Path) -> None:
    nodes = [
        {
            "id": node_id,
            "label": attrs.get("label", node_id),
            "type": attrs.get("type", "concept"),
        }
        for node_id, attrs in graph.nodes(data=True)
    ]
    edges = [
        {
            "from": source,
            "to": target,
            "label": attrs.get("relation", "related_to"),
            "title": " | ".join(
                str(x) for x in [attrs.get("chapter"), attrs.get("source_file"), attrs.get("confidence")] if x
            ),
        }
        for source, target, attrs in graph.edges(data=True)
    ]
    node_json = json.dumps(nodes, ensure_ascii=False)
    edge_json = json.dumps(edges, ensure_ascii=False)
    title = html.escape("StoryGraph - Novel Relationship Map")
    page = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8'>
<title>{title}</title>
<style>
html,body,#graph{{width:100%;height:100%;margin:0;font-family:system-ui,sans-serif}}
#toolbar{{position:fixed;z-index:2;top:12px;left:12px;background:white;padding:10px 12px;border-radius:10px;box-shadow:0 2px 12px #0002}}
#graph{{position:fixed;inset:0}}
</style>
<script src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>
</head>
<body>
<div id='toolbar'><b>StoryGraph</b>　节点 {len(nodes)}　关系 {len(edges)}</div>
<div id='graph'></div>
<script>
const nodes = new vis.DataSet({node_json});
const edges = new vis.DataSet({edge_json});
const network = new vis.Network(document.getElementById('graph'), {{nodes, edges}}, {{
  interaction: {{hover:true, navigationButtons:true}},
  physics: {{stabilization:true}},
  nodes: {{shape:'dot', size:18, font:{{size:16}}}},
  edges: {{arrows:'to', font:{{align:'middle'}}, smooth:true}}
}});
</script>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
