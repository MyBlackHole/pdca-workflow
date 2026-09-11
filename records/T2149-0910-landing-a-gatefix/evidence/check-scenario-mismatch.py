#!/usr/bin/env python3
# 本体投射[T2153]：ontology:concept/pdca-task（双层闸之 CI 全库层）；本体是源、代码是投射。
"""CI 全库 parent/child scenario_type 一致性扫描（T2149）。

补齐 `ci-ontology-gate.py` 1b 节引用的缺失脚本。判定语义复用
`task_identity.py` 创建时跨层规则：父子 scenario 不一致时，
子标题含 `ontology:` 即视为显式跨层授权，否则 SCENARIO_MISMATCH。

无 parent、parent 缺失、任一方无 scenario_type、任一方非活跃（active 非 true）、
parent 已 archive 的任务跳过（历史包袱豁免：父归档后子 plan 僵尸票无执行意义）。
退出码 0 = 通过；非 0 = 阻断并输出 mismatch 清单（JSON）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def repo_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    return ROOT


def _load_tasks(root: Path) -> dict[str, dict]:
    tasks: dict[str, dict] = {}
    for path in sorted((root / "pdca" / "tasks").glob("**/task.json")):
        try:
            task = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        tid = task.get("id")
        if isinstance(tid, str):
            tasks[tid] = task
    return tasks


def find_mismatches(root: Path) -> list[dict]:
    """返回跨层无批注的 (child, parent) 清单。"""
    tasks = _load_tasks(root)
    mismatches: list[dict] = []
    for tid in sorted(tasks):
        task = tasks[tid]
        if (task.get("meta") or {}).get("active") is not True:
            continue
        parent = task.get("parent")
        if not parent or parent not in tasks:
            continue
        parent_task = tasks[parent]
        if (parent_task.get("meta") or {}).get("active") is not True:
            continue
        if (parent_task.get("meta") or {}).get("phase") == "archive":
            continue
        p_scen = (tasks[parent].get("meta") or {}).get("scenario_type")
        c_scen = (task.get("meta") or {}).get("scenario_type")
        if not p_scen or not c_scen or p_scen == c_scen:
            continue
        title = str(task.get("title") or "")
        conv = ((task.get("meta") or {}).get("convergence") or [])
        has_onto = "ontology:" in title.lower() or any(
            "ontology" in str(c).lower() for c in conv
        )
        if not has_onto:
            mismatches.append(
                {
                    "child": tid,
                    "child_scenario": c_scen,
                    "parent": parent,
                    "parent_scenario": p_scen,
                    "code": "SCENARIO_MISMATCH",
                }
            )
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description="全库 scenario 双层闸扫描")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = repo_root(args.root)
    mismatches = find_mismatches(root)
    if args.json or mismatches:
        print(json.dumps({"valid": not mismatches, "mismatches": mismatches}, ensure_ascii=False))
    else:
        print(json.dumps({"valid": True, "mismatches": []}, ensure_ascii=False))
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
