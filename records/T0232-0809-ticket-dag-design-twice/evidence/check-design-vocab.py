#!/usr/bin/env python3
"""design-it-twice 词汇契约校验器。

校验 design-it-twice 技能产出的接口设计文档只允许词汇表术语
（module/interface/seam/adapter/depth/leverage/locality），拒绝
词汇表明确 Avoid 的词（component/service/API/boundary）。
与 T0231 的 source 术语一致性测试同构：契约由脚本强制，可回归验证。

用法:
  cat design.md | python3 scripts/check-design-vocab.py
  python3 scripts/check-design-vocab.py < design.md
"""

from __future__ import annotations

import json
import re
import sys

# design-it-twice 强制词汇表（mattpocock codebase-design/SKILL.md）。
VOCAB_TERMS = (
    "module",
    "interface",
    "seam",
    "adapter",
    "depth",
    "leverage",
    "locality",
)

# 词汇表明确标注 "Avoid" 的替代词，产出文档中出现即违规。
FORBIDDEN_TERMS = (
    "component",
    "service",
    "boundary",
    "API",
)


def check(text: str) -> dict:
    """扫描文本，返回违规词列表（含重复词去重）与是否通过。"""
    lower = text.lower()
    violations: list[str] = []
    for term in FORBIDDEN_TERMS:
        # 用词边界避免误伤（如 boundary 出现在 boundary 之外的组合词）
        if re.search(rf"\b{re.escape(term.lower())}\b", lower):
            violations.append(term)

    # 中文章节合法术语不应被误判；此处只检测禁用词，合法词无需收集。
    return {"vocab_ok": not violations, "violations": violations}


def main() -> int:
    text = sys.stdin.read()
    if not text.strip():
        print(json.dumps({"error": "stdin 为空", "vocab_ok": False}, ensure_ascii=False))
        return 1
    result = check(text)
    result["valid_terms"] = list(VOCAB_TERMS)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
