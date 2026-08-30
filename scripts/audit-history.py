#!/usr/bin/env python3
"""Create and apply protected manifests for strict-schema-incompatible tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from pdca_core import path_is_protected, repo_root, task_issues


def directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(file_path.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def tracked_state(root: Path, path: Path) -> tuple[int, int]:
    total = sum(1 for item in path.rglob("*") if item.is_file())
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", path.relative_to(root).as_posix()],
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = len([line for line in completed.stdout.splitlines() if line])
    return tracked, total


def validate_target(root: Path, raw_path: str, scope: str) -> Path:
    if any(character in raw_path for character in "*?[]"):
        raise RuntimeError(f"patterns are forbidden in deletion target: {raw_path}")
    target = (root / raw_path).resolve()
    tasks_root = (root / "pdca/tasks").resolve()
    archive_root = (tasks_root / "archive").resolve()
    if scope == "active":
        if target.parent != tasks_root or target == archive_root:
            raise RuntimeError(f"unsafe active deletion target: {raw_path}")
    elif scope == "archive":
        target.relative_to(archive_root)
        if target == archive_root:
            raise RuntimeError(f"unsafe archive deletion target: {raw_path}")
    else:
        raise RuntimeError(f"unknown deletion scope: {scope}")
    if path_is_protected(root, target):
        raise RuntimeError(f"unsafe deletion target: {raw_path}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", type=Path, metavar="MANIFEST")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirm-target-count", type=int)
    parser.add_argument("--allow-unrecoverable", action="store_true")
    parser.add_argument("--scope", choices=("active", "archive"))
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    root = repo_root(args.root)
    if args.apply:
        payload = json.loads(args.apply.read_text(encoding="utf-8"))
        scope = payload.get("scope")
        if (
            payload.get("schema") != "pdca.deletion-manifest/v1"
            or payload.get("mode") != "dry-run"
            or scope not in {"active", "archive"}
        ):
            raise RuntimeError("invalid deletion manifest")
        targets = payload.get("targets", [])
        if payload.get("target_count") != len(targets):
            raise RuntimeError("manifest target_count does not match targets")
        if args.confirm_target_count != len(targets):
            raise RuntimeError("--confirm-target-count must exactly match the manifest")
        unrecoverable = [item["path"] for item in targets if not item.get("git_recoverable")]
        if unrecoverable and not args.allow_unrecoverable:
            raise RuntimeError("manifest contains targets not recoverable by Git; explicit approval is required")
        resolved = []
        for item in targets:
            target = validate_target(root, item["path"], scope)
            if not target.is_dir():
                raise RuntimeError(f"target missing or not a directory: {item['path']}")
            if directory_digest(target) != item["digest"]:
                raise RuntimeError(f"target changed after dry-run: {item['path']}")
            if not task_issues(root, target):
                raise RuntimeError(f"target is now a valid strict task: {item['path']}")
            resolved.append(target)
        for target in resolved:
            shutil.rmtree(target)
        print(json.dumps({"schema": "pdca.deletion-result/v1", "deleted": [item["path"] for item in targets]}, ensure_ascii=False, indent=2))
        return 0

    if not args.scope:
        parser.error("--scope is required with --dry-run")
    if args.scope == "active":
        task_paths = [
            path
            for path in sorted((root / "pdca/tasks").glob("*/task.json"))
            if path.parent.name != "archive"
        ]
    else:
        task_paths = sorted((root / "pdca/tasks/archive").glob("**/task.json"))
    source_commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    targets = []
    for task_path in task_paths:
        task_dir = task_path.parent.resolve()
        if path_is_protected(root, task_dir):
            raise RuntimeError(f"protected path selected: {task_dir}")
        issues = task_issues(root, task_dir)
        if issues:
            tracked, total = tracked_state(root, task_dir)
            recoverable = total > 0 and tracked == total
            targets.append(
                {
                    "path": task_dir.relative_to(root).as_posix(),
                    "digest": directory_digest(task_dir),
                    "tracked_files": tracked,
                    "total_files": total,
                    "git_recoverable": recoverable,
                    "reasons": [issue.as_dict() for issue in issues],
                    "recovery": (
                        f"git restore --source={source_commit} -- {task_dir.relative_to(root).as_posix()}"
                        if recoverable
                        else None
                    ),
                }
            )
    payload = {
        "schema": "pdca.deletion-manifest/v1",
        "mode": "dry-run",
        "scope": args.scope,
        "source_commit": source_commit,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "protected_prefixes": ["records/", "ontology/domain/", "pdca/journal/"],
        "target_count": len(targets),
        "targets": targets,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
