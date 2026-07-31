#!/usr/bin/env python3
"""Resolve the machine-readable Do-path contract without parsing Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from pdca_core import repo_root, schema_issues


CONTRACT_PATH = Path("pdca/ai-friendliness-route-contract.json")
SCENARIOS = ("development", "bugfix", "research", "documentation", "design", "review")


class RouteError(Exception):
    """A stable, machine-readable route-contract rejection."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def error_payload(error: RouteError) -> dict[str, str]:
    return {
        "schema": "pdca.ai-route-result/v1",
        "status": "error",
        "code": error.code,
        "path": error.path,
        "message": error.message,
    }


def contract_file(root: Path) -> Path:
    return root / CONTRACT_PATH


def safe_relative_path(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise RouteError("ROUTE_CONTRACT_INVALID", "flow_document", "must stay inside the PDCA root") from exc
    return candidate


def load_contract(root: Path) -> dict[str, Any]:
    path = contract_file(root)
    if not path.is_file():
        raise RouteError("ROUTE_CONTRACT_MISSING", CONTRACT_PATH.as_posix(), "route contract is required")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteError("ROUTE_CONTRACT_INVALID", CONTRACT_PATH.as_posix(), "route contract is not valid JSON") from exc
    if not isinstance(value, dict):
        raise RouteError("ROUTE_CONTRACT_INVALID", CONTRACT_PATH.as_posix(), "route contract must be an object")

    issues = schema_issues(root, value, "ai-friendliness-route-contract.schema.json")
    if issues:
        issue = issues[0]
        raise RouteError("ROUTE_CONTRACT_INVALID", f"{CONTRACT_PATH}{issue.path}", issue.message)

    routes = value["routes"]
    scenarios = [route["scenario"] for route in routes]
    if len(set(scenarios)) != len(scenarios) or set(scenarios) != set(SCENARIOS):
        raise RouteError(
            "ROUTE_CONTRACT_INVALID",
            f"{CONTRACT_PATH}/routes",
            "routes must contain each supported scenario exactly once",
        )
    route_ids = [route["route_id"] for route in routes]
    if len(set(route_ids)) != len(route_ids):
        raise RouteError(
            "ROUTE_CONTRACT_INVALID",
            f"{CONTRACT_PATH}/routes",
            "route IDs must be unique",
        )
    anchors = [route["anchor"] for route in routes]
    if len(set(anchors)) != len(anchors):
        raise RouteError(
            "ROUTE_CONTRACT_INVALID",
            f"{CONTRACT_PATH}/routes",
            "route anchors must be unique",
        )
    for index, route in enumerate(routes):
        if any(not step.startswith(route["route_id"]) for step in route["steps"]):
            raise RouteError(
                "ROUTE_CONTRACT_INVALID",
                f"{CONTRACT_PATH}/routes/{index}/steps",
                "each step must use the route ID prefix",
            )
    safe_relative_path(root, value["flow_document"])
    return value


def document_path(root: Path, contract: dict[str, Any]) -> tuple[Path, str]:
    relative = str(contract["flow_document"])
    return safe_relative_path(root, relative), relative


def verify_document(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    path, relative = document_path(root, contract)
    if not path.is_file():
        raise RouteError("ROUTE_REFERENCE_MISSING", relative, "contract flow document is missing")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = {line[3:].strip() for line in lines if line.startswith("## ")}
    for route in contract["routes"]:
        if route["anchor"] not in headings:
            raise RouteError(
                "ROUTE_ANCHOR_MISSING",
                relative,
                f"route anchor is missing: {route['anchor']}",
            )

    documented_paths = {
        line[3:].strip()
        for line in lines
        if line.startswith("## ")
        if re.fullmatch(r"路径 [A-F]：.+", line[3:].strip())
    }
    contract_paths = {
        route["anchor"] for route in contract["routes"] if re.fullmatch(r"路径 [A-F]：.+", route["anchor"])
    }
    if documented_paths and documented_paths != contract_paths:
        raise RouteError(
            "ROUTE_ANCHOR_DRIFT",
            relative,
            "documented route headings do not exactly match the route contract",
        )
    return {
        "schema": "pdca.ai-route-document-check/v1",
        "status": "ok",
        "path": relative,
        "route_count": len(contract["routes"]),
    }


def resolve(contract: dict[str, Any], scenario: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise RouteError("ROUTE_SCENARIO_INVALID", "--scenario", "scenario is not supported")
    route = next(route for route in contract["routes"] if route["scenario"] == scenario)
    return {
        "schema": "pdca.ai-route-result/v1",
        "status": "ok",
        "scenario": scenario,
        "route": {
            "id": route["route_id"],
            "anchor": route["anchor"],
            "steps": route["steps"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--scenario")
    selection.add_argument("--verify-document", action="store_true")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        root = repo_root(args.root)
        contract = load_contract(root)
        payload = verify_document(root, contract) if args.verify_document else resolve(contract, args.scenario)
    except RouteError as exc:
        emit(error_payload(exc))
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        error = RouteError("ROUTE_INTERNAL_ERROR", "/", "unable to resolve the route contract")
        emit(error_payload(error))
        print(f"{error.code}: {exc}", file=sys.stderr)
        return 1
    emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
