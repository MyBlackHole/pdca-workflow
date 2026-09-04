#!/usr/bin/env python3
# 本体投射[T2053]：ontology:process/flow-do（声明接缝契约验证）；本体是源、代码是投射。
"""PRD seam 契约验证。

解析 spec 的 `### 声明的测试接缝` 子节中的 `- seam: <测试文件> -> <被测模块>`
行，验证：(1) 声明的测试文件存在；(2) 测试文件引用了声明的被测模块。
供 tests/test_seam_contract.py 与被 flow-plan 的 P6 门禁调用。

不追溯策略：无 `- seam:` 行的 spec 视为无声明 seam，直接通过。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEAM_LINE_RE = re.compile(r"^-\s+seam:\s+(\S+)\s*->\s*(\S+)\s*$")


def parse_seams(spec_text: str) -> list[tuple[str, str]]:
    """解析 `- seam: <测试文件> -> <被测模块>` 行，返回 [(测试, 被测)]。"""
    seams: list[tuple[str, str]] = []
    for line in spec_text.splitlines():
        m = SEAM_LINE_RE.match(line.strip())
        if m:
            seams.append((m.group(1), m.group(2)))
    return seams


def validate_seams(spec_path: Path, base_dir: Path) -> list[str]:
    """验证 spec 声明的 seam，返回问题列表（空 = 通过）。

    - 测试文件不存在 → issue "测试文件缺失: <path>"
    - 测试文件存在但不含被测模块路径引用 → issue "被测模块不一致: <mod>"
    无 seam 行 → 空问题（不追溯历史 spec）。
    """
    issues: list[str] = []
    if not spec_path.is_file():
        return [f"spec 文件缺失: {spec_path}"]
    seams = parse_seams(spec_path.read_text(encoding="utf-8"))
    for test_rel, target_rel in seams:
        test_path = base_dir / test_rel
        if not test_path.is_file():
            issues.append(f"测试文件缺失: {test_rel}")
            continue
        test_text = test_path.read_text(encoding="utf-8")
        # 被测模块以"模块路径"或"模块名"两种形式被引用均可
        target_name = target_rel.rstrip(".py").replace("/", ".")
        if target_rel not in test_text and target_name not in test_text:
            issues.append(f"被测模块不一致: {test_rel} 未引用 {target_rel}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="spec (PRD) 文件路径")
    parser.add_argument("--base-dir", type=Path, default=Path("."),
                        help="测试文件相对基准目录（默认当前目录）")
    args = parser.parse_args()

    issues = validate_seams(args.spec, args.base_dir)
    print(json.dumps({"valid": not issues, "issues": issues}, ensure_ascii=False))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
