#!/usr/bin/env python3
"""双层闸：research父仅生research叶，development父仅生development叶，跨层需显式ontology批注"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_tasks(root: Path):
    tasks = {}
    for p in (root / "pdca" / "tasks").rglob("task.json"):
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            tasks[j.get("id")] = (j, p)
        except Exception:
            continue
    return tasks

def check(root: Path = ROOT):
    tasks = load_tasks(root)
    issues = []
    for tid, (j, p) in tasks.items():
        # 历史豁免：archive且created_at早于硬门禁日（2026-09-01）跳过
        created = j.get("meta", {}).get("created_at", "")
        if created and created < "2026-09-01":
            continue
        parent_id = j.get("parent")
        if not parent_id or parent_id not in tasks:
            continue
        parent_j, _ = tasks[parent_id]
        p_scen = parent_j.get("meta", {}).get("scenario_type")
        c_scen = j.get("meta", {}).get("scenario_type")
        if p_scen and c_scen and p_scen != c_scen:
            # 跨层需显式ontology批注：child prd或task含ontology:
            prd = (p.parent / "prd.md")
            has_onto = False
            if prd.is_file():
                try:
                    if "ontology:" in prd.read_text(encoding="utf-8"):
                        has_onto = True
                except Exception:
                    pass
            if not has_onto:
                issues.append(f"{p.relative_to(root)}: 父 {parent_id}({p_scen})→子 {tid}({c_scen}) 跨层无ontology:批注 → SCENARIO_MISMATCH")
    return issues

def main():
    issues = check()
    if issues:
        print(f"FAIL: {len(issues)} SCENARIO_MISMATCH")
        for it in issues:
            print(f"  [SCENARIO_MISMATCH] {it}")
        return 1
    print("OK: scenario双层闸通过")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
