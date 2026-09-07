#!/usr/bin/env python3
"""知识类本体证据支撑：验证知识类本体有evidence_source或等效验证。

知识类本体的testable_signal允许使用非代码验证方式：
  - expert-review: 领域专家确认
  - experiment: 实验验证
  - case-study: 案例研究
  - code-grep: 代码搜索（与domain/entity相同）

用法：
  python3 scripts/ontology-knowledge-evidence.py --ontology-dir ontology
  python3 scripts/ontology-knowledge-evidence.py --ontology-dir ontology --knowledge-type principle
"""
from __future__ import annotations
import argparse, json, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_TYPES = {"pattern", "principle", "pitfall", "fact", "decision"}
VALID_VERIFICATION_METHODS = {"code-grep", "expert-review", "experiment", "case-study"}


def check_knowledge_evidence(ont_dir: Path, knowledge_type: str | None = None) -> list[dict]:
    """检查知识类本体的证据支撑。"""
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

        # 检查 testable_signal 是否存在
        has_testable_signal = any(a.get("testable_signal", "").strip() for a in attrs)
        if not has_testable_signal:
            issues.append({
                "ontology_id": oid,
                "file": str(md),
                "type": ftype,
                "issue": "MISSING_TESTABLE_SIGNAL",
                "message": f"知识类本体缺少testable_signal"
            })
            continue

        # 检查 verification_method 是否存在
        has_verification = any("verification_method" in a.get("name", "").lower() for a in attrs)
        # 也检查正文中的 verification_method 或 evidence_source
        has_evidence_source = "evidence_source" in text or "verification_method" in text or "evidence" in text.lower()

        if not (has_verification or has_evidence_source):
            # 检查testable_signal中是否包含已知的验证方式
            all_signals = " ".join(a.get("testable_signal", "") for a in attrs)
            has_known_method = any(m in all_signals for m in VALID_VERIFICATION_METHODS)
            if not has_known_method:
                issues.append({
                    "ontology_id": oid,
                    "file": str(md),
                    "type": ftype,
                    "issue": "MISSING_VERIFICATION_METHOD",
                    "message": f"知识类本体的testable_signal未声明验证方式（code-grep/expert-review/experiment/case-study）"
                })

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="知识类本体证据支撑检查")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--knowledge-type", choices=list(KNOWLEDGE_TYPES), default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    issues = check_knowledge_evidence(args.ontology_dir, args.knowledge_type)

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
