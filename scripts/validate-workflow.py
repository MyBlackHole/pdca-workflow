#!/usr/bin/env python3
# 本体投射[T2053]：ontology:process/flow-plan（任务全量校验）；本体是源、代码是投射。
"""Validate a strict PDCA task or every active/archived task."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdca_core import gate_issues, identity_diagnostics, repo_root, task_issues


def result(task_dir: Path, issues: list) -> dict:
    return {
        "task_dir": str(task_dir),
        "valid": not issues,
        "issues": [issue.as_dict() for issue in issues],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-dir", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--gate", action="store_true", help="validate readiness for the next phase")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if bool(args.task_dir) == bool(args.all):
        parser.error("choose exactly one of --task-dir or --all")

    root = repo_root(args.root)
    if args.task_dir:
        task_dir = args.task_dir.resolve()
        if args.gate:
            phase, issues = gate_issues(root, task_dir)
            payload = result(task_dir, issues)
            payload["phase"] = phase
        else:
            payload = result(task_dir, task_issues(root, task_dir))
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["valid"] else 1

    payloads = []
    for task_path in sorted((root / "pdca/tasks").glob("**/task.json")):
        task_dir = task_path.parent
        payloads.append(result(task_dir.relative_to(root), task_issues(root, task_dir)))
    identity = identity_diagnostics(root)
    summary = {
        "valid": all(item["valid"] for item in payloads) and identity["valid"],
        "task_count": len(payloads),
        "invalid_count": sum(not item["valid"] for item in payloads),
        "identity": identity,
        "tasks": payloads,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
