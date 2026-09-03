#!/usr/bin/env python3
"""检查本体独立性：domain/pattern 是否可脱离 records 独立理解。

判据（按本体重构教训 T0539）：
  I1 独立可读：正文不以 `> 来源：records/` 强耦合开头
  I2 信号自足：每条 testable_signal 至少含一次 `ontology/` 自检（grep 本体自身）
  I3 信号不唯记录：testable_signal 不得仅含 `records/` 而无 `ontology/` 自检
  I4 模式结构：pattern 须含 `## 上下文/## 问题/## 解` 三段（可复用模式）

对 `type: entity/fact` 等实现绑定型本体放宽 I2/I3（允许纯 records 信号），
仅对 `domain/pattern/concept` 等知识型本体强制独立性。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONT = ROOT / "ontology"

STRICT_TYPES = {"domain", "pattern", "concept", "principle", "decision"}

import argparse
import subprocess

import yaml

parser = argparse.ArgumentParser(description="本体独立性校验")
parser.add_argument("--changed", action="store_true", help="仅校验 git 变更的本体文件（用于 CI 增量门禁）")
parser.add_argument("--all", action="store_true", help="校验全量（默认，仅 I1/I3 强门禁阻断）")
args, _ = parser.parse_known_args()
changed_only = args.changed

if changed_only:
    # 仅检查 git 变更的本体文件（staged + unstaged + untracked 的 ontology/）
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    tracked = [ROOT / p for p in out.stdout.splitlines() if p.startswith("ontology/") and p.endswith(".md")]
    out2 = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, cwd=ROOT)
    untracked = [ROOT / p for p in out2.stdout.splitlines() if p.startswith("ontology/") and p.endswith(".md")]
    ontology_files = sorted(set(tracked + untracked))
else:
    ontology_files = sorted(ONT.rglob("*.md"))

def extract_frontmatter(text: str) -> dict:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            data = yaml.safe_load(parts[1])
            return data if isinstance(data, dict) else {}
    return {}

issues = []
for md in ontology_files:
    if md.name == "README.md":
        continue
    text = md.read_text(encoding="utf-8")
    fm = extract_frontmatter(text)
    otype = fm.get("type", "")
    if otype not in STRICT_TYPES:
        continue
    body = text.split("---", 2)[2] if text.startswith("---") else text
    rel = md.relative_to(ONT)

    # I1
    if re.search(r"^\s*>\s*来源：\s*records/", body, re.M):
        issues.append(f"I1 {rel}: 正文以 `> 来源：records/` 强耦合，应改为领域定义（独立可读）")

    # I2/I3 per-signal
    signals = re.findall(r"testable_signal:\s*\"([^\"]+)\"", text)
    for sig in signals:
        has_ont = "ontology/" in sig
        has_rec = "records/" in sig
        if not has_ont:
            issues.append(f"I2 {rel}: testable_signal 无 `ontology/` 自检: {sig[:80]}")
        if has_rec and not has_ont:
            issues.append(f"I3 {rel}: testable_signal 仅含 `records/` 无自检: {sig[:80]}")

    # I4
    if otype == "pattern":
        for sec in ["## 上下文", "## 问题", "## 解"]:
            if sec not in body:
                issues.append(f"I4 {rel}: pattern 缺 `{sec}` 段（上下文/问题/解）")

# 分级：I1/I3 为强门禁（FAIL），I2/I4 为弱门禁（WARN，仅提示存量）
fails = [x for x in issues if x.startswith("I1") or x.startswith("I3")]
warns = [x for x in issues if x.startswith("I2") or x.startswith("I4")]
if warns:
    print(f"WARN: {len(warns)} 弱门禁（建议整改，不阻断存量）")
    for it in warns[:10]:
        print(f"  - {it}")
    if len(warns) > 10:
        print(f"  ... 余 {len(warns)-10} 条省略")
if fails:
    print(f"FAIL: {len(fails)} 强门禁（I1 正文耦合 / I3 信号唯记录）")
    for it in fails:
        print(f"  - {it}")
    sys.exit(1)
else:
    print(f"OK: 强门禁通过（0 FAIL，{len(warns)} WARN 存量待收敛）")
    sys.exit(0)
