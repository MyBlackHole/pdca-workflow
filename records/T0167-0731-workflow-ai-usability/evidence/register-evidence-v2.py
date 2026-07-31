#!/usr/bin/env python3
"""Register one immutable evidence artifact with verified metadata."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from pdca_core import load_jsonl, repo_root, schema_issues, sha256_file


def atomic_text(path: Path, text: str) -> None:
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--criterion", required=True, action="append")
    parser.add_argument("--file")
    parser.add_argument("--replace", metavar="ID", help="supersede an existing evidence entry with this id")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()

    root = repo_root(args.root)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.record):
        parser.error("--record must be a safe direct child name")
    source = args.source.resolve()
    if not source.is_file():
        parser.error(f"--source is not a file: {source}")
    filename = args.file or source.name
    if Path(filename).name != filename or filename in {".", ".."}:
        parser.error("--file must be a plain filename")

    evidence_dir = root / "records" / args.record / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    destination = evidence_dir / filename
    manifest = evidence_dir / "manifest.jsonl"
    entries = load_jsonl(manifest) if manifest.is_file() else []
    replaced: dict[str, Any] | None = None
    if args.replace:
        matches = [entry for entry in entries if entry.get("id") == args.replace]
        if not matches:
            parser.error(f"no evidence entry with id: {args.replace}")
        replaced = matches[0]
        if replaced.get("superseded_by"):
            parser.error(f"entry {args.replace} is already superseded by {replaced['superseded_by']}")
        if replaced.get("file") == filename:
            parser.error(f"replacement must use a different --file than the superseded entry")
        if args.id == args.replace:
            parser.error("--id must differ from --replace")
    elif any(entry.get("id") == args.id for entry in entries):
        parser.error(f"duplicate evidence id: {args.id}")
    if destination.exists() or any(entry.get("file") == filename for entry in entries):
        parser.error(f"duplicate evidence filename: {filename}")

    descriptor, temporary_name = tempfile.mkstemp(prefix=filename + ".", dir=evidence_dir)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(source, temporary)
        entry = {
            "id": args.id,
            "file": filename,
            "kind": args.kind,
            "size": temporary.stat().st_size,
            "digest": sha256_file(temporary),
            "at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "criteria": list(dict.fromkeys(args.criterion)),
        }
        issues = schema_issues(root, entry, "evidence-entry.schema.json")
        if issues:
            for issue in issues:
                print(json.dumps(issue.as_dict(), ensure_ascii=False), file=sys.stderr)
            return 1
        if replaced is not None:
            old_file = evidence_dir / str(replaced["file"])
            old_file.rename(evidence_dir / f"{old_file.stem}.superseded.{entry['id']}{old_file.suffix}")
            superseded = {**replaced, "superseded_by": entry["id"]}
            lines = [
                json.dumps(item if item.get("id") != args.replace else superseded, ensure_ascii=False, separators=(",", ":"))
                for item in entries
            ]
        else:
            lines = [json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in entries]
        os.replace(temporary, destination)
        try:
            atomic_text(manifest, "\n".join([*lines, json.dumps(entry, ensure_ascii=False, separators=(",", ":"))]) + "\n")
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    finally:
        if temporary.exists():
            temporary.unlink()

    print(json.dumps({"status": "registered" if replaced is None else "replaced", "record": args.record, **entry}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
