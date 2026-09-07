#!/usr/bin/env python3
"""知识类本体案例/正反例检查：验证知识类本体有案例支撑。

- pattern/principle: 必须有case_study
- pitfall: 必须有counterexample
- fact: 必须有source_record

用法：
  python3 scripts/ontology-knowledge-examples.py --ontology-dir ontology
  python3 scripts/ontology-knowledge-examples.py --ontology-dir ontology --knowledge-type pitfall
"""
from __future__ import annotations
import argparse, json, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_TYPES = {"pattern", "principle", "pitfall", "fact", "decision"}
REQUIREMENTS = {
    "pattern": ("case_study", "MISSING_CASE_STUDY"),
    "principle": ("case_study", "MISSING_CASE_STUDY"),
    "pitfall": ("counterexample", "MISSING_COUNTEREXAMPLE"),
    "fact": ("source_record", "MISSING_SOURCE_RECORD"),
    "decision": ("evidence_ids", "MISSING_EVIDENCE_IDS"),
}


def check_knowledge_examples(ont_dir: Path, knowledge_type: str | None = None) -> list[dict]:
    """检查知识类本体的案例/正反例完备性。"""
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

        # 检查属性中的案例字段
        attrs = fm.get("attributes", []) or []
        attr_names = " ".join(a.get("name", "").lower() for a in attrs)
        # 也检查正文
        full_text = text.lower()

        if ftype in REQUIREMENTS:
            required_field, issue_code = REQUIREMENTS[ftype]
            has_field = (required_field in attr_names or
                        required_field in full_text or
                        f"## {required_field.replace('_', ' ')}" in text)
            if not has_field:
                issues.append({
                    "ontology_id": oid,
                    "file": str(md),
                    "type": ftype,
                    "issue": issue_code,
                    "message": f"{ftype} 缺少{REQUIREMENTS[ftype][0]}（{required_field}）"
                })

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="知识类本体案例/正反例检查")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--knowledge-type", choices=list(KNOWLEDGE_TYPES), default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    issues = check_knowledge_examples(args.ontology_dir, args.knowledge_type)

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
