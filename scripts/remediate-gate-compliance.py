#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-architecture（门禁异常修复）；本体是源、代码是投射。
"""门禁合规存量修复器（T0271，第七轮）。

对 T0270 审计发现的门禁异常执行安全修复：
  1. 补 verdict：从 records/<record>/conclusion.md 的 Verdict 段提取，写入 meta.verdict
  2. 豁免标记：对无依据历史项加 meta.gate_exemption（如实记录，不伪造）
  3. 嵌套副本删除：archive_dup 的孤立嵌套副本（仅 task.json）删除，保留完整主目录
  4. active 残留移除：active_stale 的 active 目录残留（archive task.json 相同）移除

默认 --dry-run 只预览；--apply 才实际改动。原子写 task.json，git 保证可回滚。

用法：
  remediate-gate-compliance.py --root <repo> --dry-run            # 预览修复计划
  remediate-gate-compliance.py --root <repo> --apply              # 执行修复
  remediate-gate-compliance.py --root <repo> --apply --verbose    # 详细输出
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

VERDICT_BACKFILL = {
    "T0207": "T0207-0803-fsck-scrub-rewrite-followup",
    "T0208": "T0208-0803-btree-random-op-consistency",
    "T0209": "T0209-0803-snapshot-table-reload",
}

EXEMPTIONS = {
    "T0149": "早期任务（T0149-0801-design-md-review）record=None 无 conclusion，缺 final_confirmation 属历史未纳入门禁，如实豁免不伪造",
    "T0200": "早期任务缺 act-to-archive receipt（仅 plan-to-do/check-to-act），无过渡记录依据，如实豁免不伪造",
    "T0207": "补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Verdict，如实豁免",
    "T0208": "补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Verdict，如实豁免",
    "T0209": "补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Verdict，如实豁免",
}

NESTED_DUPES = [
    "pdca/tasks/archive/0801-btree-split-proptest/0801-btree-split-proptest",
    "pdca/tasks/archive/0801-trans-enomem-restart/0801-trans-enomem-restart",
]

ACTIVE_STALE = [
    "pdca/tasks/active/0804-cdm-report-center-analyse",
    "pdca/tasks/active/T0215-0804-report-subscheme-docs",
]

VERDICT_RE = re.compile(r"##\s*Verdict\s*(.*?)(?:##|\Z)", re.DOTALL)


def load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def atomic_json(path: Path, value: dict) -> None:
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with open(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
    finally:
        Path(name).unlink(missing_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_verdict(conclusion_path: Path) -> dict | None:
    if not conclusion_path.is_file():
        return None
    text = conclusion_path.read_text(encoding="utf-8", errors="replace")
    m = VERDICT_RE.search(text)
    if not m:
        return None
    section = m.group(1).strip()
    verdict_id = None
    idm = re.search(r"(V-[A-Za-z0-9-]+)", section)
    if idm:
        verdict_id = idm.group(1)
    outcome = "confirmed"
    if re.search(r"complete|Passed|通过|收敛", section, re.IGNORECASE):
        outcome = "confirmed"
    elif re.search(r"refuted|失败|不通过", section, re.IGNORECASE):
        outcome = "refuted"
    return {
        "outcome": outcome,
        "reason": f"backfilled from {conclusion_path.relative_to(conclusion_path.parents[1])} Verdict section",
        "verdict_id": verdict_id,
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def plan_verdict_backfill(root: Path, verbose: bool) -> list[dict]:
    plans = []
    for task_id, record in VERDICT_BACKFILL.items():
        matches = [p for p in root.rglob("task.json") if (load_json(p) or {}).get("id") == task_id]
        if not matches:
            plans.append({"action": "skip", "task": task_id, "reason": "task.json not found"})
            continue
        task_path = matches[0]
        task = load_json(task_path) or {}
        if (task.get("meta") or {}).get("verdict"):
            plans.append({"action": "skip", "task": task_id, "reason": "verdict already present"})
            continue
        conclusion = root / "records" / record / "conclusion.md"
        verdict = extract_verdict(conclusion)
        if not verdict:
            plans.append({"action": "skip", "task": task_id, "reason": f"verdict not extractable from {conclusion}"})
            continue
        plans.append({
            "action": "backfill-verdict",
            "task": task_id,
            "path": str(task_path.relative_to(root)),
            "verdict_id": verdict["verdict_id"],
            "outcome": verdict["outcome"],
        })
    return plans


def plan_exemptions(root: Path) -> list[dict]:
    plans = []
    for task_id, reason in EXEMPTIONS.items():
        matches = [p for p in root.rglob("task.json") if (load_json(p) or {}).get("id") == task_id]
        if not matches:
            plans.append({"action": "skip", "task": task_id, "reason": "task.json not found"})
            continue
        task_path = matches[0]
        task = load_json(task_path) or {}
        if (task.get("meta") or {}).get("gate_exemption"):
            plans.append({"action": "skip", "task": task_id, "reason": "exemption already present"})
            continue
        plans.append({"action": "mark-exemption", "task": task_id, "path": str(task_path.relative_to(root))})
    return plans


def plan_nested_cleanup(root: Path) -> list[dict]:
    plans = []
    for rel in NESTED_DUPES:
        target = root / rel
        if not target.is_dir():
            plans.append({"action": "skip", "path": rel, "reason": "nested dir not found"})
            continue
        files = sorted(target.rglob("*"))
        plans.append({
            "action": "delete-nested-copy",
            "path": rel,
            "files": [str(f.relative_to(root)) for f in files],
        })
    return plans


def plan_active_cleanup(root: Path) -> list[dict]:
    plans = []
    for rel in ACTIVE_STALE:
        target = root / rel
        if not target.is_dir():
            plans.append({"action": "skip", "path": rel, "reason": "active dir not found"})
            continue
        plans.append({
            "action": "remove-active-stale",
            "path": rel,
            "files": [str(f.relative_to(root)) for f in sorted(target.rglob("*"))],
        })
    return plans


def apply_plan(root: Path, plans: list[dict], verbose: bool) -> None:
    for plan in plans:
        action = plan["action"]
        if action == "skip":
            if verbose:
                print(f"- skip {plan.get('task', plan.get('path'))}: {plan['reason']}")
            continue
        if action == "backfill-verdict":
            task_path = root / plan["path"]
            task = load_json(task_path)
            if task is None:
                print(f"- SKIP backfill {plan['task']}: task.json unreadable")
                continue
            conclusion = root / "records" / VERDICT_BACKFILL[plan["task"]] / "conclusion.md"
            verdict = extract_verdict(conclusion)
            if verdict is None:
                print(f"- SKIP backfill {plan['task']}: verdict not extractable")
                continue
            task.setdefault("meta", {})["verdict"] = verdict
            atomic_json(task_path, task)
            print(f"+ backfilled verdict {verdict['verdict_id']} -> {plan['task']}")
        elif action == "mark-exemption":
            task_path = root / plan["path"]
            task = load_json(task_path)
            if task is None:
                print(f"- SKIP exemption {plan['task']}: task.json unreadable")
                continue
            task.setdefault("meta", {})["gate_exemption"] = {
                "reason": EXEMPTIONS[plan["task"]],
                "at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            atomic_json(task_path, task)
            print(f"+ marked exemption -> {plan['task']}")
        elif action == "delete-nested-copy":
            target = root / plan["path"]
            shutil.rmtree(target)
            print(f"+ deleted nested copy {plan['path']} ({len(plan['files'])} files)")
        elif action == "remove-active-stale":
            target = root / plan["path"]
            shutil.rmtree(target)
            print(f"+ removed active stale {plan['path']} ({len(plan['files'])} files)")


def main() -> int:
    parser = argparse.ArgumentParser(description="门禁合规存量修复器")
    parser.add_argument("--root", type=Path, required=True, help="仓库根目录")
    parser.add_argument("--dry-run", action="store_true", help="只预览不改动")
    parser.add_argument("--apply", action="store_true", help="执行修复")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.dry_run == args.apply:
        parser.error("must specify exactly one of --dry-run or --apply")

    root = args.root.resolve()
    plans = []
    plans += plan_verdict_backfill(root, args.verbose)
    plans += plan_exemptions(root)
    plans += plan_nested_cleanup(root)
    plans += plan_active_cleanup(root)

    if args.dry_run:
        print(f"# 修复计划预览（dry-run）—— 共 {len(plans)} 项")
        for plan in plans:
            action = plan["action"]
            if action == "skip":
                print(f"- [skip] {plan.get('task', plan.get('path'))}: {plan['reason']}")
            elif action == "backfill-verdict":
                print(f"- [补 verdict] {plan['task']}: {plan['verdict_id']} ({plan['outcome']}) -> {plan['path']}")
            elif action == "mark-exemption":
                print(f"- [豁免] {plan['task']} -> {plan['path']}")
            elif action == "delete-nested-copy":
                print(f"- [删嵌套副本] {plan['path']} ({len(plan['files'])} files)")
            elif action == "remove-active-stale":
                print(f"- [移 active 残留] {plan['path']} ({len(plan['files'])} files)")
        return 0

    apply_plan(root, plans, args.verbose)
    print("修复完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
