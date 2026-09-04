#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/triage（brief 字段契约与采用率）；本体是源、代码是投射。
"""triager-brief 采用度检查器（T0268）。

解析 `triager-brief.md`（AGENT-BRIEF 产出），断言核心字段契约，并对历史
全量 brief 回溯统计采用率基线。

核心字段（宽松匹配，兼容早期非统一格式）：
  - category：`## 分类` / `category` / `类型`
  - evidence：`## 事实核验` / `## 已验证问题` / `fact` / `核验` / `验证`
  - dedup：`## 查重` / `查重` / `dedup`
  - scenario：`scenario_type` / `场景`
  - priority：`priority` / `优先级` / `P0` / `P1` / `P2`
  - actionable：`风险` / `信息缺口` / `推荐方向` / `下一步`

用法：
  check-triage-brief.py --file <triager-brief.md>   # 单文件契约检查
  check-triage-brief.py --scan <tasks-root>         # 全量回溯统计采用率
  check-triage-brief.py --scan <tasks-root> --json  # JSON 输出
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FIELDS = {
    "category": [r"##\s*分类", r"category", r"类型"],
    "evidence": [r"##\s*事实核验", r"##\s*已验证问题", r"fact", r"核验", r"验证"],
    "dedup": [r"##\s*查重", r"查重", r"dedup"],
    "scenario": [r"scenario_type", r"场景"],
    "priority": [r"priority", r"优先级", r"\bP0\b", r"\bP1\b", r"\bP2\b"],
    "actionable": [r"风险", r"信息缺口", r"推荐方向", r"下一步", r"信息缺口"],
}

CORE_FIELDS = ("category", "evidence", "dedup")


def extract_brief_paths(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*/triager-brief.md") if p.is_file() and "drafts" not in p.parts
    )


def check_brief(text: str) -> dict[str, bool]:
    found: dict[str, bool] = {}
    for name, patterns in FIELDS.items():
        found[name] = any(re.search(p, text, re.IGNORECASE) for p in patterns)
    return found


def report_brief(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    found = check_brief(text)
    return {
        "task": path.parent.name,
        "path": str(path),
        "fields": found,
        "core_fields": sum(1 for f in CORE_FIELDS if found[f]),
        "all_core": all(found[f] for f in CORE_FIELDS),
    }


def scan_baseline(root: Path) -> dict:
    paths = extract_brief_paths(root)
    items = [report_brief(p) for p in paths]
    total = len(items)
    counts = {f: sum(1 for i in items if i["fields"][f]) for f in FIELDS}
    coverage = {f: round(counts[f] / total * 100, 1) if total else 0 for f in FIELDS}
    core_full = sum(1 for i in items if i["all_core"])
    return {
        "total": total,
        "field_counts": counts,
        "field_coverage": coverage,
        "core_fields_full": core_full,
        "core_coverage": round(core_full / total * 100, 1) if total else 0,
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="triager-brief 采用度检查器")
    parser.add_argument("--file", help="单个 triager-brief.md 检查")
    parser.add_argument("--scan", help="扫描根目录全量回溯")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--exit-code", action="store_true",
                        help="核心字段缺失时返回非 0")
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"文件不存在: {path}", file=sys.stderr)
            return 1
        item = report_brief(path)
        if args.json:
            print(json.dumps(item, ensure_ascii=False, indent=2))
        else:
            print(f"# {item['task']}")
            for f, ok in item["fields"].items():
                print(f"- {f}: {'OK' if ok else 'MISSING'}")
            print(f"核心字段: {item['core_fields']}/{len(CORE_FIELDS)}")
        if args.exit_code and not item["all_core"]:
            return 1
        return 0

    if args.scan:
        baseline = scan_baseline(Path(args.scan))
        if args.json:
            print(json.dumps(baseline, ensure_ascii=False, indent=2))
        else:
            print(f"# triager-brief 采用度基线")
            print(f"总 brief 数: {baseline['total']}")
            for f in FIELDS:
                print(f"- {f}: {baseline['field_counts'][f]} ({baseline['field_coverage'][f]}%)")
            print(f"核心三字段全含: {baseline['core_fields_full']} ({baseline['core_coverage']}%)")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
