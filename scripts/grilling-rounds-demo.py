#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/grilling-methodology（批量问法轮数实证）；本体是源、代码是投射。
"""grilling 批量问法真实轮数统计演示。

读取任务目录的 clarifications.jsonl，按 round 字段统计"批量问法"实际使用的
交互轮数，并与"一次只问一个"（每个条目一轮）对比。用于证明批量问法对真实
会话轮数的压缩效果（AC-4 的实证层，区别于纯函数模型层）。

用法:
  python3 scripts/grilling-rounds-demo.py <task-dir>...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_entries(path: Path) -> list[dict]:
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return [json.loads(ln) for ln in lines]


def rounds_used(entries: list[dict]) -> int:
    """批量问法轮数：distinct round 值数量。无 round 字段的条目各计一轮。"""
    rounds = {e["round"] for e in entries if "round" in e}
    legacy = sum(1 for e in entries if "round" not in e)
    return len(rounds) + legacy


def entries_as_rounds(entries: list[dict]) -> int:
    """旧"一次一问"轮数：每个条目一轮。"""
    return len(entries)


def summarize(path: Path) -> dict:
    entries = load_entries(path)
    return {
        "file": str(path),
        "entries": len(entries),
        "batch_rounds": rounds_used(entries),
        "one_at_a_time_rounds": entries_as_rounds(entries),
        "compression": len(entries) / rounds_used(entries) if rounds_used(entries) else 1.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dirs", nargs="+", type=Path)
    args = parser.parse_args()

    results = []
    for task_dir in args.task_dirs:
        path = task_dir / "clarifications.jsonl"
        if not path.is_file():
            print(json.dumps({"status": "missing", "file": str(path)}, ensure_ascii=False))
            continue
        results.append(summarize(path))

    for r in results:
        print(json.dumps(r, ensure_ascii=False))

    if not results:
        print("no valid clarifications.jsonl found", file=sys.stderr)
        return 1

    # 失败条件：任一会话批量问法未压缩轮数（batch >= one_at_a_time）
    regressions = [r for r in results if r["batch_rounds"] >= r["one_at_a_time_rounds"]]
    if regressions:
        print(f"REGRESSION: {len(regressions)} session(s) not compressed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
