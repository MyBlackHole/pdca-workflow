#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/frontier（可答前沿独立验证）；本体是源、代码是投射。
"""to-tickets blocking edges 的 ready-set / DAG 独立验证工具。

从 stdin 读 {task_id: [直接前置 task_id 列表]} JSON，输出 ready-set
（所有直接前置已完成的任务集合，completed 缺省为空）与依赖分批，
或依赖图非法错误。供 to-tickets 拆解后独立验证，也是
tests/test_ticket_dag.py 的直接被测对象。

用法:
  echo '{"T1": [], "T2": ["T1"], "T3": []}' | python3 scripts/compute-frontier.py
  echo '{"T1": ["T2"], "T2": ["T1"]}' | python3 scripts/compute-frontier.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ticket_dag import iter_tasks, ready_set, ready_set_batches  # noqa: E402


def parse_stdin(raw: str) -> dict[str, list[str]]:
    dag = json.loads(raw)
    if not isinstance(dag, dict):
        raise ValueError("输入必须是 {task_id: [前置 id 列表]} JSON 对象")
    return {str(k): list(v) for k, v in dag.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--completed",
        help='已完成任务 JSON 数组，如 \'["T1"]\'；缺省空集',
        default="[]",
    )
    args = parser.parse_args()

    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"error": "stdin 为空"}, ensure_ascii=False))
        return 1
    try:
        dag = parse_stdin(raw)
        completed = set(json.loads(args.completed))
    except (json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1

    tasks = dict(iter_tasks(dag))
    try:
        rs = ready_set(tasks, completed)
        batches = ready_set_batches(tasks)
    except ValueError as exc:
        print(json.dumps({"error": str(exc), "valid": False}, ensure_ascii=False))
        return 1

    print(json.dumps(
        {
            "valid": True,
            "ready_set": sorted(rs),
            "completed": sorted(completed),
            "batches": batches,
        },
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
