#!/usr/bin/env python3
"""triager-brief 决策兑现回读器（T0269，第五轮）。

从 `triager-brief.md` 提取关键决策（推荐方向 / 已验证问题 / 信息缺口 / 风险），
在任务产出（design.md / research.md / implement.md / do-evidence*.md / conclusion.md）
中检测命中，生成回读矩阵骨架；并可解析已填写的矩阵统计兑现率。

决策类型：
  - recommendation   `## 推荐方向` 列表项
  - verified_issue   `## 已验证问题` / `## 事实核验` 列表项
  - information_gap  `## 信息缺口` 列表项
  - risk             `## 风险` 列表项

兑现状态（审计在矩阵中标注）：
  - fulfilled        决策已进入实施产出
  - partial          部分采纳 / 仍在进行中
  - not-fulfilled    未采纳或被明确推翻
  - unknown          无法判定

用法：
  recall-brief-decisions.py --task-dir <task>          # 生成回读矩阵骨架
  recall-brief-decisions.py --task-dir <task> --out <path>   # 写入文件
  recall-brief-decisions.py --matrix <recall-matrix.md>      # 解析矩阵统计兑现率
  recall-brief-decisions.py --matrix <path> --json           # JSON 输出
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SECTION_TYPES = [
    (r"^##\s*推荐方向", "recommendation"),
    (r"^##\s*已验证问题", "verified_issue"),
    (r"^##\s*事实核验", "verified_issue"),
    (r"^##\s*信息缺口", "information_gap"),
    (r"^##\s*风险", "risk"),
]

PRODUCTION_FILES = [
    "design.md",
    "research.md",
    "implement.md",
    "do-evidence*.md",
    "conclusion.md",
]

EN_STOP = {
    "the", "and", "for", "with", "not", "are", "this", "that", "from",
    "but", "only", "into", "must", "will", "has", "have", "its", "was",
    "would", "can", "could", "should", "each", "every", "over", "under",
    "using", "used", "use", "via", "per", "such", "than", "then", "there",
    "these", "those", "more", "most", "also", "any", "may", "been", "being",
    "make", "made", "still", "cannot", "needs", "based", "basedon", "current",
    "existing", "following", "maintain", "keep", "do", "does", "done", "what",
}

CN_STOP = {
    "以及", "对于", "以及", "通过", "用于", "需要", "必须", "可以", "不能",
    "不会", "如果", "同时", "以及", "仍然", "为了", "根据", "作为", "因为",
    "所以", "但是", "并且", "或者", "这个", "那个", "一个", "当前", "现有",
    "之后", "之前", "内部", "外部", "不同", "目标", "要求", "进行", "完成",
    "继续", "采用", "保持", "确保", "避免", "新增", "修改", "实现", "支持",
    "使用", "通过", "提供", "包含", "涉及", "出现", "存在", "对应", "属于",
}

TOKEN_EN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
TOKEN_CN = re.compile(r"[\u4e00-\u9fff]{2,}")


@dataclass
class Decision:
    index: int
    dtype: str
    text: str
    section: str
    keywords: list[str] = field(default_factory=list)


def parse_brief(text: str) -> list[Decision]:
    """解析 brief，按章节提取决策列表项。"""
    lines = text.splitlines()
    decisions: list[Decision] = []
    idx = 0
    current_type: str | None = None
    current_section = ""
    for line in lines:
        stripped = line.strip()
        sec = None
        for pat, dtype in SECTION_TYPES:
            if re.match(pat, stripped):
                sec = (dtype, stripped.lstrip("# ").strip())
                break
        if sec:
            current_type, current_section = sec
            continue
        if current_type is None:
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            item = stripped[2:].strip()
            if item:
                idx += 1
                decisions.append(Decision(
                    index=idx,
                    dtype=current_type,
                    text=item,
                    section=current_section,
                ))
    return decisions


def extract_keywords(text: str) -> list[str]:
    """从决策文本抽取中英文关键词（去停用词，去重保序）。"""
    words = [w for w in TOKEN_EN.findall(text) if w.lower() not in EN_STOP]
    words += [w for w in TOKEN_CN.findall(text) if w not in CN_STOP]
    seen: set[str] = set()
    out: list[str] = []
    for w in words:
        key = w.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(w)
    return out


def production_files(task_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pat in PRODUCTION_FILES:
        files += sorted(task_dir.glob(pat))
    return files


def detect_hits(decision: Decision, task_dir: Path) -> dict[str, int]:
    """对决策关键词在各产出文件中计数命中。返回 {file: hit_count}。"""
    if not decision.keywords:
        decision.keywords = extract_keywords(decision.text)
    hits: dict[str, int] = {}
    for f in production_files(task_dir):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        count = sum(text.lower().count(k.lower()) for k in decision.keywords)
        if count:
            hits[f.name] = count
    return hits


def render_matrix(task_dir: Path, brief_text: str) -> str:
    decisions = parse_brief(brief_text)
    lines = [
        f"# 决策兑现回读矩阵：{task_dir.name}",
        "",
        f"任务: `{task_dir.name}` | brief: `triager-brief.md` | 决策数: {len(decisions)}",
        "",
        "兑现状态: fulfilled=决策已进入实施产出 | partial=部分采纳/进行中 | "
        "not-fulfilled=未采纳或推翻 | unknown=无法判定",
        "",
        "| # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |",
        "|---|------|------|---------|---------|------|",
    ]
    for d in decisions:
        hits = detect_hits(d, task_dir)
        hit_txt = "; ".join(f"{k}({c})" for k, c in hits.items()) or "-"
        text = d.text.replace("|", "/")
        lines.append(
            f"| {d.index} | {d.dtype} | {text} | {hit_txt} | - | |"
        )
    return "\n".join(lines) + "\n"


def parse_matrix(md_text: str) -> dict:
    """解析已填写的矩阵，统计兑现率。

    行格式: | # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |
    unknown 不计入可判定决策。
    """
    rows = []
    for line in md_text.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        num, dtype, text, hit, status, basis = cells[:6]
        if num == "#":
            continue
        rows.append({
            "index": num,
            "type": dtype,
            "decision": text,
            "hits": hit,
            "status": status,
            "basis": basis,
        })
    valid = {"fulfilled", "partial", "not-fulfilled"}
    judged = [r for r in rows if r["status"] in valid]
    unknown = [r for r in rows if r["status"] == "unknown"]
    unjudged = [r for r in rows if r["status"] not in valid | {"unknown"}]
    fulfilled = sum(1 for r in judged if r["status"] == "fulfilled")
    partial = sum(1 for r in judged if r["status"] == "partial")
    not_fulfilled = sum(1 for r in judged if r["status"] == "not-fulfilled")
    rate = round((fulfilled + partial) / len(judged) * 100, 1) if judged else 0.0
    return {
        "total_decisions": len(rows),
        "judged": len(judged),
        "fulfilled": fulfilled,
        "partial": partial,
        "not_fulfilled": not_fulfilled,
        "unknown": len(unknown),
        "unjudged": len(unjudged),
        "fulfillment_rate": rate,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="triager-brief 决策兑现回读器")
    parser.add_argument("--task-dir", help="任务目录（含 triager-brief.md 与产出）")
    parser.add_argument("--out", help="矩阵骨架输出文件")
    parser.add_argument("--matrix", help="已填写矩阵文件，统计兑现率")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if args.matrix:
        path = Path(args.matrix)
        if not path.exists():
            print(f"文件不存在: {path}", file=sys.stderr)
            return 1
        stats = parse_matrix(path.read_text(encoding="utf-8", errors="replace"))
        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print("# 决策兑现率")
            print(f"总决策数: {stats['total_decisions']}")
            print(f"可判定: {stats['judged']}（fulfilled {stats['fulfilled']} / "
                  f"partial {stats['partial']} / not-fulfilled {stats['not_fulfilled']}）")
            print(f"unknown: {stats['unknown']} | 未标注: {stats['unjudged']}")
            print(f"兑现率: {stats['fulfillment_rate']}%")
        return 0

    if args.task_dir:
        task_dir = Path(args.task_dir)
        brief = task_dir / "triager-brief.md"
        if not brief.exists():
            print(f"未找到 triager-brief.md: {brief}", file=sys.stderr)
            return 1
        text = brief.read_text(encoding="utf-8", errors="replace")
        matrix = render_matrix(task_dir, text)
        if args.out:
            Path(args.out).write_text(matrix, encoding="utf-8")
            print(f"矩阵已写入: {args.out}")
        else:
            sys.stdout.write(matrix)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
