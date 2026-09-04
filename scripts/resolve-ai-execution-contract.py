#!/usr/bin/env python3
"""Resolve and verify the test-first execution contract without parsing intent."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from pdca_core import repo_root, schema_issues


CONTRACT_PATH = Path("pdca/ai-execution-contract.json")
SCENARIOS = ("development", "bugfix")
PHASE_IDS = (
    "seam",
    "red",
    "minimal-change",
    "focused-verification",
    "full-verification",
    "code-review",
)
BUGFIX_PHASE_IDS = (
    "seam",
    "red",
    "fix-approval",
    "minimal-change",
    "focused-verification",
    "full-verification",
    "code-review",
)
RECEIPT_POLICY = {
    "slice": ["focused-verification"],
    "final": ["full-verification", "code-review"],
}


class ExecutionError(Exception):
    """A stable execution-contract rejection."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def error_payload(error: ExecutionError) -> dict[str, str]:
    return {
        "schema": "pdca.ai-execution-result/v1",
        "status": "error",
        "code": error.code,
        "path": error.path,
        "message": error.message,
    }


def safe_relative_path(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ExecutionError("EXECUTION_CONTRACT_INVALID", "flow_document", "must stay inside the PDCA root") from exc
    return candidate


def load_contract(root: Path) -> dict[str, Any]:
    path = root / CONTRACT_PATH
    if not path.is_file():
        raise ExecutionError("EXECUTION_CONTRACT_MISSING", CONTRACT_PATH.as_posix(), "execution contract is required")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionError("EXECUTION_CONTRACT_INVALID", CONTRACT_PATH.as_posix(), "execution contract is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ExecutionError("EXECUTION_CONTRACT_INVALID", CONTRACT_PATH.as_posix(), "execution contract must be an object")

    issues = schema_issues(root, value, "ai-execution-contract.schema.json")
    if issues:
        issue = issues[0]
        raise ExecutionError("EXECUTION_CONTRACT_INVALID", f"{CONTRACT_PATH}{issue.path}", issue.message)

    routes = value["routes"]
    scenarios = [route["scenario"] for route in routes]
    if len(set(scenarios)) != len(scenarios) or set(scenarios) != set(SCENARIOS):
        raise ExecutionError(
            "EXECUTION_CONTRACT_INVALID",
            f"{CONTRACT_PATH}/routes",
            "routes must contain development and bugfix exactly once",
        )
    anchors = [route["route_anchor"] for route in routes]
    if len(set(anchors)) != len(anchors):
        raise ExecutionError("EXECUTION_CONTRACT_INVALID", f"{CONTRACT_PATH}/routes", "route anchors must be unique")
    for index, route in enumerate(routes):
        phase_ids = [phase["id"] for phase in route["phases"]]
        expected = list(BUGFIX_PHASE_IDS if route["scenario"] == "bugfix" else PHASE_IDS)
        if phase_ids != expected:
            raise ExecutionError(
                "EXECUTION_CONTRACT_INVALID",
                f"{CONTRACT_PATH}/routes/{index}/phases",
                "phases must use the canonical test-first order",
            )
        if route["receipt_policy"] != RECEIPT_POLICY:
            raise ExecutionError(
                "EXECUTION_CONTRACT_INVALID",
                f"{CONTRACT_PATH}/routes/{index}/receipt_policy",
                "receipt policy must preserve slice and final verification semantics",
            )
    safe_relative_path(root, value["flow_document"])
    return value


def verify_route_alignment(root: Path, contract: dict[str, Any]) -> None:
    """Use the public route resolver so route ownership stays outside this contract."""

    route_script = Path(__file__).with_name("resolve-ai-friendliness-route.py")
    for index, route in enumerate(contract["routes"]):
        completed = subprocess.run(
            [sys.executable, str(route_script), "--scenario", route["scenario"], "--root", str(root)],
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = {}
        resolved = payload.get("route")
        if completed.returncode != 0 or not isinstance(resolved, dict):
            raise ExecutionError(
                "EXECUTION_ROUTE_ALIGNMENT_FAILED",
                f"{CONTRACT_PATH}/routes/{index}",
                f"route resolver rejected {route['scenario']}: {payload.get('code', 'CLI_OUTPUT_INVALID')}",
            )
        if resolved.get("id") != route["route_id"] or resolved.get("anchor") != route["route_anchor"]:
            raise ExecutionError(
                "EXECUTION_ROUTE_ALIGNMENT_FAILED",
                f"{CONTRACT_PATH}/routes/{index}",
                "execution route does not match the public scenario route",
            )


def document_path(root: Path, contract: dict[str, Any]) -> tuple[Path, str]:
    relative = str(contract["flow_document"])
    return safe_relative_path(root, relative), relative


def route_section(lines: list[str], anchor: str, relative: str) -> list[str]:
    try:
        start = next(index for index, line in enumerate(lines) if line.startswith("## ") and line[3:].strip() == anchor)
    except StopIteration as exc:
        raise ExecutionError("EXECUTION_ANCHOR_MISSING", relative, f"route anchor is missing: {anchor}") from exc
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return lines[start:end]


def verify_document(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    path, relative = document_path(root, contract)
    if not path.is_file():
        raise ExecutionError("EXECUTION_REFERENCE_MISSING", relative, "contract flow document is missing")
    lines = path.read_text(encoding="utf-8").splitlines()
    headings = {line[3:].strip() for line in lines if line.startswith("## ")}
    contract_anchors = {route["route_anchor"] for route in contract["routes"]}
    for anchor in contract_anchors:
        if anchor not in headings:
            raise ExecutionError("EXECUTION_ANCHOR_MISSING", relative, f"route anchor is missing: {anchor}")

    documented = {
        line[3:].strip()
        for line in lines
        if line.startswith("## ") and re.fullmatch(r"路径 [AB]：.+", line[3:].strip())
    }
    if documented != contract_anchors:
        raise ExecutionError(
            "EXECUTION_ANCHOR_DRIFT",
            relative,
            "documented development and bugfix headings do not match the execution contract",
        )

    for route in contract["routes"]:
        section = "\n".join(route_section(lines, route["route_anchor"], relative))
        previous = -1
        for phase in route["phases"]:
            marker = phase["marker"]
            occurrences = section.count(marker)
            if occurrences == 0:
                raise ExecutionError(
                    "EXECUTION_MARKER_MISSING",
                    relative,
                    f"execution marker is missing: {marker}",
                )
            if occurrences != 1:
                raise ExecutionError(
                    "EXECUTION_MARKER_AMBIGUOUS",
                    relative,
                    f"execution marker must occur exactly once: {marker}",
                )
            position = section.find(marker)
            if position <= previous:
                raise ExecutionError(
                    "EXECUTION_MARKER_ORDER_DRIFT",
                    relative,
                    f"execution marker is out of order: {marker}",
                )
            previous = position
    return {
        "schema": "pdca.ai-execution-document-check/v1",
        "status": "ok",
        "path": relative,
        "route_count": len(contract["routes"]),
    }


def resolve(contract: dict[str, Any], scenario: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ExecutionError("EXECUTION_SCENARIO_INVALID", "--scenario", "scenario is not supported")
    route = next(route for route in contract["routes"] if route["scenario"] == scenario)
    return {
        "schema": "pdca.ai-execution-result/v1",
        "status": "ok",
        "scenario": scenario,
        "route": {
            "id": route["route_id"],
            "anchor": route["route_anchor"],
            "phases": route["phases"],
            "receipt_policy": route["receipt_policy"],
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
        verify_route_alignment(root, contract)
        payload = verify_document(root, contract) if args.verify_document else resolve(contract, args.scenario)
    except ExecutionError as exc:
        emit(error_payload(exc))
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        error = ExecutionError("EXECUTION_INTERNAL_ERROR", "/", "unable to resolve the execution contract")
        emit(error_payload(error))
        print(f"{error.code}: {exc}", file=sys.stderr)
        return 1
    emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
