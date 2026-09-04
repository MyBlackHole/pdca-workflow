#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-architecture（体系健康度聚合）；本体是源、代码是投射。
"""PDCA 体系健康度自我审查聚合器。

聚合四类信号（doctor 一致性 / identity 唯一性 / seam 契约 / 门禁覆盖率），
按三级严重度分级（阻断门禁 / 数据完整性 / 仅统计噪音）与根因分类
（机制前遗留 / 外部项目 / 真缺陷），输出 JSON + Markdown 双格式健康度报告。

只读诊断：不修改任何任务、记录或数据文件。

用法:
    python3 scripts/self-audit.py [--root ROOT] [--out OUT] [--json]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

SCHEMA_ISSUE_CODES = {"SCHEMA_INVALID", "STATE_TIME_ORDER", "CONFIRMATION_AFTER_PLAN_TO_DO", "STATE_TIMESTAMP_MISSING"}

# round 系列任务（T0248/T0252/T0253 等外部项目）
EXTERNAL_PROJECT_PATTERNS = ("round62", "round63", "round64", "round65", "round66", "round67", "round68", "round69")
# 严格 schema 冻结前的早期任务
LEGACY_PATTERNS = ("T013", "T014", "T015", "T016", "T017", "T018", "T019", "T020", "T021", "T022", "0728", "0729", "0731")


def run(cmd, root):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=root).stdout


def collect_doctor(root):
    out = run(["python3", "scripts/pdca-doctor.py", "--json"], root)
    return json.loads(out)


def collect_gate(root):
    out = run(["python3", "scripts/audit-gate-compliance.py", "--scan", "pdca/tasks", "--json"], root)
    return json.loads(out)


def task_id_from_path(path):
    parts = path.split("/")
    for part in parts:
        if part.startswith("T") and any(c.isdigit() for c in part):
            return part
    return parts[-1] if parts else "?"


def read_task_id(root, spec_path):
    """从 PRD 所在任务目录读取真实 task id。"""
    task_dir = Path(spec_path).parent
    task_json = task_dir / "task.json"
    if task_json.exists():
        try:
            data = json.loads(task_json.read_text(encoding="utf-8"))
            return data.get("id", "?")
        except (json.JSONDecodeError, OSError):
            pass
    return "?"


def classify_root_cause(task_id, slug, issues):
    """按任务命名与异常类型推断根因。"""
    if any(p in slug for p in EXTERNAL_PROJECT_PATTERNS):
        return "external-project"
    if task_id.startswith(("T01", "T02")) or any(p in slug for p in LEGACY_PATTERNS):
        return "legacy"
    return "real-defect"


def severity_of(category, is_exemption):
    """三级严重度映射：阻断门禁 / 数据完整性 / 仅统计噪音。"""
    if category in ("gate_incomplete", "id_collision"):
        return "blocking"
    if category in ("schema", "seam", "event_mismatch", "record_mismatch"):
        return "integrity"
    return "noise"


def build_report(root):
    doctor = collect_doctor(root)
    gate = collect_gate(root)

    issues = []

    # 1. doctor 一致性：schema 不一致 / 状态时序 / 确认时序
    for t in doctor["task_timeline"]:
        if t["consistent"]:
            continue
        schema_issues = [i for i in t["issues"] if i["code"] in SCHEMA_ISSUE_CODES]
        if schema_issues:
            codes = sorted({i["code"] for i in schema_issues})
            issues.append({
                "category": "schema",
                "task_id": t["task"],
                "slug": t["task"],
                "detail": "; ".join(codes),
                "count": len(schema_issues),
                "severity": "integrity",
                "root_cause": classify_root_cause(t["task"], t["task"], schema_issues),
            })

    # 2. identity：ID 撞车 / record 派生不一致 / flow-event 路径不匹配
    idn = doctor.get("identity", {})
    for group in idn.get("duplicate_task_ids", []):
        paths = group["paths"]
        issues.append({
            "category": "id_collision",
            "task_id": group["task_id"],
            "slug": " / ".join(p.split("/")[-2] for p in paths),
            "detail": f"同一 task_id 出现在 {len(paths)} 个目录",
            "count": len(paths) - 1,
            "severity": "blocking",
            "root_cause": "legacy" if group["task_id"].startswith(("T01", "T02")) else "real-defect",
        })
    for m in idn.get("record_derived_mismatches", []):
        issues.append({
            "category": "record_mismatch",
            "task_id": m.get("task_id", "?"),
            "slug": m["path"].split("/")[-2],
            "detail": f"record={m.get('record')} 期望={m.get('expected')}",
            "count": 1,
            "severity": "integrity",
            "root_cause": classify_root_cause(m.get("task_id", ""), m["path"].split("/")[-2], []),
        })
    for m in idn.get("event_path_mismatches", []):
        issues.append({
            "category": "event_mismatch",
            "task_id": m.get("payload_record_id", "?"),
            "slug": m["path"].split("/")[-2],
            "detail": f"目录 record={m.get('directory_record_id')} payload={m.get('payload_record_id')}",
            "count": 1,
            "severity": "integrity",
            "root_cause": classify_root_cause(m.get("payload_record_id", ""), m["path"].split("/")[-2], []),
        })

    # 3. seam 契约：测试接缝声明与实际不一致
    for path, errors in (doctor.get("seam_contracts") or {}).get("issues", {}).items():
        slug = path.split("/")[-2]
        task_id = read_task_id(root, path)
        issues.append({
            "category": "seam",
            "task_id": task_id,
            "slug": slug,
            "detail": "; ".join(errors[:3]),
            "count": len(errors),
            "severity": "integrity",
            "root_cause": "external-project" if any(p in slug for p in EXTERNAL_PROJECT_PATTERNS) else "real-defect",
        })

    # 4. 门禁覆盖率：gate_incomplete（非豁免）/ 豁免 / legacy 无门禁
    for item in gate["items"]:
        gate_issues = [i for i in item.get("issues", []) if i.startswith("gate_incomplete")]
        if gate_issues and not item.get("gate_exemption"):
            issues.append({
                "category": "gate_incomplete",
                "task_id": item["id"],
                "slug": item["slug"],
                "detail": "; ".join(gate_issues),
                "count": len(gate_issues),
                "severity": "blocking",
                "root_cause": classify_root_cause(item["id"], item["slug"], gate_issues),
            })
        elif item.get("gate_exemption"):
            issues.append({
                "category": "exemption",
                "task_id": item["id"],
                "slug": item["slug"],
                "detail": item.get("gate_exemption_reason", "")[:80],
                "count": 1,
                "severity": "noise",
                "root_cause": "legacy",
            })
        elif item.get("phase") in ("archive", "act") and item.get("receipt_count", 0) == 0:
            issues.append({
                "category": "legacy_no_gate",
                "task_id": item["id"],
                "slug": item["slug"],
                "detail": "机制前任务无 transition receipts",
                "count": 1,
                "severity": "noise",
                "root_cause": "legacy",
            })

    counts = Counter(i["category"] for i in issues)
    severity = Counter(i["severity"] for i in issues)
    root = Counter(i["root_cause"] for i in issues)

    return {
        "schema": "pdca.self-audit/v1",
        "generated_at": None,
        "summary": {
            "total_issues": len(issues),
            "by_category": dict(counts),
            "by_severity": dict(severity),
            "by_root_cause": dict(root),
        },
        "gate_coverage": {
            "total": gate["counts"]["total"],
            "with_receipts": gate["counts"]["with_receipts"],
            "with_verdict": gate["counts"]["with_verdict"],
            "with_convergence": gate["counts"]["with_convergence"],
            "with_final_confirmation": gate["counts"]["with_final_confirmation"],
            "rejected_receipts": gate["counts"]["rejected_receipts_total"],
            "receipts_pct": round(gate["counts"]["with_receipts"] / gate["counts"]["total"] * 100, 1) if gate["counts"]["total"] else 0,
            "verdict_pct": round(gate["counts"]["with_verdict"] / gate["counts"]["total"] * 100, 1) if gate["counts"]["total"] else 0,
        },
        "issues": issues,
        "candidates": build_candidates(issues),
    }


def build_candidates(issues):
    """从问题聚合修复候选清单（依据 + 建议范围，不执行）。"""
    cands = []
    blocking = [i for i in issues if i["severity"] == "blocking"]
    integrity = [i for i in issues if i["severity"] == "integrity"]
    if any(i["category"] == "id_collision" for i in blocking):
        n = sum(1 for i in blocking if i["category"] == "id_collision")
        cands.append({
            "title": "ID 撞车清理",
            "basis": f"{n} 组 task_id 重复（跨目录），identity 歧义影响可追溯性",
            "scope": "为每组冲突决定保留/重命名，更新依赖引用与记录",
            "priority": "high",
        })
    if any(i["category"] == "gate_incomplete" for i in blocking):
        n = sum(1 for i in blocking if i["category"] == "gate_incomplete")
        cands.append({
            "title": "真违规门禁修复",
            "basis": f"{n} 项 gate_incomplete 非豁免（缺失 verdict/final_confirmation 等）",
            "scope": "按 T0271 remediate 模式补全或如实豁免",
            "priority": "high",
        })
    if any(i["category"] == "schema" for i in integrity):
        n = sum(1 for i in integrity if i["category"] == "schema")
        cands.append({
            "title": "schema 一致性修复",
            "basis": f"{n} 项 schema/时序不一致任务",
            "scope": "区分机制前遗留与真缺陷，对齐 states/receipts 时间序",
            "priority": "medium",
        })
    if any(i["category"] == "record_mismatch" for i in integrity):
        n = sum(1 for i in integrity if i["category"] == "record_mismatch")
        cands.append({
            "title": "record 派生一致性修复",
            "basis": f"{n} 项 record 字段与派生规则不符",
            "scope": "按 identity 派生规则修正 task.json meta.record",
            "priority": "medium",
        })
    if any(i["category"] == "seam" for i in integrity):
        n = sum(1 for i in integrity if i["category"] == "seam")
        cands.append({
            "title": "seam 契约补齐",
            "basis": f"{n} 项声明的测试接缝与实际测试不一致",
            "scope": "补齐缺失测试文件或修正 seam 声明（外部项目需确认测试位置）",
            "priority": "medium",
        })
    return cands


def digest_report(report):
    canonical = json.dumps(report, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(canonical).hexdigest()


def render_markdown(report):
    lines = ["# PDCA 体系健康度自我审查报告", "", f"- 异常总数: {report['summary']['total_issues']}", ""]
    lines.append("## 汇总")
    lines.append("")
    lines.append("| 维度 | 计数 |")
    lines.append("|------|------|")
    for k, v in sorted(report["summary"]["by_category"].items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("| 严重度 | 计数 |")
    lines.append("|--------|------|")
    for k, v in sorted(report["summary"]["by_severity"].items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("| 根因 | 计数 |")
    lines.append("|------|------|")
    for k, v in sorted(report["summary"]["by_root_cause"].items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("## 门禁覆盖率")
    lines.append("")
    g = report["gate_coverage"]
    lines.append(f"- receipts {g['receipts_pct']}% ({g['with_receipts']}/{g['total']})，verdict {g['verdict_pct']}%，rejected receipts {g['rejected_receipts']} 条")
    lines.append("")
    lines.append("## 问题明细（按严重度）")
    lines.append("")
    for severity in ("blocking", "integrity", "noise"):
        group = [i for i in report["issues"] if i["severity"] == severity]
        if not group:
            continue
        label = {"blocking": "阻断门禁", "integrity": "数据完整性", "noise": "仅统计噪音"}[severity]
        lines.append(f"### {label} ({len(group)})")
        lines.append("")
        lines.append("| task_id | slug | 类别 | 根因 | 明细 |")
        lines.append("|---------|------|------|------|------|")
        for i in sorted(group, key=lambda x: x["task_id"]):
            lines.append(f"| {i['task_id']} | {i['slug']} | {i['category']} | {i['root_cause']} | {i['detail']} |")
        lines.append("")
    lines.append("## 修复候选清单（不执行，另立任务）")
    lines.append("")
    for c in report["candidates"]:
        lines.append(f"- **[{c['priority']}] {c['title']}**: {c['basis']} → 建议范围: {c['scope']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="PDCA 体系健康度自我审查")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=None, help="Markdown 报告输出路径")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON")
    args = parser.parse_args()

    report = build_report(args.root)
    report["generated_at"] = "deterministic"

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    md = render_markdown(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
        print(f"报告已写入: {args.out}")
        print(f"digest: {digest_report(report)}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
