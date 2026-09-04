#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-ai-friendly-confirmation（确认时间戳真值）；本体是源、代码是投射。
"""Append one confirmation entry to clarifications.jsonl with a real timestamp.

Why this exists: AI agents hand-writing ISO timestamps fabricate them (observed
twice in one day). The script generates ``at`` from the real clock and validates
against the clarification schema before touching the file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from pdca_core import load_jsonl, repo_root, schema_issues

CONFIRMATION_SOURCES = ("final_confirmation", "check_confirmation", "direction_confirm", "fix_confirmation")
RESPONSES = ("confirmed", "rejected", "partial")


def atomic_append(path: Path, line: str) -> None:
    """Append ``line`` atomically: write temp file, fsync, then replace."""
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            if path.is_file():
                handle.write(path.read_text(encoding="utf-8"))
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a confirmation with a real timestamp")
    parser.add_argument("--task-dir", required=True, type=Path)
    parser.add_argument("--source", required=True, choices=CONFIRMATION_SOURCES)
    parser.add_argument("--response", required=True, choices=RESPONSES)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()

    root = repo_root(args.root)
    task_dir = args.task_dir.resolve()
    path = task_dir / "clarifications.jsonl"

    if args.source == "final_confirmation" and args.response != "confirmed":
        parser.error("--response must be 'confirmed' for final_confirmation")
    if args.source == "fix_confirmation" and args.response not in ("confirmed", "rejected"):
        parser.error("--response must be 'confirmed' or 'rejected' for fix_confirmation")

    entry: dict = {
        "source": args.source,
        "summary": args.summary,
        "response": args.response,
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    issues = schema_issues(root, entry, "clarification.schema.json")
    if issues:
        for issue in issues:
            print(json.dumps(issue.as_dict(), ensure_ascii=False), file=sys.stderr)
        return 1

    existing = load_jsonl(path) if path.is_file() else []
    entries = [*existing, entry]
    if args.source == "final_confirmation":
        confirmed = [e for e in entries if e.get("source") == "final_confirmation"]
        if len(confirmed) > 1:
            print(json.dumps({"status": "rejected", "error": "DUPLICATE_FINAL_CONFIRMATION"}, ensure_ascii=False), file=sys.stderr)
            return 1

    lines = [json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in entries]
    atomic_append(path, lines[-1])

    print(json.dumps({"status": "appended", "task": task_dir.name, **entry}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
