#!/usr/bin/env python3
"""本体主题覆盖校验（T2118）。

按主题词表扫描本体 md 文件：每个 topic 的 keywords 任一命中（大小写不敏感、
任一文件）即算覆盖；全部覆盖退出 0 并打印 OK，缺失则打印缺失 topic id 并退出 1。

用法：
  python3 scripts/check-ontology-topic-coverage.py --topics /tmp/topics.json --files ontology/pattern/sm4-storage-encryption.md ontology/pattern/sm4-s3-encryption.md
  python3 scripts/check-ontology-topic-coverage.py --help

词表格式（JSON）：
  {"topics": [{"id": "s3-三态", "keywords": ["gmssl", "三态"]}, ...]}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topics", required=True, type=Path, help="主题词表 JSON 文件：{\"topics\": [{\"id\": ..., \"keywords\": [...]}, ...]}")
    ap.add_argument("--files", required=True, nargs="+", type=Path, help="待查本体 md 文件（可多个）")
    args = ap.parse_args()

    if not args.topics.is_file():
        print(f"TOPICS_NOT_FOUND: {args.topics}", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.topics.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"TOPICS_INVALID_JSON: {e}", file=sys.stderr)
        return 2

    topics = data.get("topics") if isinstance(data, dict) else None
    if not isinstance(topics, list) or not topics:
        print("TOPICS_EMPTY: JSON 须含非空 topics 数组", file=sys.stderr)
        return 2

    haystack_parts: list[str] = []
    for f in args.files:
        if not f.is_file():
            print(f"FILE_NOT_FOUND: {f}", file=sys.stderr)
            return 2
        try:
            haystack_parts.append(f.read_text(encoding="utf-8"))
        except OSError as e:
            print(f"FILE_READ_ERROR: {f}: {e}", file=sys.stderr)
            return 2
    haystack = "\n".join(haystack_parts).lower()

    missing: list[str] = []
    for t in topics:
        tid = t.get("id", "<no-id>") if isinstance(t, dict) else "<no-id>"
        kws = t.get("keywords", []) if isinstance(t, dict) else []
        if not isinstance(kws, list) or not kws:
            missing.append(str(tid))
            continue
        hit = any(isinstance(kw, str) and kw and kw.lower() in haystack for kw in kws)
        if not hit:
            missing.append(str(tid))

    if not missing:
        print(f"OK: {len(topics)}/{len(topics)} topics covered")
        return 0

    for mid in missing:
        print(f"MISSING: {mid}")
    print(f"FAIL: {len(missing)}/{len(topics)} topics missing")
    return 1


if __name__ == "__main__":
    sys.exit(main())
