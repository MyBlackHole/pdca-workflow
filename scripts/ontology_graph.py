#!/usr/bin/env python3
"""scripts/ontology_graph.py

读取 ontology/**.md 的 pdca.asset/v1 frontmatter + relations，导出：
- Obsidian 兼容图谱（每个节点列出其 relations 作为 [[wikilink]]）
- 孤岛节点清单（无 relations 连线的节点）

仅用于可视化自检，不修改任何文件。由 T0407 落地（采纳 ONTOLOGY_GUIDE）。

用法：
  python3 scripts/ontology_graph.py [--root ontology] [--format summary|obsidian|dot] [--out FILE]
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import yaml


def extract_frontmatter(text: str) -> dict:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            data = yaml.safe_load(parts[1])
            return data if isinstance(data, dict) else {}
    return {}


def normalize(ref) -> str:
    s = ref.strip().strip("[]")
    if s.startswith("ontology:"):
        return s
    return "ontology:" + s


def load_graph(root: Path):
    nodes: dict[str, dict] = {}
    edges: list[tuple[str, str, str]] = []
    for md in sorted(root.rglob("*.md")):
        if md.name == "README.md":
            continue
        fm = extract_frontmatter(md.read_text(encoding="utf-8"))
        oid = fm.get("id")
        if not oid:
            continue
        nodes[oid] = {"type": fm.get("type"), "path": md, "fm": fm}
        for pred, vals in (fm.get("relations") or {}).items():
            for v in (vals if isinstance(vals, list) else [vals]):
                edges.append((oid, pred, normalize(v)))
    return nodes, edges


def islands(nodes: dict, edges: list) -> list[str]:
    connected: set[str] = set()
    for s, _, d in edges:
        connected.add(s)
        connected.add(d)
    return [nid for nid in nodes if nid not in connected]


def render_summary(nodes: dict, edges: list, iso: list) -> None:
    print("# Ontology graph summary")
    print(f"nodes: {len(nodes)}")
    print(f"edges: {len(edges)}")
    print(f"islands: {len(iso)}")
    for nid in iso:
        print(f"  - {nid}")


def render_obsidian(nodes: dict, edges: list) -> None:
    by_src: dict[str, list] = {}
    for s, p, d in edges:
        by_src.setdefault(s, []).append((p, d))
    for nid in sorted(nodes):
        print(f"# {nid}")
        for p, d in sorted(by_src.get(nid, [])):
            print(f"- **{p}**: [[{d}]]")
        print()


def render_dot(nodes: dict, edges: list) -> None:
    print("digraph ontology {")
    for nid in sorted(nodes):
        print(f'  "{nid}";')
    for s, p, d in edges:
        print(f'  "{s}" -> "{d}" [label="{p}"];')
    print("}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("ontology"))
    ap.add_argument("--format", choices=["summary", "obsidian", "dot"], default="summary")
    ap.add_argument("--out")
    args = ap.parse_args()
    nodes, edges = load_graph(args.root)
    iso = islands(nodes, edges)
    buf = io.StringIO()
    old = sys.stdout
    if args.out:
        sys.stdout = buf
    if args.format == "summary":
        render_summary(nodes, edges, iso)
    elif args.format == "obsidian":
        render_obsidian(nodes, edges)
    else:
        render_dot(nodes, edges)
    if args.out:
        sys.stdout = old
        Path(args.out).write_text(buf.getvalue(), encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
