#!/usr/bin/env python3
"""知识类本体质量度量：统计知识类本体的保真度指标。

- 每个knowledge_type的节点数、有/无适用场景、有/无案例的比例
- verification_method分布
- reviewer覆盖率
- 空洞节点比例（无适用场景+无案例+无reviewer）

用法：
  python3 scripts/ontology-knowledge-quality.py --ontology-dir ontology
  python3 scripts/ontology-knowledge-quality.py --ontology-dir ontology --output quality-report.md
"""
from __future__ import annotations
import argparse, json, sys, yaml
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_TYPES = {"pattern", "principle", "pitfall", "fact", "decision"}


def analyze_knowledge_quality(ont_dir: Path) -> dict:
    """分析知识类本体的质量指标。"""
    stats = {kt: {"total": 0, "has_applicability": 0, "has_case": 0, "has_reviewer": 0, "has_testable_signal": 0} for kt in KNOWLEDGE_TYPES}
    hollow_nodes = []

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

        ftype = fm.get("type", "")
        if ftype not in KNOWLEDGE_TYPES:
            continue

        stats[ftype]["total"] += 1
        oid = fm.get("id", str(md))

        attrs = fm.get("attributes", []) or []
        attr_names = " ".join(a.get("name", "").lower() for a in attrs)
        full_text = text.lower()

        has_applicability = any(kw in attr_names or kw in full_text for kw in ["applicability", "适用", "boundary", "不适用"])
        has_case = any(kw in attr_names or kw in full_text for kw in ["case_study", "case-study", "case study", "counterexample", "source_record"])
        has_reviewer = bool(fm.get("reviewer", ""))
        has_signal = any(a.get("testable_signal", "").strip() for a in attrs)

        if has_applicability:
            stats[ftype]["has_applicability"] += 1
        if has_case:
            stats[ftype]["has_case"] += 1
        if has_reviewer:
            stats[ftype]["has_reviewer"] += 1
        if has_signal:
            stats[ftype]["has_testable_signal"] += 1

        # 空洞节点：无适用场景+无案例+无reviewer
        if not has_applicability and not has_case and not has_reviewer:
            hollow_nodes.append({"id": oid, "type": ftype, "file": str(md)})

    # 计算比率
    result = {"types": {}, "hollow_nodes": hollow_nodes}
    for kt, data in stats.items():
        if data["total"] > 0:
            result["types"][kt] = {
                "total": data["total"],
                "applicability_rate": round(data["has_applicability"] / data["total"] * 100, 1),
                "case_rate": round(data["has_case"] / data["total"] * 100, 1),
                "reviewer_rate": round(data["has_reviewer"] / data["total"] * 100, 1),
                "signal_rate": round(data["has_testable_signal"] / data["total"] * 100, 1),
            }

    result["hollow_count"] = len(hollow_nodes)
    result["overall_quality"] = "PASS" if len(hollow_nodes) == 0 else "NEEDS_ATTENTION"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="知识类本体质量度量")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    quality = analyze_knowledge_quality(args.ontology_dir)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# 知识类本体质量报告", ""]
        for kt, data in quality.get("types", {}).items():
            lines.append(f"## {kt}")
            lines.append(f"- 总数: {data['total']}")
            lines.append(f"- 适用场景覆盖率: {data['applicability_rate']}%")
            lines.append(f"- 案例覆盖率: {data['case_rate']}%")
            lines.append(f"- 专家确认率: {data['reviewer_rate']}%")
            lines.append(f"- 信号覆盖率: {data['signal_rate']}%")
            lines.append("")
        lines.append(f"## 空洞节点: {quality['hollow_count']}")
        lines.append(f"整体质量: {quality['overall_quality']}")
        args.output.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(quality, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
