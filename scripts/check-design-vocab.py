#!/usr/bin/env python3
# 本体投射[T2053]：ontology:domain/skill-design-it-twice（接口设计词汇契约）；本体是源、代码是投射。
"""design-it-twice 词汇契约校验器。

校验 design-it-twice 技能产出的接口设计文档只允许词汇表术语
（module/interface/seam/adapter/depth/leverage/locality），拒绝
词汇表明确 Avoid 的词（component/service/API/boundary）。
与 T0231 的 source 术语一致性测试同构：契约由脚本强制，可回归验证。

适用范围：词汇契约只约束接口设计文档（doc-type=design，默认）。
普通文档（需求/PRD/实现注释）通过 --doc-type other 跳过检查，
避免 component/service/API 等通用词误报（T0234 实测教训）。

用法:
  cat design.md | python3 scripts/check-design-vocab.py            # design 检查
  python3 scripts/check-design-vocab.py --doc-type design < design.md
  python3 scripts/check-design-vocab.py --doc-type other < prd.md  # 跳过检查
"""

from __future__ import annotations

import argparse
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

DOC_TYPES = ("design", "other")


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


def check_scoped(text: str, doc_type: str) -> dict:
    """按文档类型校验：design 检查词汇契约；other 跳过（不误报）。"""
    if doc_type != "design":
        return {"vocab_ok": True, "violations": [], "skipped": True, "doc_type": doc_type}
    result = check(text)
    result["skipped"] = False
    result["doc_type"] = doc_type
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--doc-type",
        choices=DOC_TYPES,
        default="design",
        help="文档类型：design（接口设计文档，默认，校验词汇契约）/ other（跳过检查）",
    )
    args = parser.parse_args()

    text = sys.stdin.read()
    if not text.strip():
        print(json.dumps({"error": "stdin 为空", "vocab_ok": False}, ensure_ascii=False))
        return 1
    result = check_scoped(text, args.doc_type)
    result["valid_terms"] = list(VOCAB_TERMS)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
