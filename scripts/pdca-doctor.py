#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/capability-protocol（能力探针与引用诊断）；本体是源、代码是投射。
"""Diagnose repository discovery, references, dependencies, and abstract capabilities."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

import yaml

from pdca_core import identity_diagnostics, repo_root, timeline_issues

REFERENCE_RE = re.compile(r"\$PDCA_HOME/([A-Za-z0-9_./{}<>,*-]+)")


def load_seam_contracts_module():
    """用 importlib 加载同目录 check-seam-contracts.py（连字符文件名不能直接 import）。"""
    path = Path(__file__).resolve().parent / "check-seam-contracts.py"
    if not path.is_file():
        return None
    sys_path_saved = list(sys.path)
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location("check_seam_contracts", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = sys_path_saved


def seam_contracts_checks(root: Path) -> dict:
    """批量校验活跃任务 spec 的 seam 声明，返回报告段。"""
    module = load_seam_contracts_module()
    if module is None:
        return {"checked": 0, "clean": [], "issues": {}}
    specs = module.find_active_specs(root)
    issues_per_spec, clean_specs = module.check_all(specs, root)
    return {
        "checked": len(specs),
        "clean": clean_specs,
        "issues": issues_per_spec,
    }


def active_task_timeline(root: Path) -> list[dict]:
    checks: list[dict] = []
    active_root = root / "pdca/tasks/active"
    if not active_root.is_dir():
        return checks
    for task_dir in sorted(active_root.iterdir()):
        if not (task_dir / "task.json").is_file():
            continue
        issues = timeline_issues(root, task_dir)
        checks.append(
            {
                "task": task_dir.name,
                "consistent": not issues,
                "issues": [issue.as_dict() for issue in issues],
            }
        )
    return checks


def probe(root: Path, expression: str) -> bool:
    if expression == "repository-readable":
        return os.access(root, os.R_OK)
    if expression == "repository-writable":
        return os.access(root, os.W_OK)
    if expression.startswith("command:"):
        return shutil.which(expression.split(":", 1)[1]) is not None
    if expression.startswith("environment:"):
        return os.environ.get(expression.split(":", 1)[1], "").lower() in {"1", "true", "yes", "available"}
    return shutil.which(expression) is not None


def local_references(root: Path) -> list[dict]:
    sources = [root / "AGENTS.md", *sorted((root / "flows").glob("flow-*/SKILL.md"))]
    results: list[dict] = []
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for match in REFERENCE_RE.finditer(text):
            raw = match.group(1).rstrip(".,;:，。；：")
            if any(character in raw for character in "{}<>*,") or re.search(r"(YYYY|NNNN)", raw):
                continue
            target = root / raw
            results.append(
                {
                    "source": source.relative_to(root).as_posix(),
                    "reference": raw,
                    "exists": target.exists(),
                }
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = repo_root(args.root)
    fallback_used = not bool(os.environ.get("PDCA_HOME"))

    config = yaml.safe_load((root / "config/capabilities.yaml").read_text(encoding="utf-8"))
    capabilities = []
    missing_required = []
    for name, definition in config["capabilities"].items():
        available = probe(root, definition["probe"])
        if available:
            status = "available"
        elif definition.get("required"):
            status = "missing"
            missing_required.append(name)
        else:
            status = "fallback"
        capabilities.append(
            {
                "name": name,
                "status": status,
                "probe": definition["probe"],
                "fallback": definition.get("fallback"),
            }
        )

    references = local_references(root)
    missing_references = [item for item in references if not item["exists"]]
    seam_checks = seam_contracts_checks(root)
    seam_broken = bool(seam_checks["issues"])
    identity = identity_diagnostics(root)
    payload = {
        "schema": "pdca.doctor/v1",
        "root": str(root),
        "pdca_home_source": "repository-fallback" if fallback_used else "environment",
        "warning": "configure PDCA_HOME for external projects" if fallback_used else None,
        "valid": (
            not missing_required
            and not missing_references
            and not seam_broken
        ),
        "missing_required": missing_required,
        "missing_references": missing_references,
        "capabilities": capabilities,
        "references_checked": len(references),
        "task_timeline": active_task_timeline(root),
        "seam_contracts": seam_checks,
        "identity": identity,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
