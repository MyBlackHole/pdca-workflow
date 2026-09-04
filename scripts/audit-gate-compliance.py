#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-architecture（门禁合规审计）；本体是源、代码是投射。
"""PDCA 门禁合规审计器（T0270，第六轮）。

扫描全量任务（archive/active/根目录），采集门禁要素覆盖：
  - transition-receipts 成功 receipt 数量
  - meta.verdict 是否存在
  - meta.convergence 是否非空
  - clarifications.jsonl 是否含 final_confirmation
  - id 唯一性（撞车检测）
  - 归档一致性（重复归档 / 嵌套 / active 残留 / 源未移）
  - rejected receipts 计数（transition 拒绝留痕，gate-rejection）

异常分类：
  - legacy_no_gate   0 个成功 receipt（未纳入 transition 门禁，仅报告不判违规）
  - gate_incomplete  有 receipts 但 phase=check/act/archive 且缺 verdict 或缺 final_confirmation（真违规候选）
  - id_collision     id 被多个任务复用
  - archive_dup      同一 slug 在 archive 出现多次（嵌套/重复）
  - active_stale     同一 slug 同时存在于 active 与 archive

用法：
  audit-gate-compliance.py --scan <tasks-root>            # 输出合规报告
  audit-gate-compliance.py --scan <tasks-root> --out <p>  # 报告写入文件
  audit-gate-compliance.py --scan <tasks-root> --json     # JSON 输出
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def load_json_checked(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def find_task_jsons(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("task.json") if p.is_file())


def load_clarifications_sources(task_dir: Path) -> set[str]:
    path = task_dir / "clarifications.jsonl"
    if not path.is_file():
        return set()
    sources: set[str] = set()
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get("source"):
                sources.add(obj["source"])
    except OSError:
        pass
    return sources


def scan_task(root: Path, task_path: Path) -> dict:
    task_dir = task_path.parent
    task = load_json_checked(task_path) or {}
    tid = task.get("id") or "?"
    phase = (task.get("meta") or {}).get("phase") or "?"
    verdict = bool((task.get("meta") or {}).get("verdict"))
    exemption = (task.get("meta") or {}).get("gate_exemption") or {}
    convergence = (task.get("meta") or {}).get("convergence") or []
    receipts_dir = task_dir / "transition-receipts"
    receipts = sorted(receipts_dir.glob("*-to-*.json")) if receipts_dir.is_dir() else []
    receipt_names = {r.stem for r in receipts}
    rejected = sorted(receipts_dir.glob("rejected-*.json")) if receipts_dir.is_dir() else []
    sources = load_clarifications_sources(task_dir)
    rel = task_path.relative_to(root)
    return {
        "id": tid,
        "path": str(rel),
        "slug": rel.parent.name,
        "phase": phase,
        "receipts": [r.name for r in receipts],
        "receipt_count": len(receipts),
        "rejected_count": len(rejected),
        "verdict": verdict,
        "gate_exemption": bool(exemption),
        "gate_exemption_reason": str(exemption.get("reason", "")) if exemption else "",
        "convergence_count": len(convergence),
        "final_confirmation": "final_confirmation" in sources,
        "has_plan_to_do": "plan-to-do" in receipt_names,
        "has_do_to_check": "do-to-check" in receipt_names,
        "has_check_to_act": "check-to-act" in receipt_names,
        "has_act_to_archive": "act-to-archive" in receipt_names,
    }


def classify(item: dict) -> list[str]:
    issues: list[str] = []
    if item["gate_exemption"]:
        return issues
    if item["receipt_count"] == 0:
        issues.append("legacy_no_gate")
    else:
        # check 阶段进行中本就无 verdict（check→act 前才要求），仅 act/archive 判违规
        if item["phase"] in {"act", "archive"}:
            if not item["verdict"]:
                issues.append("gate_incomplete:no-verdict")
            if not item["final_confirmation"]:
                issues.append("gate_incomplete:no-final-confirmation")
        if item["phase"] == "archive" and not item["has_act_to_archive"]:
            issues.append("gate_incomplete:no-act-to-archive")
    return issues


def scan_all(root: Path) -> dict:
    task_paths = find_task_jsons(root)
    items = [scan_task(root, p) for p in task_paths]
    for item in items:
        item["issues"] = []

    id_map: dict[str, list[str]] = defaultdict(list)
    slug_map: dict[str, list[str]] = defaultdict(list)
    for item in items:
        id_map[item["id"]].append(item["path"])
        slug_map[item["slug"]].append(item["path"])

    collided_ids = {k: v for k, v in id_map.items() if len(v) > 1}
    for item in items:
        if item["id"] in collided_ids:
            item["issues"].append("id_collision")
        for issue in classify(item):
            if issue not in item["issues"]:
                item["issues"].append(issue)

    archive_dup: dict[str, list[str]] = {}
    active_stale: dict[str, list[str]] = {}
    is_archive = lambda p: p.startswith("archive/") or "/archive/" in p
    is_active = lambda p: p.startswith("active/") or "/active/" in p
    for slug, paths in slug_map.items():
        archive_hits = [p for p in paths if is_archive(p)]
        active_hits = [p for p in paths if is_active(p)]
        if len(archive_hits) > 1:
            archive_dup[slug] = archive_hits
        if active_hits and archive_hits:
            active_stale[slug] = active_hits + archive_hits

    counts = {
        "total": len(items),
        "with_receipts": sum(1 for i in items if i["receipt_count"] > 0),
        "with_verdict": sum(1 for i in items if i["verdict"]),
        "with_convergence": sum(1 for i in items if i["convergence_count"] > 0),
        "with_final_confirmation": sum(1 for i in items if i["final_confirmation"]),
        "rejected_receipts_total": sum(i["rejected_count"] for i in items),
        "id_collision_groups": len(collided_ids),
        "archive_dup_groups": len(archive_dup),
        "active_stale_groups": len(active_stale),
    }

    phase_dist: dict[str, int] = defaultdict(int)
    for i in items:
        phase_dist[i["phase"]] += 1

    return {
        "counts": counts,
        "phase_distribution": dict(phase_dist),
        "items": items,
        "collided_ids": collided_ids,
        "archive_dup": archive_dup,
        "active_stale": active_stale,
    }


def render_report(result: dict) -> str:
    c = result["counts"]
    total = c["total"] or 1
    pct = lambda n: f"{round(n / total * 100, 1)}%"
    lines = [
        "# PDCA 门禁合规审计（T0270，第六轮）",
        "",
        f"扫描根: `pdca/tasks` | 任务数: {c['total']}",
        "",
        "## 覆盖率",
        "",
        "| 要素 | 覆盖数 | 覆盖率 |",
        "|---|---:|---:|",
        f"| transition receipts（成功） | {c['with_receipts']} | {pct(c['with_receipts'])} |",
        f"| verdict | {c['with_verdict']} | {pct(c['with_verdict'])} |",
        f"| convergence 非空 | {c['with_convergence']} | {pct(c['with_convergence'])} |",
        f"| final_confirmation | {c['with_final_confirmation']} | {pct(c['with_final_confirmation'])} |",
        f"| rejected receipts（拒收留痕） | {c['rejected_receipts_total']} | - |",
        "",
        "## 阶段分布",
        "",
        "| 阶段 | 任务数 |",
        "|---|---:|",
    ]
    for phase in sorted(result["phase_distribution"]):
        lines.append(f"| {phase} | {result['phase_distribution'][phase]} |")

    lines += [
        "",
        "## 异常清单",
        "",
        "### id 撞车",
        "",
        f"组数: {c['id_collision_groups']}",
        "",
    ]
    for tid, paths in sorted(result["collided_ids"].items()):
        lines.append(f"- `{tid}`: " + "; ".join(paths))
    if not result["collided_ids"]:
        lines.append("- 无")

    lines += [
        "",
        "### 归档不一致（重复归档 / active 残留）",
        "",
        f"重复归档组数: {c['archive_dup_groups']} | active 残留组数: {c['active_stale_groups']}",
        "",
    ]
    for slug, paths in sorted(result["archive_dup"].items()):
        lines.append(f"- `{slug}` 重复归档: " + "; ".join(paths))
    for slug, paths in sorted(result["active_stale"].items()):
        lines.append(f"- `{slug}` active 残留: " + "; ".join(paths))
    if not result["archive_dup"] and not result["active_stale"]:
        lines.append("- 无")

    lines += [
        "",
        "### 豁免清单（meta.gate_exemption）",
        "",
    ]
    exempted = [i for i in result["items"] if i["gate_exemption"]]
    for i in sorted(exempted, key=lambda x: x["id"]):
        lines.append(f"- `{i['id']}` (`{i['phase']}`): {i['gate_exemption_reason']}")
    if not exempted:
        lines.append("- 无")

    lines += [
        "",
        "### 门禁要素异常（按任务）",
        "",
        "| id | phase | receipts | verdict | final_conf | issues |",
        "|---|---|---:|---|---|---|",
    ]
    for i in sorted(result["items"], key=lambda x: x["id"]):
        issues = [x for x in i["issues"]]
        if not issues:
            continue
        lines.append(
            f"| {i['id']} | {i['phase']} | {i['receipt_count']} | "
            f"{'Y' if i['verdict'] else 'N'} | {'Y' if i['final_confirmation'] else 'N'} | "
            f"{'; '.join(issues)} |"
        )
    lines += ["", "## 结论", ""]
    gate_incomplete = sum(1 for i in result["items"] if any(x.startswith("gate_incomplete") for x in i["issues"]))
    legacy = sum(1 for i in result["items"] if "legacy_no_gate" in i["issues"])
    lines.append(
        f"- 真违规候选（gate_incomplete）: {gate_incomplete} 个；机制前任务（legacy_no_gate）: {legacy} 个。"
    )
    lines.append(
        f"- 门禁拦截留痕（rejected receipts）: {c['rejected_receipts_total']} 次（transition 拒绝现可计数可审计）。"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="PDCA 门禁合规审计器")
    parser.add_argument("--scan", help="扫描根目录（含 archive/active/根）")
    parser.add_argument("--out", help="报告输出文件")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if args.scan:
        root = Path(args.scan)
        if not root.is_dir():
            print(f"目录不存在: {root}", file=sys.stderr)
            return 1
        result = scan_all(root)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        report = render_report(result)
        if args.out:
            Path(args.out).write_text(report, encoding="utf-8")
            print(f"报告已写入: {args.out}")
        else:
            sys.stdout.write(report)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
