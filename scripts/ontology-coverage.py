#!/usr/bin/env python3
"""本体覆盖率度量：统计代码到本体的覆盖比率。

用法：
  python3 scripts/ontology-coverage.py --ontology-dir ontology --source src/
  python3 scripts/ontology-coverage.py --ontology-dir ontology --source src/ --output coverage-report.md
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def count_code_entities(source_dir: Path) -> dict:
    """统计源代码中的实体数量。"""
    counts = {"classes": 0, "functions": 0, "files": 0}
    if not source_dir.is_dir():
        return counts
    for py_file in source_dir.rglob("*.py"):
        counts["files"] += 1
        text = py_file.read_text(encoding="utf-8")
        counts["classes"] += len(re.findall(r'\bclass\s+\w+', text))
        counts["functions"] += len(re.findall(r'\bdef\s+\w+', text))
    return counts


def count_ontology_nodes(ont_dir: Path) -> dict:
    """统计本体中的节点数量和属性。"""
    counts = {"nodes": 0, "attributes": 0, "testable_signals": 0, "types": {}}
    for md in sorted(ont_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        fm = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                except Exception:
                    pass
        counts["nodes"] += 1
        counts["types"][fm.get("type", "unknown")] = counts["types"].get(fm.get("type", "unknown"), 0) + 1
        attrs = fm.get("attributes", []) or []
        counts["attributes"] += len(attrs)
        for attr in attrs:
            if attr.get("testable_signal", "").strip():
                counts["testable_signals"] += 1
    return counts


def compute_coverage(code_counts: dict, ont_counts: dict) -> dict:
    """计算覆盖率。"""
    # 简化计算：本体节点数 / 代码类数
    code_classes = code_counts.get("classes", 1) or 1
    ont_nodes = ont_counts.get("nodes", 0)
    coverage = (ont_nodes / code_classes * 100) if code_classes > 0 else 0

    # 识别未覆盖的代码区域
    uncovered = max(0, code_classes - ont_nodes)

    return {
        "code_classes": code_classes,
        "code_functions": code_counts.get("functions", 0),
        "code_files": code_counts.get("files", 0),
        "ontology_nodes": ont_nodes,
        "ontology_attributes": ont_counts.get("attributes", 0),
        "ontology_testable_signals": ont_counts.get("testable_signals", 0),
        "coverage_percentage": round(coverage, 1),
        "uncovered_classes": uncovered,
        "ontology_types": ont_counts.get("types", {})
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="本体覆盖率度量")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--source", type=Path, default=ROOT / "src")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    code_counts = count_code_entities(args.source)
    ont_counts = count_ontology_nodes(args.ontology_dir)
    coverage = compute_coverage(code_counts, ont_counts)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        report_md = f"""# 本体覆盖率报告

## 覆盖率

- 代码类: {coverage['code_classes']}
- 代码函数: {coverage['code_functions']}
- 代码文件: {coverage['code_files']}
- 本体节点: {coverage['ontology_nodes']}
- 本体属性: {coverage['ontology_attributes']}
- 可测试信号: {coverage['ontology_testable_signals']}
- **覆盖率: {coverage['coverage_percentage']}%**
- 未覆盖类: {coverage['uncovered_classes']}

## 本体类型分布

{json.dumps(coverage['ontology_types'], ensure_ascii=False, indent=2)}
"""
        args.output.write_text(report_md, encoding="utf-8")

    print(json.dumps(coverage, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
