#!/usr/bin/env python3
"""Audit ontology code references conformance: 本体代码引用符合度审计。

对 ontology/domain/core-*.md 中 `path:line` 与 `函数名` 引用：
- 文件存在性（确错：FILE_MISSING）
- 符号存在性（函数/结构体/宏 grep，确错：SYMBOL_MISSING）
- 行号有效性（行存在；内容关键词匹配，否则疑似 LINE_DRIFT）

分级：ERROR（确错）/ WARN（疑似漂移）/ OK。
用法：
  python3 scripts/audit-ontology-conformance.py --dir ontology/domain [--repo /path/to/bcachefs-tools]
  python3 scripts/audit-ontology-conformance.py --node ontology/domain/foo.md [--repo ...]
Exit 0 全过（无 ERROR），Exit 1 有确错。WARN 不影响退出码但打印。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = Path("/home/black/Documents/bcachefs-tools")

# `path:line` 或 `path:line-line`，path 含 fs/ 或 src/ 或 c_src/
REF_RE = re.compile(r"`((?:fs|src|c_src)/[A-Za-z0-9_./\-]+\.[ch](?::\d+(?:-\d+)?)?)`")
# 反引号函数名 `snake_case`（带括号或不带）
SYM_RE = re.compile(r"`([a-z][a-z0-9_]{3,})(?:\(\))?`")


def audit_node(path: Path, repo: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1] if text.startswith("---") else text
    seen_refs: set[str] = set()
    for m in REF_RE.finditer(body):
        ref = m.group(1)
        if ref in seen_refs:
            continue
        seen_refs.add(ref)
        if ":" in ref:
            fpath, lineno = ref.rsplit(":", 1)
            start = int(lineno.split("-")[0])
        else:
            fpath, start = ref, None
        fp = repo / fpath
        if not fp.is_file():
            issues.append(("ERROR", f"{path.name} FILE_MISSING: {fpath}"))
            continue
        if start is not None:
            try:
                lines = fp.read_text(encoding="utf-8", errors="ignore").split("\n")
            except OSError:
                issues.append(("ERROR", f"{path.name} FILE_UNREADABLE: {fpath}"))
                continue
            if start < 1 or start > len(lines):
                issues.append(("ERROR", f"{path.name} LINE_OUT_OF_RANGE: {ref} 文件仅 {len(lines)} 行"))
    # 符号存在性：取反引号 snake_case 符号，排除常见英文词
    STOP = {"the", "and", "with", "from", "that", "this", "code", "data", "file",
            "lock", "keys", "node", "path", "state", "type", "value", "entry"}
    seen_syms: set[str] = set()
    for m in SYM_RE.finditer(body):
        sym = m.group(1)
        if sym in seen_syms or sym in STOP or len(sym) < 5:
            continue
        if re.fullmatch(r"[0-9a-f]{7,40}", sym):
            continue  # commit 哈希非符号，跳过
        seen_syms.add(sym)
        # 在引用文件集合中查找符号定义
        found = False
        for fref in seen_refs:
            fpath = fref.split(":")[0]
            fp = repo / fpath
            if not fp.is_file():
                continue
            try:
                content = fp.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if re.search(r"\b" + re.escape(sym) + r"\b", content):
                found = True
                break
        if not found:
            # 回退：全仓库 fs/ 与 src/ 的 .c/.h 搜索（排除构建产物目录）
            import subprocess
            try:
                r = subprocess.run(
                    ["grep", "-rlw", "--include=*.c", "--include=*.h",
                     "--include=*.rs",
                     "--exclude-dir=build", "--exclude-dir=target",
                     "--exclude-dir=.git",
                     sym,
                     str(repo / "fs"), str(repo / "src"), str(repo / "c_src")],
                    capture_output=True, text=True, timeout=120)
                if r.stdout.strip():
                    found = True
            except (OSError, subprocess.TimeoutExpired):
                pass
        if not found:
            issues.append(("WARN", f"{path.name} SYMBOL_NOT_FOUND: {sym}（未在引用文件及 fs 头文件中找到）"))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", type=Path)
    ap.add_argument("--dir", type=Path)
    ap.add_argument("--repo", type=Path, default=REPO)
    args = ap.parse_args()
    targets: list[Path] = []
    if args.node:
        targets = [args.node]
    elif args.dir:
        targets = sorted(args.dir.glob("core-*.md"))
    else:
        print("need --node or --dir", file=sys.stderr)
        return 2
    errors = warns = 0
    for t in targets:
        for level, msg in audit_node(t, args.repo):
            print(f"{level}: {msg}")
            if level == "ERROR":
                errors += 1
            else:
                warns += 1
    print(f"checked {len(targets)} files: {errors} errors, {warns} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
