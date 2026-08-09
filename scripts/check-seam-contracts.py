#!/usr/bin/env python3
"""仓库级 seam 契约门禁：批量校验活跃任务 spec 的 seam 声明。

对 pdca/tasks/（不含 archive/）下所有含 `### 声明的测试接缝` 子节的
spec（prd.md）运行 seam_contract 校验，任一失败则退出码非 0。
供 CI/提交前门禁调用，与 flow-plan P6 的单任务校验互补
（P6 防单个任务漏检，本脚本防跨任务回归）。

归档任务（archive/）不扫描：其 seam 指向的历史测试文件可能已随
外部项目生命周期移除（T0240 实测：T0234 FastAPI 归档 spec 的
tests/test_service.py 等已不存在），归档 spec 为不可变记录。

用法:
  python3 scripts/check-seam-contracts.py             # 扫描活跃任务
  python3 scripts/check-seam-contracts.py --root .    # 指定仓库根
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pdca_core import repo_root
from seam_contract import validate_seams


def find_active_specs(tasks_dir: Path) -> list[Path]:
    """返回活跃任务目录下含 seam 子节的 spec（prd.md），升序排列。"""
    specs: list[Path] = []
    for prd in (tasks_dir / "pdca/tasks").glob("**/prd.md"):
        if "archive" in prd.parts:
            continue
        text = prd.read_text(encoding="utf-8")
        if "声明的测试接缝" in text and "- seam:" in text:
            specs.append(prd)
    return sorted(specs)


def check_all(specs: list[Path], base_dir: Path) -> tuple[dict[str, list[str]], list[str]]:
    """批量校验，返回 (spec 路径 → 问题列表) 与 (无 seam 问题的 spec 集合)。"""
    issues_per_spec: dict[str, list[str]] = {}
    clean_specs: list[str] = []
    for spec in specs:
        issues = validate_seams(spec, base_dir)
        if issues:
            issues_per_spec[str(spec)] = issues
        else:
            clean_specs.append(str(spec))
    return issues_per_spec, clean_specs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--base-dir", type=Path, default=None,
                        help="测试文件相对基准目录（默认 = 仓库根 root）")
    args = parser.parse_args()

    root = repo_root(args.root)
    base_dir = args.base_dir if args.base_dir is not None else root
    specs = find_active_specs(root)
    issues_per_spec, clean_specs = check_all(specs, base_dir)
    result = {
        "valid": not issues_per_spec,
        "checked": len(specs),
        "clean": clean_specs,
        "issues": issues_per_spec,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues_per_spec else 1


if __name__ == "__main__":
    sys.exit(main())
