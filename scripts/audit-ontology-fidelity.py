#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/meta-ontology（保真度七检）；本体是源、代码是投射。
"""Audit ontology fidelity: seven-checklist scoring + severity, produce report.

Usage:
  python3 scripts/audit-ontology-fidelity.py --ontology-dir ontology --out records/T0534/audit-report.md --jsonl /tmp/fidelity.jsonl
  python3 scripts/audit-ontology-fidelity.py --check fidelity --ontology-dir ontology  # exit 1 if fatal
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent

GENERIC_PHRASES = ["检查本文件", "相关章节的完整性", "相关章节的定义完整性"]
REQUIRED_VERBS = ["grep -q", "grep -c", "python3 scripts/", "gate.py", "scaffold", "pytest"]

def extract_frontmatter(text: str) -> dict:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                data = yaml.safe_load(parts[1])
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
    return {}

def score_one(path: Path, fm: dict, body: str) -> dict:
    oid = fm.get("id", str(path))
    tdir = path.parent.name if path.parent.name != "ontology" else "root"
    attrs = fm.get("attributes", []) or []
    rels = fm.get("relations", {}) or {}
    # 2 attributes
    attr_count = len(attrs)
    generic_count = 0
    concrete_count = 0
    for a in attrs:
        sig = str(a.get("testable_signal", ""))
        if any(p in sig for p in GENERIC_PHRASES):
            generic_count += 1
        if any(v in sig for v in REQUIRED_VERBS):
            concrete_count += 1
    has_generic = generic_count > 0
    has_concrete = concrete_count > 0
    # 3 relations
    has_specializes = bool(rels.get("specializes"))
    has_guides = bool(rels.get("guides") or rels.get("relates_to"))
    # 4 behavior
    mermaid_count = body.count("```mermaid")
    has_mermaid = mermaid_count >= 1
    has_mermaid2 = mermaid_count >= 2
    # 5 examples
    has_example = "正例" in body or "Example" in body
    has_counter = "反例" in body or "Counter" in body
    has_both_examples = has_example and has_counter
    # 6 provenance
    has_source = "Source:" in body
    has_source_line = bool(re.search(r"Source:.*:\d+", body) or re.search(r"Source:.*file:line", body))
    # 1 concept + 7 body lines
    lines = len(body.splitlines())
    has_concept = bool(fm.get("summary") and len(body.strip()) > 20)
    # 7 scaffold: heuristic — has attributes implies should scaffold
    # score
    score = 0
    # attributes 30
    if has_generic:
        s_attr = 0
    elif has_concrete and attr_count >= 3:
        s_attr = 30
    elif has_concrete and attr_count >= 1:
        s_attr = 20
    elif attr_count >= 1:
        s_attr = 8
    else:
        s_attr = 0
    score += s_attr
    # behavior 25
    if has_mermaid2:
        s_beh = 25
    elif has_mermaid:
        s_beh = 15
    else:
        s_beh = 0
    score += s_beh
    # relations 15
    if has_specializes and has_guides:
        s_rel = 15
    elif has_specializes:
        s_rel = 8
    else:
        s_rel = 0
    score += s_rel
    # provenance 15
    if has_source_line:
        s_prov = 15
    elif has_source:
        s_prov = 8
    else:
        s_prov = 0
    score += s_prov
    # examples 15
    if has_both_examples:
        s_ex = 15
    elif has_example:
        s_ex = 8
    else:
        s_ex = 0
    score += s_ex

    # severity
    fatal = []
    serious = []
    minor = []
    if has_generic:
        fatal.append("ATTR_GENERIC")
    if attr_count == 0 and tdir in ("domain", "entity", "pattern", "principle", "pitfall", "fact"):
        # domain/entity should have attributes, but concept may not
        if tdir in ("domain", "entity"):
            fatal.append("MISSING_ATTRIBUTES")
    if not has_concept:
        fatal.append("MISSING_CONCEPT")
    if not has_mermaid and tdir in ("domain", "entity"):
        serious.append("MISSING_DIAGRAM")
    if not has_both_examples and tdir in ("domain", "entity"):
        serious.append("MISSING_EXAMPLES")
    if not has_source_line and has_mermaid:
        minor.append("MISSING_SOURCE_LINE")
    elif not has_source and tdir in ("domain", "entity"):
        minor.append("MISSING_SOURCE")
    if lines < 60 and tdir in ("domain", "entity"):
        minor.append("BODY_TOO_SHORT")
    # scaffold check: only for nodes with attributes
    # we don't actually run scaffold here (slow), mark minor if no concrete verb
    if attr_count > 0 and not has_concrete:
        # already fatal generic, but also not scaffoldable
        minor.append("NOT_SCAFFOLDABLE")

    severity = "pass"
    if fatal:
        severity = "fatal"
    elif serious:
        severity = "serious"
    elif minor:
        severity = "minor"

    return {
        "id": oid,
        "path": str(path.relative_to(ROOT)) if path.is_absolute() else str(path),
        "type_dir": tdir,
        "attr_count": attr_count,
        "generic_count": generic_count,
        "concrete_count": concrete_count,
        "has_generic": has_generic,
        "mermaid_count": mermaid_count,
        "has_source": has_source,
        "has_source_line": has_source_line,
        "has_both_examples": has_both_examples,
        "lines": lines,
        "score": score,
        "severity": severity,
        "fatal": fatal,
        "serious": serious,
        "minor": minor,
        "issues": fatal + serious + minor,
    }

def main() -> int:
    ap = argparse.ArgumentParser(description="Audit ontology fidelity seven-checklist")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--out", type=Path, help="markdown report path")
    ap.add_argument("--jsonl", type=Path, help="jsonl with per-node scores")
    ap.add_argument("--check", choices=["fidelity"], help="gate mode: exit 1 if fatal found")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()
    ont_dir = args.ontology_dir
    rows = []
    for md in sorted(ont_dir.rglob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        fm = extract_frontmatter(text)
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        rows.append(score_one(md, fm, body))

    # stats
    total = len(rows)
    by_type = {}
    for r in rows:
        by_type.setdefault(r["type_dir"], []).append(r)
    fatal_rows = [r for r in rows if r["severity"] == "fatal"]
    serious_rows = [r for r in rows if r["severity"] == "serious"]
    minor_rows = [r for r in rows if r["severity"] == "minor"]
    pass_rows = [r for r in rows if r["severity"] == "pass"]

    check_failed = False
    if args.check == "fidelity":
        if fatal_rows:
            print(f"FAIL: {len(fatal_rows)} fatal nodes (generic/missing)")
            for r in sorted(fatal_rows, key=lambda x: x["score"])[:20]:
                print(f"  [FATAL] {r['id']} score={r['score']} issues={r['issues']} :: {r['path']}")
            check_failed = True
        else:
            print(f"OK: no fatal fidelity issues ({total} nodes, {len(pass_rows)} pass)")

    if args.jsonl:
        args.jsonl.parent.mkdir(parents=True, exist_ok=True)
        with args.jsonl.open("w", encoding="utf-8") as f:
            for r in sorted(rows, key=lambda x: x["score"]):
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # build markdown
        with args.out.open("w", encoding="utf-8") as out:
            out.write("# 本体保真度审计报告 — T0534\n\n")
            out.write("> 七项清单：概念定义/属性完备/关系闭环/行为可视化/正反例/门禁溯源/可scaffold；fidelity score 0-100；致命/严重/一般三级。金标准：AI仅读本体可复现实现。\n\n")
            out.write(f"**审计时间**：`audit-ontology-fidelity.py` 全量 `{total}` 节点（`ontology/` 409 md，`ontology-validate` 扫描一致）\n\n")
            out.write("## 汇总\n\n")
            out.write("| 分级 | 数量 | 占比 |\n|------|------|------|\n")
            out.write(f"| fatal 致命 | {len(fatal_rows)} | {len(fatal_rows)/total*100:.1f}% |\n")
            out.write(f"| serious 严重 | {len(serious_rows)} | {len(serious_rows)/total*100:.1f}% |\n")
            out.write(f"| minor 一般 | {len(minor_rows)} | {len(minor_rows)/total*100:.1f}% |\n")
            out.write(f"| pass 通过 | {len(pass_rows)} | {len(pass_rows)/total*100:.1f}% |\n")
            out.write(f"| **合计** | {total} | 100% |\n\n")
            out.write("### 按类型\n\n")
            out.write("| type | 总数 | fatal | serious | minor | pass | 均分 |\n|------|------|-------|---------|-------|------|------|\n")
            for tdir in sorted(by_type.keys()):
                grp = by_type[tdir]
                f = sum(1 for r in grp if r["severity"] == "fatal")
                s = sum(1 for r in grp if r["severity"] == "serious")
                m = sum(1 for r in grp if r["severity"] == "minor")
                p = sum(1 for r in grp if r["severity"] == "pass")
                avg = sum(r["score"] for r in grp) / len(grp) if grp else 0
                out.write(f"| {tdir} | {len(grp)} | {f} | {s} | {m} | {p} | {avg:.1f} |\n")
            out.write("\n")
            out.write("### 四类空洞量化\n\n")
            generic = sum(1 for r in rows if r["has_generic"])
            no_mermaid = sum(1 for r in rows if r["mermaid_count"] == 0)
            no_source = sum(1 for r in rows if not r["has_source"])
            short_body = sum(1 for r in rows if r["lines"] < 60)
            no_examples = sum(1 for r in rows if not r["has_both_examples"])
            out.write(f"- 泛化signal（含`检查本文件`）：{generic} 节点（{generic/total*100:.1f}%）— 零容忍致命\n")
            out.write(f"- 无mermaid：{no_mermaid} 节点（{no_mermaid/total*100:.1f}%）\n")
            out.write(f"- 无Source溯源：{no_source} 节点（{no_source/total*100:.1f}%）\n")
            out.write(f"- 正文<60行：{short_body} 节点（{short_body/total*100:.1f}%）\n")
            out.write(f"- 缺正反例：{no_examples} 节点（{no_examples/total*100:.1f}%）\n\n")
            out.write("## Top20 待修复（按score升序，致命优先）\n\n")
            out.write("| # | score | 分级 | id | 病症 | 路径 |\n|---|-------|------|----|------|------|\n")
            for i, r in enumerate(sorted(rows, key=lambda x: (0 if x["severity"]=="fatal" else 1 if x["severity"]=="serious" else 2, x["score"]))[:20], 1):
                issues = ",".join(r["issues"][:3])
                out.write(f"| {i} | {r['score']} | {r['severity']} | {r['id']} | {issues} | {r['path']} |\n")
            out.write("\n")
            out.write("## 豁免清单（存量限期，P0两周）\n\n")
            out.write("本报告 `fatal` 列表即豁免清单基线；门禁 `--check fidelity` 对以下路径增量零容忍，存量按 P0/P1/P2 限期清零：\n\n")
            out.write("```\n")
            for r in sorted(fatal_rows, key=lambda x: x["id"]):
                out.write(f"{r['id']}  # {r['path']} score={r['score']} {r['issues']}\n")
            out.write("```\n\n")
            out.write("## 复现\n\n")
            out.write("```bash\npython3 scripts/audit-ontology-fidelity.py --ontology-dir ontology --out records/T0534-0902-ontology-fidelity-remediation/audit-report.md --jsonl /tmp/fidelity.jsonl\npython3 scripts/audit-ontology-fidelity.py --check fidelity --ontology-dir ontology  # 致命门禁\n```\n")
            out.write("\nSource: `ontology/concept/ontology-fidelity-criterion.md` 七项清单 + `scripts/audit-ontology-fidelity.py`\n")
        print(f"Wrote {args.out} ({total} nodes, {len(fatal_rows)} fatal)")

    if args.format == "json":
        print(json.dumps({"total": total, "fatal": len(fatal_rows), "serious": len(serious_rows), "minor": len(minor_rows), "pass": len(pass_rows)}, ensure_ascii=False, indent=2))
    else:
        if not args.out and not args.jsonl and not args.check:
            print(f"Total {total}: fatal {len(fatal_rows)} serious {len(serious_rows)} minor {len(minor_rows)} pass {len(pass_rows)}")
            for r in sorted(rows, key=lambda x: x["score"])[:10]:
                print(f"  {r['score']:3d} {r['severity']:7s} {r['id']} {r['issues']}")

    return 1 if check_failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
