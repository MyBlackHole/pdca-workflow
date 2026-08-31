#!/usr/bin/env python3
"""Check research tasks' ontology settlement decision in Act.

For scenario_type == research and phase in (act, archive):
- conclusion.md must contain '## 本体沉淀' section
- that section must explicitly mention 'ontology:' or 'records-only'
- task.json meta.disposition.reason must contain 'ontology' or 'records-only'
- if decision is 'ontology', at least one ontology/<type>/*.md must reference the record or task

Exit 0 when not applicable (non-research or not in act/archive) or when all checks pass.
Exit 1 with RESEARCH_SETTLEMENT_* issues otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True, type=Path, help="pdca/tasks/<slug> or pdca/tasks/archive/.../<slug>")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()

    task_dir: Path = args.task_dir
    if not task_dir.is_dir():
        print(f"TASK_DIR_NOT_FOUND: {task_dir}", file=sys.stderr)
        return 1

    task_path = task_dir / "task.json"
    if not task_path.is_file():
        print(f"TASK_JSON_MISSING: {task_path}", file=sys.stderr)
        return 1

    task = load_json(task_path)
    scenario = task.get("meta", {}).get("scenario_type")
    phase = task.get("meta", {}).get("phase")
    record = task.get("meta", {}).get("record")

    # Only check research tasks in act/archive
    if scenario != "research":
        print(f"SKIP: scenario_type={scenario} not research")
        return 0
    if phase not in ("act", "archive"):
        print(f"SKIP: phase={phase} not in (act, archive)")
        return 0

    issues = []

    # Resolve record dir: prefer records/<record>
    record_dir = None
    if record:
        cand = args.root / "records" / record
        if cand.is_dir():
            record_dir = cand

    conclusion = None
    if record_dir:
        cand = record_dir / "conclusion.md"
        if cand.is_file():
            conclusion = cand.read_text(encoding="utf-8")
        else:
            issues.append(f"RESEARCH_SETTLEMENT_MISSING: conclusion.md not found at {cand}")
    else:
        # Fallback: try to find conclusion under task_dir? (should not happen in act)
        issues.append(f"RESEARCH_SETTLEMENT_MISSING: record dir not found for record={record}")

    # Check conclusion has ## 本体沉淀 with explicit decision
    if conclusion is not None:
        if "## 本体沉淀" not in conclusion:
            issues.append("RESEARCH_SETTLEMENT_MISSING: conclusion.md missing '## 本体沉淀' section")
        else:
            # Extract section
            section = conclusion.split("## 本体沉淀", 1)[1].split("\n## ", 1)[0]
            has_ontology = "ontology:" in section or "ontology/" in section
            has_records_only = "records-only" in section
            if not (has_ontology or has_records_only):
                issues.append("RESEARCH_SETTLEMENT_MISSING: '## 本体沉淀' must explicitly contain 'ontology:' or 'records-only'")

    # Check disposition
    disposition = task.get("meta", {}).get("disposition")
    if not disposition:
        issues.append("RESEARCH_SETTLEMENT_MISSING: task.json meta.disposition missing (act must set disposition with ontology/records-only)")
    else:
        reason = disposition.get("reason", "")
        has_ontology = "ontology" in reason.lower()
        has_records_only = "records-only" in reason.lower()
        if not (has_ontology or has_records_only):
            issues.append("RESEARCH_SETTLEMENT_MISSING: meta.disposition.reason must contain 'ontology' or 'records-only'")

    # If decision is ontology, verify at least one ontology node references the record/task
    if conclusion and "ontology:" in conclusion:
        # Look for ontology references
        found = False
        ont_root = args.root / "ontology"
        if ont_root.is_dir():
            for md in ont_root.rglob("*.md"):
                try:
                    text = md.read_text(encoding="utf-8")
                except Exception:
                    continue
                if record and record in text:
                    found = True
                    break
                if task.get("id") and task["id"] in text:
                    found = True
                    break
        if not found:
            issues.append(f"RESEARCH_SETTLEMENT_MISSING: decision is ontology but no ontology/*.md references record={record} or task={task.get('id')}")

    if issues:
        for iss in issues:
            print(iss, file=sys.stderr)
        return 1

    print(f"OK: research settlement decision present for {task.get('id')} (record={record}, phase={phase})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
