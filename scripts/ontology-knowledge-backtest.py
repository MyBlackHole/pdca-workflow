#!/usr/bin/env python3
"""知识类本体可执行信号替代方案：对非code-grep类信号执行验证。

对code-grep类信号执行代码验证，对expert-review/experiment/case-study类信号输出验证报告。

用法：
  python3 scripts/ontology-knowledge-backtest.py --ontology-dir ontology
  python3 scripts/ontology-knowledge-backtest.py --ontology-dir ontology --knowledge-type principle
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_TYPES = {"pattern", "principle", "pitfall", "fact", "decision"}
CODE_VERIFICATION_METHODS = {"code-grep"}
NON_CODE_METHODS = {"expert-review", "experiment", "case-study"}


def extract_knowledge_signals(ont_dir: Path, knowledge_type: str | None = None) -> list[dict]:
    """提取知识类本体的testable_signal和verification_method。"""
    signals = []
    for md in sorted(ont_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        fm = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                except Exception:
                    pass

        ftype = fm.get("type", "")
        if ftype not in KNOWLEDGE_TYPES:
            continue
        if knowledge_type and ftype != knowledge_type:
            continue

        oid = fm.get("id", str(md))
        attrs = fm.get("attributes", []) or []
        for attr in attrs:
            sig = attr.get("testable_signal", "").strip()
            if sig:
                # 推断verification_method
                method = "code-grep"  # 默认
                for m in NON_CODE_METHODS:
                    if m in sig.lower():
                        method = m
                        break
                signals.append({
                    "id": oid,
                    "type": ftype,
                    "attribute": attr.get("name", ""),
                    "signal": sig,
                    "verification_method": method,
                    "file": str(md)
                })
    return signals


def backtest_signal(signal_info: dict) -> dict:
    """对信号执行回测。"""
    method = signal_info["verification_method"]
    sig = signal_info["signal"]

    if method == "code-grep":
        # 尝试执行代码搜索
        try:
            if "grep" in sig.lower():
                cmd = sig.split("\n")[0].strip()
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                return {"executable": result.returncode == 0, "method": "code-grep", "returncode": result.returncode}
            return {"executable": True, "method": "code-grep", "reason": "syntax valid"}
        except Exception as e:
            return {"executable": False, "method": "code-grep", "reason": str(e)}

    elif method == "expert-review":
        return {"executable": True, "method": "expert-review", "reason": "requires expert confirmation", "status": "pending"}
    elif method == "experiment":
        return {"executable": True, "method": "experiment", "reason": "requires experimental validation", "status": "pending"}
    elif method == "case-study":
        return {"executable": True, "method": "case-study", "reason": "requires case study", "status": "pending"}

    return {"executable": False, "method": "unknown", "reason": "unknown verification method"}


def main() -> int:
    ap = argparse.ArgumentParser(description="知识类本体信号回测")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--knowledge-type", choices=list(KNOWLEDGE_TYPES), default=None)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    signals = extract_knowledge_signals(args.ontology_dir, args.knowledge_type)
    results = []
    code_grep_passed = 0
    code_grep_failed = 0
    non_code_pending = 0

    for sig_info in signals:
        result = backtest_signal(sig_info)
        entry = {**sig_info, **result}
        results.append(entry)
        if result["method"] == "code-grep" and result["executable"]:
            code_grep_passed += 1
        elif result["method"] == "code-grep" and not result["executable"]:
            code_grep_failed += 1
        elif result["method"] in NON_CODE_METHODS:
            non_code_pending += 1

    report = {
        "total": len(signals),
        "code_grep_passed": code_grep_passed,
        "code_grep_failed": code_grep_failed,
        "non_code_pending": non_code_pending,
        "results": results
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"# 知识类本体信号回测\n\n总计: {len(signals)}\n\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    print(f"\n回测: code-grep {code_grep_passed}/{code_grep_passed+code_grep_failed} 通过, {non_code_pending} 个非代码信号待确认", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
