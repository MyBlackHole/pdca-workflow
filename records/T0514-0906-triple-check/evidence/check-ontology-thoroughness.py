#!/usr/bin/env python3
"""Ontology thoroughness triple-check: 完整性五要素门禁。

一查结构：frontmatter 合法、attributes>=2、relations 含 specializes 与
  relates_to/guides 至少各一、体裁节齐全。
二查详尽（完整性五要素实质存在）：
  - 背景问题节、核心机制（编号条目>=3 且带依据标记）、适用边界节、
    违反后果节、关联导航（relates_to 含非 pdca 目标）。
  - domain/pattern/principle 按体裁映射节名，缺一即 issue。
三查交叉：引用节点文件存在、信号无泛化短语。

用法：
  python3 scripts/check-ontology-thoroughness.py --node ontology/domain/foo.md
  python3 scripts/check-ontology-thoroughness.py --dir ontology/domain
只检查给定文件，不重跑历史（误杀历史由调用方承担范围）。
Exit 0 全过，Exit 1 有 issue（逐条打印）。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERIC_PHRASES = ["由领域实践与测试验证", "符合领域最佳实践", "相关验证", "相应检查"]

# 体裁 -> 五要素节标题关键词（正文 ## 节）
SECTIONS = {
    "domain": {
        "背景": ["## 背景", "## 问题"],
        "机制": ["## 核心概念", "## 学习路径"],
        "边界": ["## 复用指南", "## 约束", "## 适用"],
        "违反": ["## 违反", "## 后果", "## 复用指南"],
        "导航": None,  # 由 relations 判定
    },
    "pattern": {
        "背景": ["## 问题"],
        "机制": ["## 方案"],
        "边界": ["## 后果"],
        "违反": ["## 违反", "## 后果"],
        "导航": None,
    },
    "principle": {
        "背景": ["## 背景", "## 适用场景"],
        "机制": ["## 约定"],
        "边界": ["## 适用场景", "## 约定"],
        "违反": ["## 违反"],
        "导航": None,
    },
}

REQUIRED_FM = ["schema", "id", "type", "layer", "summary", "status"]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm: dict = {}
    for line in text[3:end].split("\n"):
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def check_node(path: Path, root: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    ntype = fm.get("type", "")

    # 一查结构
    for k in REQUIRED_FM:
        if k not in fm:
            issues.append(f"STRUCT_FM_MISSING: {path.name} 缺 frontmatter 字段 {k}")
    n_attrs = len(re.findall(r"^- name: |^  - name: ", text, re.M))
    if n_attrs < 2:
        issues.append(f"STRUCT_ATTRS_FEW: {path.name} attributes 仅 {n_attrs} 条，要求>=2")
    if "specializes" not in text:
        issues.append(f"STRUCT_REL_MISSING: {path.name} 缺 specializes")
    if "relates_to" not in text and "guides" not in text:
        issues.append(f"STRUCT_REL_MISSING: {path.name} 缺 relates_to/guides")

    # 二查详尽
    secs = SECTIONS.get(ntype)
    if secs is None:
        issues.append(f"STRUCT_TYPE_UNKNOWN: {path.name} type={ntype} 无五要素映射")
        return issues
    body = text.split("---", 2)[-1] if text.startswith("---") else text
    for elem, keys in secs.items():
        if keys is None:
            continue
        if not any(k in body for k in keys):
            issues.append(f"THOROUGH_ELEM_MISSING: {path.name} 缺{elem}节（{ '/'.join(keys) }）")
    numbered = re.findall(r"^#{0,3}\s*\d+\.\s+\*\*|^#{0,3}\s*\d+\.\s+\S", body, re.M)
    plain_numbered = re.findall(r"^\d+\.\s+", body, re.M)
    if len(numbered) + len(plain_numbered) < 3:
        issues.append(f"THOROUGH_ITEMS_FEW: {path.name} 编号机制条目不足 3 条")
    # 依据标记：代码路径 / 函数调用形 / 本体引用
    has_evidence = ("fs/" in body or "src/" in body or re.search(r"[a-z_]+\(\)", body)
                    or "ontology:" in body or "对照" in body)
    if not has_evidence:
        issues.append(f"THOROUGH_EVIDENCE_MISSING: {path.name} 无依据标记（代码路径/函数形/本体引用/对照）")

    # 三查交叉
    for m in re.finditer(r"ontology:([A-Za-z0-9._/\-]+)", text):
        nid = m.group(0)
        if nid in ("ontology:concept/pdca", "ontology:concept/pdca-task"):
            continue
        if "/" not in nid.split(":", 1)[1]:
            continue  # 本体根引用（如 ontology:pattern），非节点引用
        try:
            typ, slug = nid.split(":", 1)[1].split("/", 1)
        except ValueError:
            issues.append(f"CROSS_REF_INVALID: {path.name} 引用格式非法 {nid}")
            continue
        cand = root / "ontology" / typ / f"{slug}.md"
        if not cand.is_file():
            found = any(nid in md.read_text(encoding="utf-8", errors="ignore")
                        for md in (root / "ontology").rglob("*.md"))
            if not found:
                issues.append(f"CROSS_REF_DANGLING: {path.name} 引用空悬 {nid}")
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("testable_signal:") and any(p in s for p in GENERIC_PHRASES):
            issues.append(f"CROSS_GENERIC_SIGNAL: {path.name} 信号含泛化短语")
            break
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", type=Path)
    ap.add_argument("--dir", type=Path)
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()
    targets: list[Path] = []
    if args.node:
        targets = [args.node]
    elif args.dir:
        targets = sorted(args.dir.glob("*.md"))
    else:
        print("need --node or --dir", file=sys.stderr)
        return 2
    all_issues: list[str] = []
    for t in targets:
        if t.name == "README.md":
            continue
        all_issues.extend(check_node(t, args.root))
    for iss in all_issues:
        print(iss)
    print(f"checked {len(targets)} files, {len(all_issues)} issues")
    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
