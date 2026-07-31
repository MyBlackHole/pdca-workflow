#!/usr/bin/env python3
"""Diagnose repository discovery, references, dependencies, and abstract capabilities."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path

import yaml

from pdca_core import repo_root

REFERENCE_RE = re.compile(r"\$PDCA_HOME/([A-Za-z0-9_./{}<>,*-]+)")


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
    payload = {
        "schema": "pdca.doctor/v1",
        "root": str(root),
        "pdca_home_source": "repository-fallback" if fallback_used else "environment",
        "warning": "configure PDCA_HOME for external projects" if fallback_used else None,
        "valid": not missing_required and not missing_references,
        "missing_required": missing_required,
        "missing_references": missing_references,
        "capabilities": capabilities,
        "references_checked": len(references),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
