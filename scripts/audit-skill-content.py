#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/knowledge-artifact（flow/skill 内容度量）；本体是源、代码是投射。
"""Measure reproducible, dependency-light flow/skill content metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pdca_core import repo_root, schema_issues

REFERENCE_RE = re.compile(r"\$PDCA_HOME/([A-Za-z0-9_./*-]+)")
HEADING_RE = re.compile(r"^(#+)\s+", re.MULTILINE)


def normalize_lines(text: str) -> set[str]:
    values = set()
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw.strip().lower())
        line = re.sub(r"`[^`]+`", "`<code>`", line)
        if len(line) >= 24 and not line.startswith(("#", "---", "|---")):
            values.add(line)
    return values


def asset_paths(root: Path) -> list[Path]:
    return sorted([*(root / "flows").glob("flow-*/SKILL.md"), *(root / "skills").glob("**/SKILL.md")])


def pareto_frontier(metrics: list[dict], cost_field: str) -> list[str]:
    frontier = []
    for candidate in metrics:
        dominated = any(
            other[cost_field] >= candidate[cost_field]
            and other["cross_asset_duplicate_ratio"] >= candidate["cross_asset_duplicate_ratio"]
            and (
                other[cost_field] > candidate[cost_field]
                or other["cross_asset_duplicate_ratio"] > candidate["cross_asset_duplicate_ratio"]
            )
            for other in metrics
            if other is not candidate
        )
        if not dominated:
            frontier.append(candidate["file"])
    return sorted(frontier)


def measure(root: Path) -> dict:
    paths = asset_paths(root)
    texts = {path: path.read_text(encoding="utf-8") for path in paths}
    line_sets = {path: normalize_lines(text) for path, text in texts.items()}
    owners: dict[str, set[Path]] = defaultdict(set)
    for path, lines in line_sets.items():
        for line in lines:
            owners[line].add(path)

    metrics = []
    for path in paths:
        text = texts[path]
        data = text.encode("utf-8")
        lines = line_sets[path]
        duplicate_lines = {line for line in lines if len(owners[line]) > 1}
        references = sorted(set(REFERENCE_RE.findall(text)))
        broken = [
            reference
            for reference in references
            if not re.search(r"(YYYY|NNNN|[*])", reference) and not (root / reference).exists()
        ]
        headings = HEADING_RE.findall(text)
        metrics.append(
            {
                "file": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "line_count": len(text.splitlines()),
                "heading_count": len(headings),
                "max_heading_depth": max((len(value) for value in headings), default=0),
                "normalized_content_lines": len(lines),
                "cross_asset_duplicate_lines": len(duplicate_lines),
                "cross_asset_duplicate_ratio": round(len(duplicate_lines) / max(len(lines), 1), 4),
                "reference_count": len(references),
                "broken_references": broken,
            }
        )
    metrics.sort(key=lambda item: item["file"])
    cost_field = "bytes"
    return {
        "schema": "pdca.skill-content/v1",
        "cost_metric": cost_field,
        "asset_count": len(metrics),
        "totals": {
            "bytes": sum(item["bytes"] for item in metrics),
            "broken_references": sum(len(item["broken_references"]) for item in metrics),
        },
        "pareto_candidates": pareto_frontier(metrics, cost_field),
        "assets": metrics,
    }


def budget_issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def command_payload(command: list[str]) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(command, capture_output=True, text=True)
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError:
        value = {}
    return completed.returncode, value if isinstance(value, dict) else {}


def deterministic_contract_issues(root: Path) -> list[dict[str, str]]:
    """Require contract/document and fixture checks when the corresponding assets exist."""

    issues: list[dict[str, str]] = []
    script_dir = Path(__file__).resolve().parent
    contracts = (
        (
            "pdca/ai-friendliness-route-contract.json",
            "resolve-ai-friendliness-route.py",
            "--verify-document",
            "CONTENT_ROUTE_CONTRACT_FAILED",
            "route document verification",
        ),
        (
            "pdca/ai-execution-contract.json",
            "resolve-ai-execution-contract.py",
            "--verify-document",
            "CONTENT_EXECUTION_CONTRACT_FAILED",
            "execution document verification",
        ),
        (
            "pdca/skill-invocation-contract.json",
            "resolve-skill-invocation.py",
            "--verify-documents",
            "CONTENT_INVOCATION_CONTRACT_FAILED",
            "invocation document verification",
        ),
    )
    for contract_relative, script_name, argument, issue_code, label in contracts:
        contract = root / contract_relative
        if not contract.is_file():
            continue
        status, payload = command_payload(
            [sys.executable, str(script_dir / script_name), argument, "--root", str(root)]
        )
        if status != 0:
            issues.append(
                budget_issue(
                    issue_code,
                    contract.relative_to(root).as_posix(),
                    f"{label} failed: {payload.get('code', 'CLI_OUTPUT_INVALID')}",
                )
            )
    fixture = root / "tests/fixtures/ai-friendliness-scenarios.json"
    if fixture.is_file():
        status, payload = command_payload(
            [sys.executable, str(script_dir / "run-ai-friendliness-fixtures.py"), "--all", "--root", str(root)]
        )
        if status != 0:
            issues.append(
                budget_issue(
                    "CONTENT_FIXTURE_FAILED",
                    fixture.relative_to(root).as_posix(),
                    f"deterministic fixture failed: {payload.get('failed', 'CLI_OUTPUT_INVALID')}",
                )
            )
    return issues


def content_budget(root: Path, payload: dict) -> dict:
    baseline_path = root / "pdca/skill-content-baseline.json"
    issues: list[dict[str, str]] = []
    current = {asset["file"]: asset for asset in payload["assets"]}
    comparisons: list[dict[str, Any]] = []
    if not baseline_path.is_file():
        issues.append(
            budget_issue(
                "CONTENT_BASELINE_MISSING",
                baseline_path.relative_to(root).as_posix(),
                "versioned content baseline is required",
            )
        )
        return {
            "status": "rejected",
            "baseline": baseline_path.relative_to(root).as_posix(),
            "issues": issues,
            "assets": comparisons,
        }
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        issues.append(
            budget_issue(
                "CONTENT_BASELINE_INVALID",
                baseline_path.relative_to(root).as_posix(),
                "baseline must be valid JSON",
            )
        )
        return {
            "status": "rejected",
            "baseline": baseline_path.relative_to(root).as_posix(),
            "issues": issues,
            "assets": comparisons,
        }

    schema_errors = schema_issues(root, baseline, "skill-content-baseline.schema.json")
    if schema_errors:
        issues.extend(
            budget_issue(
                "CONTENT_BASELINE_INVALID",
                f"{baseline_path.relative_to(root).as_posix()}{error.path}",
                error.message,
            )
            for error in schema_errors
        )
        return {
            "status": "rejected",
            "baseline": baseline_path.relative_to(root).as_posix(),
            "issues": issues,
            "assets": comparisons,
        }

    baseline_assets = baseline["assets"]
    filenames = [entry["file"] for entry in baseline_assets]
    duplicates = sorted({filename for filename in filenames if filenames.count(filename) > 1})
    if duplicates:
        issues.extend(
            budget_issue(
                "CONTENT_BASELINE_INVALID",
                baseline_path.relative_to(root).as_posix(),
                f"baseline repeats asset: {filename}",
            )
            for filename in duplicates
        )
    baseline_by_file = {entry["file"]: entry for entry in baseline_assets}

    for filename in sorted(set(current) - set(baseline_by_file)):
        issues.append(
            budget_issue(
                "CONTENT_BASELINE_ASSET_MISSING",
                filename,
                "current audited asset is not present in the baseline",
            )
        )
    for filename in sorted(set(baseline_by_file) - set(current)):
        issues.append(
            budget_issue(
                "CONTENT_BASELINE_ASSET_STALE",
                filename,
                "baseline asset is no longer in the audited scope",
            )
        )
    for filename in sorted(set(current) & set(baseline_by_file)):
        actual = current[filename]["bytes"]
        allowed = baseline_by_file[filename]["bytes"]
        comparisons.append(
            {
                "file": filename,
                "baseline_bytes": allowed,
                "current_bytes": actual,
                "delta_bytes": actual - allowed,
                "reason": baseline_by_file[filename]["reason"],
            }
        )
        if actual > allowed:
            issues.append(
                budget_issue(
                    "CONTENT_BUDGET_EXCEEDED",
                    filename,
                    f"current bytes {actual} exceed baseline {allowed}; update the versioned baseline with a reason",
                )
            )

    for asset in payload["assets"]:
        for reference in asset["broken_references"]:
            issues.append(
                budget_issue(
                    "CONTENT_REFERENCE_BROKEN",
                    asset["file"],
                    f"broken PDCA_HOME reference: {reference}",
                )
            )
    issues.extend(deterministic_contract_issues(root))
    return {
        "status": "passed" if not issues else "rejected",
        "baseline": baseline_path.relative_to(root).as_posix(),
        "issues": sorted(issues, key=lambda item: (item["code"], item["path"], item["message"])),
        "assets": comparisons,
    }


def markdown(payload: dict) -> str:
    cost_field = payload["cost_metric"]
    assets = sorted(payload["assets"], key=lambda item: item[cost_field], reverse=True)
    lines = [
        "# Skill 内容量自动审查",
        "",
        f"- 资产数：{payload['asset_count']}",
        "- 成本口径：UTF-8 bytes（零模型依赖，可跨环境复现）",
        f"- 断链：{payload['totals']['broken_references']}",
        "",
        "| 文件 | bytes | 重复率 | 标题 | 引用/断链 |",
        "|------|------:|-------:|-----:|----------:|",
    ]
    for asset in assets:
        lines.append(
            f"| `{asset['file']}` | {asset['bytes']} | {asset['cross_asset_duplicate_ratio']:.1%} | "
            f"{asset['heading_count']} | {asset['reference_count']}/{len(asset['broken_references'])} |"
        )
    lines.extend(["", "## Pareto 高成本候选", ""])
    lines.extend(f"- `{path}`" for path in payload["pareto_candidates"])
    if "budget" in payload:
        budget = payload["budget"]
        lines.extend(["", "## 内容预算", "", f"- 状态：{budget['status']}"])
        lines.extend(f"- `{issue['code']}`：{issue['path']}" for issue in budget["issues"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--check-budget", action="store_true")
    args = parser.parse_args()
    root = repo_root(args.root)
    payload = measure(root)
    if args.check_budget:
        payload["budget"] = content_budget(root, payload)
    json_text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    markdown_text = markdown(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json_text, encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown_text, encoding="utf-8")
    print(json_text if args.format == "json" else markdown_text, end="")
    return 0 if not args.check_budget or payload["budget"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
