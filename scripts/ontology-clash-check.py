#!/usr/bin/env python3
"""在任务拆分前检测候选 slug/标题是否与既有 ontology 节点重名。

PDCA 工作流的 `to-tickets` 技能在把 PRD 拆为子任务前调用本脚本：
若候选子任务 slug/标题与已存在的 ontology 节点（concept/entity/...）
名称冲突，提示「已有本体节点 X，建议复用而非新建任务」，
避免任务与本体分类法不对齐。

仅作提示，不改变拆解产出；退出码恒为 0（告警式，不阻断 CI）。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ONTOLOGY_DIR = "ontology"

# 本体节点类型词表（与 ontology-validate.TYP_VOCAB 对齐）。
NODE_TYPES = {
    "domain", "entity", "concept", "process", "role",
    "pattern", "principle", "pitfall", "fact", "decision",
}

# 去掉任务 slug 常见的 MMDD- 日期前缀，便于与本体 slug 比较。
_DATE_PREFIX = re.compile(r"^[0-9]{4}-")


def _node_ids(root: Path) -> list[str]:
    """收集 ontology 下全部节点 id（frontmatter `id:` 或推导 id）。"""
    ids: list[str] = []
    ont_root = root / ONTOLOGY_DIR
    if not ont_root.exists():
        return ids
    for path in sorted(ont_root.rglob("*.md")):
        rel = path.relative_to(ont_root)
        parts = rel.with_suffix("").parts
        if len(parts) != 2:
            continue
        ntype, slug = parts
        if ntype not in NODE_TYPES:
            continue
        derived = f"ontology:{ntype}/{slug}"
        ids.append(derived)
        # 也读取 frontmatter 的 id 作为别名（去重，避免与推导 id 重复）
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        m = re.search(r"^id:\s*(.+)$", text, re.MULTILINE)
        if m:
            alias = m.group(1).strip()
            if alias not in ids:
                ids.append(alias)
    return ids


def _normalize(token: str) -> str:
    return token.strip().lower()


def _slug_tokens(slug: str) -> set[str]:
    base = _DATE_PREFIX.sub("", slug)
    return {_normalize(t) for t in re.split(r"[-_\s]+", base) if len(t) >= 3}


def _match_one(candidate: str, node_ids: list[str]) -> list[str]:
    """返回与候选冲突的本体节点 id 列表。"""
    cand = candidate.strip()
    cand_lower = _normalize(cand)
    cand_tokens = _slug_tokens(cand)
    clashes: list[str] = []
    for nid in node_ids:
        if ":" not in nid:
            continue
        slug = nid.split("/", 1)[-1]
        nid_lower = _normalize(nid)
        if _normalize(slug) == cand_lower:
            clashes.append(nid)
            continue
        if _normalize(slug) in cand_lower or cand_lower in _normalize(slug):
            clashes.append(nid)
            continue
        node_tokens = _slug_tokens(slug)
        if cand_tokens and node_tokens and (cand_tokens & node_tokens):
            clashes.append(nid)
            continue
    return clashes


def find_clashes(root: Path, candidates: list[str]) -> dict[str, list[str]]:
    """给定候选列表，返回 {candidate: [冲突节点 id, ...]}。"""
    node_ids = _node_ids(root)
    return {c: _match_one(c, node_ids) for c in candidates}


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    candidates: list[str] = []
    if len(argv) > 2 and argv[2] == "--candidates":
        candidates = [c for c in argv[3].split(",") if c.strip()]
    report = find_clashes(root, candidates)
    total = sum(1 for v in report.values() if v)
    if total:
        print(f"[ontology-clash] 检测到 {total} 个候选与既有本体节点重名，建议复用而非新建：")
        for cand, clashes in report.items():
            if clashes:
                print(f"  - 候选 {cand!r} 命中: {', '.join(clashes)}")
    else:
        print("[ontology-clash] 未发现与既有本体节点重名。")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
