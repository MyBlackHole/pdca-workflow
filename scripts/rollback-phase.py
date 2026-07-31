#!/usr/bin/env python3
"""Restore the adjacent strict phase from the transition backup."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from pdca_core import PHASES, load_json, repo_root, schema_issues


def atomic_copy(source: Path, destination: Path) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=destination.name + ".", dir=destination.parent)
    os.close(descriptor)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    root = repo_root(args.root)
    task_dir = args.task_dir.resolve()
    current_path = task_dir / "task.json"
    backup_path = task_dir / "task.json.bak"
    if not backup_path.is_file():
        raise RuntimeError("task.json.bak is missing")
    current = load_json(current_path)
    backup = load_json(backup_path)
    current_phase = current["meta"]["phase"]
    backup_phase = backup["meta"]["phase"]
    if PHASES.index(current_phase) - 1 != PHASES.index(backup_phase):
        raise RuntimeError(f"backup phase {backup_phase} is not adjacent to {current_phase}")
    issues = schema_issues(root, backup, "task.schema.json")
    if issues:
        raise RuntimeError("backup does not satisfy the strict task schema")
    failed_snapshot = task_dir / "task.json.rollback-source"
    shutil.copy2(current_path, failed_snapshot)
    atomic_copy(backup_path, current_path)
    receipt_dir = task_dir / "transition-receipts"
    receipt_dir.mkdir(exist_ok=True)
    receipt = {
        "schema": "pdca.rollback/v1",
        "task_id": backup["id"],
        "from": current_phase,
        "to": backup_phase,
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    (receipt_dir / f"rollback-{current_phase}-to-{backup_phase}.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
