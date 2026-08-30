"""ontology-tree-split: 依据本体 specializes/composed_of 关系树 + PRD 拆分映射，生成 WBS 子任务候选（顾问式，不落盘）。

输入 PRD 的 `## 拆分映射` 小节（机器可读：` - <章节> -> ontology:<node-id>`），结合
`meta.ontology_fragment` 指向的本体目录中的 `composed_of`/`specializes` 关系树，自底向上
生成候选子任务：被映射节点若有 `composed_of` 子实体，则每个子实体成为子任务候选，
映射节点自身成为集成任务（依赖所有子）；无子实体时映射节点自身成为子任务候选。
每个候选自动携带 `ontology_node_type`（由本体节点 type 推导）与依赖边。
"""
import argparse
import json
import re
import sys
from pathlib import Path

from ontology_reason import load_ontology

SPLIT_MAP_RE = re.compile(r"^-\s*(.+?)\s*->\s*ontology:(.+?)\s*$", re.MULTILINE)


def parse_split_map(prd_text: str) -> list[tuple[str, str]]:
    in_section = False
    rows: list[tuple[str, str]] = []
    for line in prd_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped == "## 拆分映射"
            continue
        if in_section:
            m = SPLIT_MAP_RE.match(line)
            if m:
                rows.append((m.group(1).strip(), "ontology:" + m.group(2).strip()))
    return rows


def _relation_adj(nodes: dict, rel_key: str) -> dict:
    return {oid: (fm.get("relations", {}).get(rel_key) or []) for oid, fm in nodes.items()}


def detect_cycle(adj: dict) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in adj}

    def dfs(u: str) -> bool:
        color[u] = GRAY
        for v in adj.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for n in list(adj):
        if color[n] == WHITE and dfs(n):
            return True
    return False


def make_candidate(node_id: str, nodes: dict, deps=None, chapter=None) -> dict:
    fm = nodes[node_id]
    slug_base = node_id.split("/")[-1]
    return {
        "slug_base": slug_base,
        "title": fm.get("summary", slug_base),
        "ontology_node_type": fm.get("type"),
        "ontology_node_id": node_id,
        "dependencies": deps or [],
        "source_chapter": chapter,
    }


def generate(prd_path: Path, ont_dir: Path) -> dict:
    nodes = load_ontology(ont_dir)
    prd_text = Path(prd_path).read_text(encoding="utf-8")
    mapping = parse_split_map(prd_text)
    if not mapping:
        raise ValueError("PRD 未含 '## 拆分映射' 小节或解析为空")
    for _, nid in mapping:
        if nid not in nodes:
            raise ValueError(f"拆分映射节点不存在: {nid}")
    if detect_cycle(_relation_adj(nodes, "composed_of")) or detect_cycle(
        _relation_adj(nodes, "specializes")
    ):
        raise ValueError("本体关系图存在环（composed_of/specializes），拒绝生成")
    candidates: list[dict] = []
    seen: set[str] = set()
    for chapter, nid in mapping:
        fm = nodes[nid]
        children = fm.get("relations", {}).get("composed_of") or []
        valid_children = [c for c in children if c in nodes]
        missing = set(children) - set(valid_children)
        if missing:
            raise ValueError(f"节点 {nid} 的 composed_of 含不存在节点: {sorted(missing)}")
        if valid_children:
            child_slugs = []
            for c in valid_children:
                if c not in seen:
                    candidates.append(make_candidate(c, nodes, deps=[], chapter=chapter))
                    seen.add(c)
                child_slugs.append(c.split("/")[-1])
            candidates.append(make_candidate(nid, nodes, deps=child_slugs, chapter=chapter))
        else:
            if nid in seen:
                continue
            candidates.append(make_candidate(nid, nodes, deps=[], chapter=chapter))
            seen.add(nid)
    return {"schema": "pdca.tree-split/v1", "candidates": candidates}


def main() -> int:
    ap = argparse.ArgumentParser(description="本体关系树驱动 WBS 候选生成")
    ap.add_argument("--ontology-dir", required=True)
    ap.add_argument("--prd", required=True)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()
    try:
        result = generate(Path(args.prd), Path(args.ontology_dir))
    except ValueError as e:
        print(f"[ontology-tree-split] ERROR: {e}", file=sys.stderr)
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out == "-":
        print(text)
    else:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
