#!/usr/bin/env python3
"""知识类本体适用场景检查：验证每个知识类本体有applicability和boundary。

用法：
  python3 scripts/ontology-knowledge-applicability.py --ontology-dir ontology
  python3 scripts/ontology-knowledge-applicability.py --ontology-dir ontology --knowledge-type pattern
"""
from __future__ import annotations
import argparse, json, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_TYPES = {"pattern", "principle", "pitfall", "fact", "decision"}


def check_knowledge_applicability(ont_dir: Path, knowledge_type: str | None = None) -> list[dict]:
    """检查知识类本体的适用场景和边界定义。"""
    issues = []
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
        if knowledge_type and ftype != knowledge_type:
            continue

        oid = fm.get("id", str(md))
        attrs = fm.get("attributes", []) or []

        # 检查是否有 applicability 和 boundary 属性
        attr_names = [a.get("name", "") for a in attrs]
        has_applicability = any("applicability" in n.lower() or "适用" in n.lower() for n in attr_names)
        has_boundary = any("boundary" in n.lower() or "不适用" in n.lower() or "边界" in n.lower() for n in attr_names)

        # 也检查正文中是否有 ## 适用 / ## 约束 章节
        has_applicability_section = "## 适用" in text or "## 约束" in text or "适用场景" in text
        has_boundary_section = "## 不适用" in text or "边界" in text or "不适用场景" in text

        if not (has_applicability or has_applicability_section):
            issues.append({
                "ontology_id": oid,
                "file": str(md),
                "type": ftype,
                "issue": "MISSING_APPLICABILITY",
                "message": f"知识类本体缺少适用场景定义（applicability属性或## 适用章节）"
            })

        if not (has_boundary or has_boundary_section):
            issues.append({
                "ontology_id": oid,
                "file": str(md),
                "type": ftype,
                "issue": "MISSING_BOUNDARY",
                "message": f"知识类本体缺少不适用边界定义（boundary属性或## 不适用章节）"
            })

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="知识类本体适用场景检查")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--knowledge-type", choices=list(KNOWLEDGE_TYPES), default=None)
    ap.add_argument("--strict", action="store_true", help="严格模式：有问题的节点非0退出")
    args = ap.parse_args()

    issues = check_knowledge_applicability(args.ontology_dir, args.knowledge_type)

    report = {
        "checked": True,
        "knowledge_type": args.knowledge_type or "all",
        "issues": issues,
        "valid": len(issues) == 0
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n检查结果: {len(issues)} 个问题", file=sys.stderr)

    if args.strict and issues:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
