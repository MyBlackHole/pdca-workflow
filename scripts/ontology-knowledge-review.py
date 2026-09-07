#!/usr/bin/env python3
"""知识类本体领域专家确认：检查知识类本体frontmatter中的reviewer字段。

未经确认的节点标注status: pending-review。

用法：
  python3 scripts/ontology-knowledge-review.py --ontology-dir ontology
  python3 scripts/ontology-knowledge-review.py --ontology-dir ontology --check-pending
"""
from __future__ import annotations
import argparse, json, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_TYPES = {"pattern", "principle", "pitfall", "fact", "decision"}


def check_knowledge_review(ont_dir: Path, check_pending: bool = False) -> list[dict]:
    """检查知识类本体的领域专家确认。"""
    results = []
    pending = []
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

        oid = fm.get("id", str(md))
        reviewer = fm.get("reviewer", "")
        status = fm.get("status", "active")

        entry = {
            "ontology_id": oid,
            "type": ftype,
            "file": str(md),
            "reviewer": reviewer,
            "status": status,
            "has_reviewer": bool(reviewer)
        }
        results.append(entry)

        if check_pending and not reviewer and status == "active":
            pending.append(entry)
            # 标注为 pending-review（不修改文件，仅报告）
            entry["recommendation"] = "pending-review"

    return results, pending


def main() -> int:
    ap = argparse.ArgumentParser(description="知识类本体领域专家确认检查")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--check-pending", action="store_true", help="检查未确认的节点")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    results, pending = check_knowledge_review(args.ontology_dir, args.check_pending)

    report = {
        "checked": True,
        "total": len(results),
        "reviewed": sum(1 for r in results if r["has_reviewer"]),
        "unreviewed": len(pending),
        "pending_nodes": pending if args.check_pending else [],
        "valid": len(pending) == 0 or not args.check_pending
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.check_pending and pending:
        print(f"\n{len(pending)} 个知识类本体未确认，标注为pending-review", file=sys.stderr)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
