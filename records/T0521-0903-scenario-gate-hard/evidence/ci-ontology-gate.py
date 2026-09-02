#!/usr/bin/env python3
"""CI / git-hook 共享门禁：ontology-validate + 相关任务收敛校验。

退出码 0 = 通过；非 0 = 阻断。供 `.git/hooks/pre-commit` 与
`.github/workflows/ontology-gate.yml` 复用，使本体门禁成为提交级硬门禁。

可选参数 paths：仅对受这些变更影响、且处于 check/act/archive 并登记了
convergence-map 的任务做收敛校验（传入 git diff 的变更文件列表即可缩小范围）。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="ontology CI gate")
    ap.add_argument("paths", nargs="*", help="changed paths to scope convergence check (optional)")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()
    root = args.root
    failures: list[str] = []

    # 1) 本体契约硬校验
    val = _run([sys.executable, str(ROOT / "scripts" / "ontology-validate.py"),
                "--ontology-dir", str(root / "ontology")])
    if val.returncode != 0:
        failures.append("ontology-validate 失败")
        sys.stdout.write(val.stdout)
        sys.stderr.write(val.stderr)

    # 1b) 双层闸 scenario_type 校验
    sc = _run([sys.executable, str(ROOT / "scripts" / "check-scenario-mismatch.py")])
    if sc.returncode != 0:
        failures.append("scenario双层闸 失败")
        sys.stdout.write(sc.stdout)
        sys.stderr.write(sc.stderr)

    # 2) 相关任务的收敛校验
    for tdir in (root / "pdca" / "tasks").rglob("task.json"):
        try:
            meta = json.loads(tdir.read_text()).get("meta", {})
        except Exception:
            continue
        phase = meta.get("phase")
        record = meta.get("record")
        if phase not in ("check", "act", "archive") or not record:
            continue
        cmap = root / "records" / record / "evidence" / "convergence-map.json"
        if not cmap.exists():
            continue
        if args.paths:
            hit = any(
                (root / p).resolve() == tdir
                or (root / p).resolve() == cmap
                or str(cmap).startswith(str((root / p).resolve()))
                for p in args.paths
            )
            if not hit:
                continue
        rc = _run([sys.executable, str(ROOT / "scripts" / "validate-convergence.py"),
                   "--task-dir", str(tdir.parent)]).returncode
        if rc != 0:
            failures.append(f"convergence 无效: {tdir.parent}")
            print(f"FAIL convergence: {tdir.parent}")

    if failures:
        print(f"\nGATE FAILED: {len(failures)} 项失败")
        return 1
    print("GATE OK: ontology-validate 通过，相关任务收敛校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
