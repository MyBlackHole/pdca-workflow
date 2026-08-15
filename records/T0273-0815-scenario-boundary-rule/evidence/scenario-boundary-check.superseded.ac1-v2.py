#!/usr/bin/env python3
"""场景归属边界判定检查器（T0273）。

解决 research/development 场景归属无机械判定手段的问题。判定标准：
**含可测试代码产出（脚本/测试/可回归验证）→ development；纯结论性调研 → research。**

历史错配任务 T0268-T0272 均标 research 但实际产出可测试工具代码，本检查器据此
建立判定规则，历史任务不改，仅作为回归夹具。

用法：
  scenario-boundary-check.py --judge --desc "<描述>" \
      [--code-scripts <scripts 产出>] [--code-tests <tests 产出>] \
      [--task-id <id>] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys

CODE_SIGNALS = ("script", "scripts/", "工具", "工具代码", "测试", "tests/", "回归", "验证器", "实现")
REPORT_ONLY = ("调研", "报告", "可行性", "分析", "结论", "review", "研究")


def judge(*, desc: str, code_scripts: str | None, code_tests: str | None) -> dict:
    evidence: list[str] = []
    code_signals: list[str] = []

    if code_scripts:
        code_signals.append(f"脚本产出: {code_scripts}")
    if code_tests:
        code_signals.append(f"测试产出: {code_tests}")

    cleaned = desc
    for neg in ("无脚本", "无测试", "没有脚本", "没有测试", "无代码", "不产出"):
        cleaned = cleaned.replace(neg, "X")

    for sig in CODE_SIGNALS:
        if sig.lower() in cleaned.lower():
            code_signals.append(f"描述含代码信号: {sig}")

    if code_signals:
        return {
            "scenario": "development",
            "reason": "可测试代码产出",
            "evidence": code_signals,
        }

    report_signals = [s for s in REPORT_ONLY if s.lower() in desc.lower()]
    if report_signals:
        return {
            "scenario": "research",
            "reason": "纯结论性调研（无代码产出）",
            "evidence": [f"描述含调研信号: {s}" for s in report_signals],
        }

    return {
        "scenario": "unknown",
        "reason": "无代码产出信号亦无调研信号，无法判定",
        "evidence": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--judge", action="store_true", help="执行单次判定")
    ap.add_argument("--desc", required="--judge" in sys.argv, default="", help="任务描述")
    ap.add_argument("--code-scripts", default=None, help="脚本产出路径信号")
    ap.add_argument("--code-tests", default=None, help="测试产出路径信号")
    ap.add_argument("--task-id", default=None, help="任务 ID（仅作标注）")
    args = ap.parse_args()

    if not args.judge:
        ap.error("--judge 必填")
    if not args.desc and not args.code_scripts and not args.code_tests:
        return 1

    result = judge(desc=args.desc, code_scripts=args.code_scripts, code_tests=args.code_tests)
    if args.task_id:
        result["task_id"] = args.task_id

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["scenario"] != "unknown" else 1


if __name__ == "__main__":
    sys.exit(main())
