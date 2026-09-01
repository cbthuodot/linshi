from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

import networkx as nx

from .core import graph_to_data, save_graph
from .reasoning import consistency_issues, story_groups, unresolved_foreshadowing
from .workspace import tracked_chapters


def to_json(graph: nx.MultiDiGraph, path: Path) -> None:
    """Write the stable StoryGraph JSON interchange format."""
    save_graph(graph, path)


def to_html(graph: nx.MultiDiGraph, path: Path) -> None:
    """Write a self-contained clickable relationship map with no CDN dependency."""
    data = graph_to_data(graph)
    nodes = data["nodes"]
    edges = data["edges"]
    payload = json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape("StoryGraph 小说关系图")
    page = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{title}</title>
<style>
:root{{--bg:#f7f7f5;--panel:#fff;--line:#a7a7a7;--text:#202124;--muted:#6b7280;--accent:#2563eb;}}
*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text)}}
header{{height:58px;display:flex;align-items:center;gap:14px;padding:10px 16px;background:var(--panel);border-bottom:1px solid #ddd}}
header strong{{font-size:18px}}input{{min-width:220px;max-width:420px;width:34vw;padding:8px 10px;border:1px solid #ccc;border-radius:8px}}
#wrap{{display:grid;grid-template-columns:minmax(0,1fr) 310px;height:calc(100vh - 58px)}}
#canvas{{width:100%;height:100%;background:radial-gradient(circle at center,#fff 0,#f7f7f5 72%)}}
#panel{{padding:16px;background:var(--panel);border-left:1px solid #ddd;overflow:auto}}
#panel h2{{font-size:18px;margin:0 0 10px}}#panel p,#panel li{{font-size:13px;line-height:1.5}}.muted{{color:var(--muted)}}
.edge{{stroke:var(--line);stroke-width:1.4;opacity:.65}}.edge.active{{stroke:var(--accent);stroke-width:2.5;opacity:1}}
.node circle{{fill:#fff;stroke:#555;stroke-width:1.8}}.node text{{font-size:12px;pointer-events:none}}.node.active circle{{stroke:var(--accent);stroke-width:4}}.node.dim{{opacity:.16}}
.edge.dim{{opacity:.06}}.edge-label{{font-size:10px;fill:#555;pointer-events:none}}.edge-label.dim{{opacity:.06}}
@media(max-width:800px){{#wrap{{grid-template-columns:1fr}}#panel{{display:none}}}}
</style>
</head>
<body>
<header><strong>StoryGraph 小说关系图</strong><span class=\"muted\">节点 {len(nodes)} · 关系 {len(edges)}</span><input id=\"search\" placeholder=\"搜索人物、地点、秘密……\"></header>
<div id=\"wrap\"><svg id=\"canvas\" viewBox=\"0 0 1200 820\" aria-label=\"StoryGraph network\"></svg><aside id=\"panel\"><h2>点击一个节点</h2><p class=\"muted\">会显示它的类型、别名和直接关系。</p></aside></div>
<script id=\"storygraph-data\" type=\"application/json\">{payload}</script>
<script>
const data=JSON.parse(document.getElementById('storygraph-data').textContent);const svg=document.getElementById('canvas'),panel=document.getElementById('panel');
const NS='http://www.w3.org/2000/svg',W=1200,H=820,cx=W/2,cy=H/2;const nodes=data.nodes,edges=data.edges;const byId=new Map(nodes.map(n=>[n.id,n]));
const radius=Math.max(170,Math.min(340,130+nodes.length*7));const pos=new Map();nodes.forEach((n,i)=>{{const a=(Math.PI*2*i/Math.max(nodes.length,1))-Math.PI/2;const ring=radius+(i%3)*52;pos.set(n.id,[cx+Math.cos(a)*ring,cy+Math.sin(a)*ring]);}});
function el(name,attrs={{}}){{const x=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>x.setAttribute(k,v));return x;}}
const edgeEls=[],labelEls=[];edges.forEach((e,i)=>{{if(!pos.has(e.source)||!pos.has(e.target))return;const [x1,y1]=pos.get(e.source),[x2,y2]=pos.get(e.target);const line=el('line',{{x1,y1,x2,y2,class:'edge','data-i':i}});svg.appendChild(line);edgeEls.push([i,line]);const t=el('text',{{x:(x1+x2)/2,y:(y1+y2)/2,class:'edge-label','text-anchor':'middle'}});t.textContent=e.relation||'related_to';svg.appendChild(t);labelEls.push([i,t]);}});
const nodeEls=new Map();nodes.forEach(n=>{{const [x,y]=pos.get(n.id);const g=el('g',{{class:'node',transform:`translate(${{x}} ${{y}})`,tabindex:'0'}});const c=el('circle',{{r:18}}),t=el('text',{{y:34,'text-anchor':'middle'}});t.textContent=n.label||n.id;g.append(c,t);g.addEventListener('click',()=>select(n.id));g.addEventListener('keydown',ev=>{{if(ev.key==='Enter')select(n.id)}});svg.appendChild(g);nodeEls.set(n.id,g);}});
function relationText(e){{const a=byId.get(e.source)?.label||e.source,b=byId.get(e.target)?.label||e.target;return `${{a}} —${{e.relation||'related_to'}}→ ${{b}}${{e.chapter?' · '+e.chapter:''}}`;}}
function clearSelection(){{nodeEls.forEach(g=>g.classList.remove('active','dim'));edgeEls.forEach(([,x])=>x.classList.remove('active','dim'));labelEls.forEach(([,x])=>x.classList.remove('dim'));}}
function select(id){{clearSelection();const connected=new Set([id]),edgeIndexes=new Set();edges.forEach((e,i)=>{{if(e.source===id||e.target===id){{connected.add(e.source);connected.add(e.target);edgeIndexes.add(i);}}}});nodeEls.forEach((g,nid)=>{{if(nid===id)g.classList.add('active');else if(!connected.has(nid))g.classList.add('dim')}});edgeEls.forEach(([i,x])=>{{if(edgeIndexes.has(i))x.classList.add('active');else x.classList.add('dim')}});labelEls.forEach(([i,x])=>{{if(!edgeIndexes.has(i))x.classList.add('dim')}});const n=byId.get(id),rels=edges.filter(e=>e.source===id||e.target===id);panel.innerHTML=`<h2>${{escapeHtml(n.label||n.id)}}</h2><p><b>类型：</b>${{escapeHtml(n.type||'concept')}}</p>${{n.aliases?.length?`<p><b>别名：</b>${{n.aliases.map(escapeHtml).join('、')}}</p>`:''}}<p class=\"muted\">ID: ${{escapeHtml(n.id)}}</p><h3>直接关系</h3>${{rels.length?`<ul>${{rels.map(e=>`<li>${{escapeHtml(relationText(e))}}</li>`).join('')}}</ul>`:'<p class=\"muted\">没有直接关系</p>'}}`;}}
function escapeHtml(s){{return String(s??'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));}}
document.getElementById('search').addEventListener('input',ev=>{{const q=ev.target.value.trim().toLowerCase();clearSelection();if(!q)return;nodeEls.forEach((g,id)=>{{const n=byId.get(id),hay=[n.label,n.id,...(n.aliases||[])].join(' ').toLowerCase();if(!hay.includes(q))g.classList.add('dim')}});}});
svg.addEventListener('click',ev=>{{if(ev.target===svg){{clearSelection();panel.innerHTML='<h2>点击一个节点</h2><p class=\"muted\">会显示它的类型、别名和直接关系。</p>';}}}});
</script>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")


def to_report(graph: nx.MultiDiGraph, path: Path, *, graph_path: Path | None = None) -> None:
    """Write a deterministic human-readable story status report."""
    counts = Counter(str(attrs.get("type", "concept")) for _, attrs in graph.nodes(data=True))
    issues = consistency_issues(graph)
    unresolved = unresolved_foreshadowing(graph)
    groups = story_groups(graph)
    chapters: list[dict] = []
    if graph_path is not None:
        try:
            chapters = tracked_chapters(graph_path)
        except (ValueError, OSError, json.JSONDecodeError):
            chapters = []

    lines = [
        "# STORY REPORT",
        "",
        f"- 节点：{graph.number_of_nodes()}",
        f"- 关系：{graph.number_of_edges()}",
        f"- 已跟踪章节：{len(chapters)}",
        f"- 未回收线索/伏笔：{len(unresolved)}",
        f"- 强一致性警告：{len(issues)}",
        "",
        "## 内容类型",
        "",
    ]
    if counts:
        for kind, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {kind}: {count}")
    else:
        lines.append("- 暂无内容")

    lines.extend(["", "## 章节", ""])
    if chapters:
        for entry in chapters:
            label = entry.get("chapter_label") or f"第{entry.get('chapter_index', '?')}章"
            lines.append(f"- {label} — `{entry.get('source_file', '')}`")
    else:
        lines.append("- 没有可用的章节跟踪记录")

    lines.extend(["", "## 未回收线索与伏笔", ""])
    if unresolved:
        for item in unresolved:
            chapter = item.get("chapter_index")
            prefix = f"第{chapter}章" if isinstance(chapter, int) else "未知章节"
            lines.append(f"- {prefix}：{item.get('label')} ({item.get('type')})")
    else:
        lines.append("- 当前没有未回收项")

    lines.extend(["", "## 一致性检查", ""])
    if issues:
        for issue in issues:
            chapter = issue.get("chapter_index")
            prefix = f"第{chapter}章" if isinstance(chapter, int) else "未知章节"
            lines.append(f"- [{issue.get('kind')}] {prefix}：{issue.get('message')}")
    else:
        lines.append("- 没有发现强一致性问题")

    lines.extend(["", "## 故事关系组", ""])
    if groups:
        for index, group in enumerate(groups, start=1):
            members = "、".join(str(value) for value in group.get("members", []))
            lines.append(f"- 组 {index}（{group.get('size')} 个节点，中心：{group.get('central')}）：{members}")
    else:
        lines.append("- 暂无关系组")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_all(graph: nx.MultiDiGraph, graph_path: Path, html_path: Path, report_path: Path) -> None:
    to_json(graph, graph_path)
    to_html(graph, html_path)
    to_report(graph, report_path, graph_path=graph_path)
