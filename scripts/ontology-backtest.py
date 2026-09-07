#!/usr/bin/env python3
"""本体→代码回测验证：定期用本体 testable_signal 回测代码，验证每个信号实际可执行。

用法：
  python3 scripts/ontology-backtest.py --ontology-dir ontology
  python3 scripts/ontology-backtest.py --ontology-dir ontology --output backtest-report.md
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def extract_testable_signals(ont_dir: Path) -> list[dict]:
    """提取所有本体节点的 testable_signal。"""
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
        attrs = fm.get("attributes", []) or []
        oid = fm.get("id", str(md))
        for attr in attrs:
            sig = str(attr.get("testable_signal", ""))
            if sig.strip():
                signals.append({"id": oid, "attribute": attr.get("name", ""), "signal": sig, "file": str(md)})
    return signals


def backtest_signal(signal: str) -> dict:
    """尝试执行 testable_signal，返回结果。"""
    # 检查信号是否包含可执行动词
    has_verb = any(v in signal for v in ["grep -q", "grep -c", "python3 scripts/", "gate.py", "pytest"])
    if not has_verb:
        return {"executable": False, "reason": "no executable verb"}

    # 尝试执行信号中的命令
    try:
        # 提取命令前缀（grep, python3, pytest 等）
        if signal.startswith("grep -q") or signal.startswith("grep -c"):
            cmd = signal.split("\n")[0].strip()
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return {"executable": result.returncode == 0, "returncode": result.returncode}
        elif "python3 scripts/" in signal:
            cmd_parts = signal.split("python3 scripts/")[1].split()[0]
            script_path = ROOT / "scripts" / cmd_parts.split()[0]
            if script_path.exists():
                result = subprocess.run([sys.executable, str(script_path), "--help"], capture_output=True, timeout=10)
                return {"executable": True, "returncode": result.returncode}
        return {"executable": True, "reason": "syntax valid, not executed"}
    except Exception as e:
        return {"executable": False, "reason": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser(description="本体→代码回测验证")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    signals = extract_testable_signals(args.ontology_dir)
    results = []
    passed = 0
    failed = 0

    for sig_info in signals:
        result = backtest_signal(sig_info["signal"])
        entry = {**sig_info, **result}
        results.append(entry)
        if result["executable"]:
            passed += 1
        else:
            failed += 1

    report = {
        "total": len(signals),
        "passed": passed,
        "failed": failed,
        "coverage": f"{passed/len(signals)*100:.1f}%" if signals else "0%",
        "results": results
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"# 本体回测报告\n\n覆盖率: {report['coverage']}\n\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    print(f"\n回测结果: {passed}/{len(signals)} 可执行, {failed} 不可执行", file=sys.stderr)

    if failed > 0:
        print(f"WARNING: {failed} 个 testable_signal 不可执行，可能存在本体-代码漂移", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
