#!/usr/bin/env python3
# 本体投射[T2053]：ontology:domain/skill-verify-convergence（收敛支撑链校验）；本体是源、代码是投射。
"""Validate a task's deterministic convergence-to-evidence support chain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdca_core import convergence_issues, evidence_issues, load_json, repo_root, task_issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-dir", required=True, type=Path)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    root = repo_root(args.root)
    task_dir = args.task_dir.resolve()
    issues = task_issues(root, task_dir, include_phase_requirements=False)
    if not issues:
        task = load_json(task_dir / "task.json")
        issues.extend(evidence_issues(root, task))
        issues.extend(convergence_issues(root, task_dir))
    payload = {
        "schema": "pdca.convergence-validation/v1",
        "task_dir": str(task_dir),
        "valid": not issues,
        "issues": [issue.as_dict() for issue in issues],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
