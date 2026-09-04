#!/usr/bin/env python3
# 本体投射[T2053]：ontology:process/flow-plan（阶段原子推进与语义门禁）；本体是源、代码是投射。
"""Atomically transition one strict PDCA task after semantic gate validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from pdca_core import PHASES, Issue, acceptance_criteria, gate_issues, load_json, load_jsonl, repo_root, schema_issues
from flow_audit import audit_transition
import ontology_reason
import ontology_gate


def backfill_plan_timestamp(task_dir: Path, task: dict, task_path: Path) -> str | None:
    """若 states.plan 缺失，用 final_confirmation.at（Plan 真实完成时刻）补写；
    无 confirmation 记录时兜底用当前时刻。补写后原子落盘。
    返回补写值（未补写则返回 None）。"""
    if task.get("states", {}).get("plan") is not None:
        return None
    path = task_dir / "clarifications.jsonl"
    confirmed_at = None
    if path.is_file():
        try:
            for entry in load_jsonl(path):
                if entry.get("source") == "final_confirmation":
                    confirmed_at = entry.get("at")
                    if confirmed_at is not None:
                        break
        except ValueError:
            pass
    if confirmed_at is None:
        confirmed_at = datetime.now().astimezone().isoformat(timespec="seconds")
    task.setdefault("states", {})["plan"] = confirmed_at
    atomic_json(task_path, task)
    return confirmed_at


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_rejected_receipt(task_dir: Path, task_id: str, current: str, to: str, payload: dict) -> None:
    """过渡被拒时写拒绝留痕 receipt（schema pdca.gate-rejection/v1）。

    纳秒时间戳保证文件名唯一（多次拒绝不覆盖）；不影响成功路径。
    """
    receipt_dir = task_dir / "transition-receipts"
    receipt_dir.mkdir(exist_ok=True)
    receipt = {
        "schema": "pdca.gate-rejection/v1",
        "task_id": task_id,
        "from": current,
        "to": to,
        **payload,
        "at": datetime.now().astimezone().isoformat(timespec="microseconds"),
    }
    atomic_json(receipt_dir / f"rejected-{time.time_ns()}-{to}.json", receipt)


def atomic_json(path: Path, value: dict) -> None:
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--to", required=True, choices=PHASES)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    root = repo_root(args.root)
    task_dir = args.task_dir.resolve()
    task_path = task_dir / "task.json"
    task = load_json(task_path)
    current = task["meta"]["phase"]
    if current == args.to:
        print(json.dumps({"status": "unchanged", "phase": current}))
        return 0
    if not ontology_reason.legal_transition(current, args.to, ont_dir=root / "ontology"):
        write_rejected_receipt(task_dir, task["id"], current, args.to,
                               {"error": "ILLEGAL_TRANSITION", "from": current, "to": args.to})
        print(json.dumps({"status": "rejected", "error": "ILLEGAL_TRANSITION", "from": current, "to": args.to}))
        return 1
    ready_issues = ontology_gate.ontology_ready_issues(task, root)
    if ready_issues:
        write_rejected_receipt(task_dir, task["id"], current, args.to,
                               {"issues": [i.as_dict() for i in ready_issues]})
        print(json.dumps({"status": "rejected", "issues": [i.as_dict() for i in ready_issues]}, ensure_ascii=False, indent=2))
        return 1
    if args.to in ("act", "archive"):
        va_issues = ontology_gate.verdict_anchor_issues(task, root)
        if va_issues:
            write_rejected_receipt(task_dir, task["id"], current, args.to,
                                   {"issues": [i.as_dict() for i in va_issues]})
            print(json.dumps({"status": "rejected", "issues": [i.as_dict() for i in va_issues]}, ensure_ascii=False, indent=2))
            return 1
    if args.to == "archive":
        arch_issues = ontology_gate.archive_ontology_ready_issues(root)
        if arch_issues:
            write_rejected_receipt(task_dir, task["id"], current, args.to,
                                   {"issues": [i.as_dict() for i in arch_issues]})
            print(json.dumps({"status": "rejected", "issues": [i.as_dict() for i in arch_issues]}, ensure_ascii=False, indent=2))
            return 1
    if args.to == "do":
        backfill_plan_timestamp(task_dir, task, task_path)
    try:
        audit_transition(root, task_dir, args.to)
    except Exception as exc:  # Audit findings are non-blocking; the transition gate remains authoritative.
        print(f"flow audit could not be recorded: {exc}", file=sys.stderr)
    if args.to == "do":
        criteria, prd_issues = acceptance_criteria(task_dir)
        if prd_issues:
            prd_issues = [
                Issue("PRD_ACCEPTANCE_FORMAT_INVALID", issue.path, issue.message, issue.guidance)
                if issue.code == "ACCEPTANCE_CRITERIA_MISSING"
                else issue
                for issue in prd_issues
            ]
            write_rejected_receipt(task_dir, task["id"], current, args.to,
                                   {"issues": [issue.as_dict() for issue in prd_issues]})
            print(json.dumps({"status": "rejected", "issues": [issue.as_dict() for issue in prd_issues]}, ensure_ascii=False, indent=2))
            return 1
    _, issues = gate_issues(root, task_dir)
    if issues:
        write_rejected_receipt(task_dir, task["id"], current, args.to,
                               {"issues": [issue.as_dict() for issue in issues]})
        print(json.dumps({"status": "rejected", "issues": [issue.as_dict() for issue in issues]}, ensure_ascii=False, indent=2))
        return 1

    before_digest = digest(task_path)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    task["meta"]["phase"] = args.to
    task["states"][args.to] = now
    if args.to == "do":
        task["status"] = "InProgress"
    elif args.to in {"check", "act"}:
        task["status"] = "Completed"
        task["meta"]["active"] = True
        if args.to == "check":
            task["meta"]["completed_at"] = now
    elif args.to == "archive":
        task["status"] = "Completed"
        task["meta"]["active"] = False

    validation = schema_issues(root, task, "task.schema.json")
    if validation:
        write_rejected_receipt(task_dir, task["id"], current, args.to,
                               {"issues": [issue.as_dict() for issue in validation]})
        print(json.dumps({"status": "rejected", "issues": [issue.as_dict() for issue in validation]}, ensure_ascii=False, indent=2))
        return 1

    backup = task_dir / "task.json.bak"
    shutil.copy2(task_path, backup)
    atomic_json(task_path, task)
    receipt_dir = task_dir / "transition-receipts"
    receipt_dir.mkdir(exist_ok=True)
    receipt = {
        "schema": "pdca.transition/v1",
        "task_id": task["id"],
        "from": current,
        "to": args.to,
        "before_digest": f"sha256:{before_digest}",
        "after_digest": f"sha256:{digest(task_path)}",
        "at": now,
    }
    atomic_json(receipt_dir / f"{current}-to-{args.to}.json", receipt)
    print(json.dumps({"status": "transitioned", **receipt}, ensure_ascii=False, indent=2))
    # T0409：转换成功后打印 PDCA 元本体给出的目标阶段实时指引（仅输出，不改门禁语义；走 stderr 以免污染 stdout JSON）
    try:
        import pdca_context
        print(pdca_context.render(args.to, root / "ontology"), file=sys.stderr)
    except Exception:
        pass
    # T0456：Act 阶段 evidence→ontology 自动反哺顾问式提示（不阻断，仅指引）
    if args.to in ("act", "archive"):
        try:
            for iss in ontology_gate.auto_induce_evidence(task, root):
                print(f"[auto-induce] {iss.code}: {iss.message}", file=sys.stderr)
                if iss.guidance:
                    print(f"  guidance: {iss.guidance}", file=sys.stderr)
            for iss in ontology_gate.auto_induce_flow_issues(root, threshold=3):
                print(f"[auto-induce] {iss.code}: {iss.message}", file=sys.stderr)
                if iss.guidance:
                    print(f"  guidance: {iss.guidance}", file=sys.stderr)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
