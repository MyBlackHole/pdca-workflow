#!/usr/bin/env python3
"""Run deterministic AI-friendliness fixtures through public PDCA interfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from pdca_core import repo_root


SCRIPT_DIR = Path(__file__).resolve().parent
ROUTE_RESOLVER = SCRIPT_DIR / "resolve-ai-friendliness-route.py"
EXECUTION_RESOLVER = SCRIPT_DIR / "resolve-ai-execution-contract.py"
INVOCATION_RESOLVER = SCRIPT_DIR / "resolve-skill-invocation.py"
TRANSITION = SCRIPT_DIR / "transition-phase.py"
FIXED_TIME = "2026-07-30T10:00:00+08:00"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_payload(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "code": "FIXTURE_CLI_OUTPUT_INVALID"}
    return value if isinstance(value, dict) else {"status": "error", "code": "FIXTURE_CLI_OUTPUT_INVALID"}


def run_public(script: Path, arguments: list[str], root: Path) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, str(script), *arguments, "--root", str(root)],
        cwd=SCRIPT_DIR.parent,
        capture_output=True,
        text=True,
    )
    return completed.returncode, load_payload(completed)


def fixture_root(source_root: Path, temporary: str) -> tuple[Path, Path]:
    """Build the smallest strict repository needed by the public transition CLI."""

    root = Path(temporary)
    plan = root / "ontology/process/flow-plan.md"
    plan.parent.mkdir(parents=True)
    shutil.copy2(source_root / "ontology/process/flow-plan.md", plan)
    shutil.copytree(source_root / "schemas", root / "schemas")
    (root / "records").mkdir()
    task_dir = root / "pdca/tasks/active/0730-ai-fixture"
    task_dir.mkdir(parents=True)
    return root, task_dir


def route_fixture_root(source_root: Path, temporary: str) -> Path:
    root, _ = fixture_root(source_root, temporary)
    contract_source = source_root / "pdca/ai-friendliness-route-contract.json"
    contract_target = root / "pdca/ai-friendliness-route-contract.json"
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(contract_source, contract_target)
    contract = json.loads(contract_target.read_text(encoding="utf-8"))
    flow_document = str(contract["flow_document"])
    target_document = (root / flow_document).resolve()
    source_document = (source_root / flow_document).resolve()
    try:
        target_document.relative_to(root.resolve())
        source_document.relative_to(source_root.resolve())
    except ValueError as exc:
        raise ValueError("route fixture document must stay inside its controlled root") from exc
    target_document.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_document, target_document)
    return root


def execution_fixture_root(source_root: Path, temporary: str) -> Path:
    root, _ = fixture_root(source_root, temporary)
    route_contract_target = root / "pdca/ai-friendliness-route-contract.json"
    route_contract_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_root / "pdca/ai-friendliness-route-contract.json", route_contract_target)
    contract_source = source_root / "pdca/ai-execution-contract.json"
    contract_target = root / "pdca/ai-execution-contract.json"
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(contract_source, contract_target)
    contract = json.loads(contract_target.read_text(encoding="utf-8"))
    flow_document = str(contract["flow_document"])
    target_document = (root / flow_document).resolve()
    source_document = (source_root / flow_document).resolve()
    try:
        target_document.relative_to(root.resolve())
        source_document.relative_to(source_root.resolve())
    except ValueError as exc:
        raise ValueError("execution fixture document must stay inside its controlled root") from exc
    target_document.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_document, target_document)
    return root


def invocation_fixture_root(source_root: Path, temporary: str) -> Path:
    root = Path(temporary)
    shutil.copytree(source_root / "flows", root / "flows")
    shutil.copytree(source_root / "skills", root / "skills")
    shutil.copytree(source_root / "schemas", root / "schemas")
    contract_target = root / "pdca/skill-invocation-contract.json"
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_root / "pdca/skill-invocation-contract.json", contract_target)
    return root


def route_observation(source_root: Path, scenario: str) -> str:
    _, payload = run_public(ROUTE_RESOLVER, ["--scenario", scenario], source_root)
    route = payload.get("route")
    if payload.get("status") == "ok" and isinstance(route, dict) and isinstance(route.get("id"), str):
        return route["id"]
    return str(payload.get("code", "FIXTURE_ROUTE_RESULT_INVALID"))


def reference_observation(source_root: Path) -> str:
    """Break the actual contract reference, then run the public document check."""

    try:
        with tempfile.TemporaryDirectory() as temporary:
            root = route_fixture_root(source_root, temporary)
            contract = json.loads((root / "pdca/ai-friendliness-route-contract.json").read_text(encoding="utf-8"))
            target = (root / str(contract["flow_document"])).resolve()
            target.relative_to(root.resolve())
            target.unlink()
            _, payload = run_public(ROUTE_RESOLVER, ["--verify-document"], root)
            return str(payload.get("code", "FIXTURE_REFERENCE_RESULT_INVALID"))
    except (KeyError, OSError, TypeError, ValueError):
        return "FIXTURE_ROUTE_CONTEXT_INVALID"


def execution_observation(source_root: Path, scenario: str) -> str:
    _, payload = run_public(EXECUTION_RESOLVER, ["--scenario", scenario], source_root)
    route = payload.get("route")
    if payload.get("status") == "ok" and isinstance(route, dict) and isinstance(route.get("id"), str):
        return route["id"]
    return str(payload.get("code", "FIXTURE_EXECUTION_RESULT_INVALID"))


def execution_marker_order_observation(source_root: Path) -> str:
    try:
        with tempfile.TemporaryDirectory() as temporary:
            root = execution_fixture_root(source_root, temporary)
            contract = json.loads((root / "pdca/ai-execution-contract.json").read_text(encoding="utf-8"))
            development = next(route for route in contract["routes"] if route["scenario"] == "development")
            first = development["phases"][0]["marker"]
            second = development["phases"][1]["marker"]
            flow = root / str(contract["flow_document"])
            text = flow.read_text(encoding="utf-8")
            first_index = text.find(first)
            second_index = text.find(second)
            if first_index < 0 or second_index < 0 or first_index >= second_index:
                return "FIXTURE_EXECUTION_MARKERS_NOT_FOUND"
            swapped = (
                text[:first_index]
                + second
                + text[first_index + len(first) : second_index]
                + first
                + text[second_index + len(second) :]
            )
            flow.write_text(swapped, encoding="utf-8")
            _, payload = run_public(EXECUTION_RESOLVER, ["--verify-document"], root)
            return str(payload.get("code", "FIXTURE_EXECUTION_ORDER_RESULT_INVALID"))
    except (KeyError, OSError, StopIteration, TypeError, ValueError):
        return "FIXTURE_EXECUTION_CONTEXT_INVALID"


def invocation_alias_observation(source_root: Path) -> str:
    _, payload = run_public(INVOCATION_RESOLVER, ["--alias", "grill"], source_root)
    if payload.get("status") == "ok" and isinstance(payload.get("target"), str):
        return payload["target"]
    return str(payload.get("code", "FIXTURE_INVOCATION_ALIAS_RESULT_INVALID"))


def invocation_manual_edge_observation(source_root: Path) -> str:
    try:
        with tempfile.TemporaryDirectory() as temporary:
            root = invocation_fixture_root(source_root, temporary)
            contract_path = root / "pdca/skill-invocation-contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            edge = next(
                item
                for item in contract["edges"]
                if item["from"] == "flow-plan" and item["to"] == "triage-work"
            )
            edge["to"] = "triage"
            write_json(contract_path, contract)
            _, payload = run_public(INVOCATION_RESOLVER, ["--verify-documents"], root)
            return str(payload.get("code", "FIXTURE_INVOCATION_EDGE_RESULT_INVALID"))
    except (KeyError, OSError, StopIteration, TypeError, ValueError):
        return "FIXTURE_INVOCATION_CONTEXT_INVALID"


def invocation_stale_alias_observation(source_root: Path) -> str:
    try:
        with tempfile.TemporaryDirectory() as temporary:
            root = invocation_fixture_root(source_root, temporary)
            entry = root / "skills/ask-matt/SKILL.md"
            text = entry.read_text(encoding="utf-8")
            if "`/grill`" not in text:
                return "FIXTURE_INVOCATION_ALIAS_NOT_FOUND"
            entry.write_text(text.replace("`/grill`", "`/grill-me`", 1), encoding="utf-8")
            _, payload = run_public(INVOCATION_RESOLVER, ["--verify-documents"], root)
            return str(payload.get("code", "FIXTURE_INVOCATION_ALIAS_RESULT_INVALID"))
    except (OSError, TypeError, ValueError):
        return "FIXTURE_INVOCATION_CONTEXT_INVALID"


def initial_task() -> dict[str, Any]:
    return {
        "id": "T9900",
        "slug": "0730-ai-fixture",
        "title": "AI friendliness lifecycle fixture",
        "parent": None,
        "children": [],
        "status": "Pending",
        "meta": {
            "phase": "plan",
            "active": True,
            "scenario_type": "development",
            "created_at": FIXED_TIME,
            "convergence": ["fixture lifecycle converges"],
            "record": "R9900",
        },
        "states": {
            "created": FIXED_TIME,
            "plan": FIXED_TIME,
            "do": None,
            "check": None,
            "act": None,
            "archive": None,
        },
    }


def prepare_task(source_root: Path, temporary: str, confirmed: bool) -> tuple[Path, Path]:
    root, task_dir = fixture_root(source_root, temporary)
    write_json(task_dir / "task.json", initial_task())
    (task_dir / "prd.md").write_text("# fixture\n\n## 验收标准\n- [ ] lifecycle works\n", encoding="utf-8")
    entries: list[dict[str, str]] = []
    if confirmed:
        entries.append(
            {
                "source": "final_confirmation",
                "summary": "fixture approved",
                "response": "confirmed",
                "at": "2026-07-30T10:00:01+08:00",
            }
        )
    (task_dir / "clarifications.jsonl").write_text(
        "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries), encoding="utf-8"
    )
    return root, task_dir


def transition(root: Path, task_dir: Path, target: str) -> tuple[int, dict[str, Any]]:
    return run_public(TRANSITION, [str(task_dir), "--to", target], root)


def rejected_observation(payload: dict[str, Any], expected: str) -> str:
    issues = payload.get("issues")
    codes = sorted(
        item["code"]
        for item in issues
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    ) if isinstance(issues, list) else []
    return expected if expected in codes else ",".join(codes) or str(payload.get("status", "FIXTURE_TRANSITION_INVALID"))


def update_task(task_dir: Path, update: Callable[[dict[str, Any]], None]) -> None:
    path = task_dir / "task.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    update(value)
    write_json(path, value)


def evidence_entry(identifier: str, file: Path, kind: str) -> dict[str, Any]:
    data = file.read_bytes()
    return {
        "id": identifier,
        "file": file.name,
        "kind": kind,
        "size": len(data),
        "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
        "at": "2026-07-30T10:00:02+08:00",
        "criteria": ["AC-1"],
    }


def add_evidence(root: Path, include_convergence: bool = True) -> None:
    evidence_dir = root / "records/R9900/evidence"
    evidence_dir.mkdir(parents=True)
    result = evidence_dir / "result.txt"
    result.write_text("fixture passed\n", encoding="utf-8")
    entries = [evidence_entry("result", result, "test")]
    if include_convergence:
        mapping = evidence_dir / "convergence.json"
        write_json(
            mapping,
            {
                "schema": "pdca.convergence/v1",
                "items": [
                    {
                        "index": 1,
                        "text": "fixture lifecycle converges",
                        "criteria": ["AC-1"],
                        "evidence_ids": ["result"],
                    }
                ],
            },
        )
        entries.append(evidence_entry("convergence-map", mapping, "convergence-map"))
    (evidence_dir / "manifest.jsonl").write_text(
        "".join(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n" for entry in entries),
        encoding="utf-8",
    )


def add_check_requirements(
    root: Path,
    task_dir: Path,
    include_confirmation: bool,
    include_conclusion: bool = True,
    include_verdict: bool = True,
) -> None:
    if include_conclusion:
        (root / "records/R9900/conclusion.md").write_text("# fixture conclusion\n", encoding="utf-8")

    def add_verdict(value: dict[str, Any]) -> None:
        value["meta"]["verdict"] = {
            "outcome": "confirmed",
            "reason": "fixture passed",
            "verdict_id": "V9900",
            "at": "2026-07-30T10:00:03+08:00",
        }

    if include_verdict:
        update_task(task_dir, add_verdict)
    if include_confirmation:
        with (task_dir / "clarifications.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "source": "check_confirmation",
                        "summary": "fixture accepted",
                        "response": "confirmed",
                        "at": "2026-07-30T10:00:04+08:00",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def add_disposition(task_dir: Path) -> None:
    def update(value: dict[str, Any]) -> None:
        value["meta"]["disposition"] = {
            "outcome": "task_only",
            "reason": "fixture has no reusable knowledge",
            "at": "2026-07-30T10:00:05+08:00",
        }

    update_task(task_dir, update)


def lifecycle_success(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        add_evidence(root)
        if transition(root, task_dir, "check")[0] != 0:
            return "DO_TO_CHECK_FAILED"
        add_check_requirements(root, task_dir, include_confirmation=True)
        if transition(root, task_dir, "act")[0] != 0:
            return "CHECK_TO_ACT_FAILED"
        add_disposition(task_dir)
        if transition(root, task_dir, "archive")[0] != 0:
            return "ACT_TO_ARCHIVE_FAILED"
        receipts = [
            task_dir / "transition-receipts/plan-to-do.json",
            task_dir / "transition-receipts/do-to-check.json",
            task_dir / "transition-receipts/check-to-act.json",
            task_dir / "transition-receipts/act-to-archive.json",
        ]
        if not all(path.is_file() for path in receipts):
            return "TRANSITION_RECEIPT_MISSING"
        phase = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))["meta"]["phase"]
        return "archived" if phase == "archive" else str(phase)


def lifecycle_plan_confirmation(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=False)
        _, payload = transition(root, task_dir, "do")
        return rejected_observation(payload, "FINAL_CONFIRMATION_MISSING")


def lifecycle_do_evidence(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        _, payload = transition(root, task_dir, "check")
        return rejected_observation(payload, "EVIDENCE_MANIFEST_MISSING")


def lifecycle_do_prd(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        (task_dir / "prd.md").unlink()
        _, payload = transition(root, task_dir, "check")
        return rejected_observation(payload, "PRD_MISSING")


def lifecycle_do_convergence(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        add_evidence(root, include_convergence=False)
        _, payload = transition(root, task_dir, "check")
        return rejected_observation(payload, "CONVERGENCE_MAP_MISSING")


def lifecycle_check_confirmation(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        add_evidence(root)
        if transition(root, task_dir, "check")[0] != 0:
            return "DO_TO_CHECK_FAILED"
        add_check_requirements(root, task_dir, include_confirmation=False)
        _, payload = transition(root, task_dir, "act")
        return rejected_observation(payload, "CHECK_CONFIRMATION_MISSING")


def lifecycle_check_conclusion(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        add_evidence(root)
        if transition(root, task_dir, "check")[0] != 0:
            return "DO_TO_CHECK_FAILED"
        add_check_requirements(root, task_dir, include_confirmation=True, include_conclusion=False)
        _, payload = transition(root, task_dir, "act")
        return rejected_observation(payload, "CONCLUSION_MISSING")


def lifecycle_check_verdict(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        add_evidence(root)
        if transition(root, task_dir, "check")[0] != 0:
            return "DO_TO_CHECK_FAILED"
        add_check_requirements(root, task_dir, include_confirmation=True, include_verdict=False)
        _, payload = transition(root, task_dir, "act")
        return rejected_observation(payload, "VERDICT_MISSING")


def lifecycle_act_disposition(source_root: Path) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root, task_dir = prepare_task(source_root, temporary, confirmed=True)
        if transition(root, task_dir, "do")[0] != 0:
            return "PLAN_TO_DO_FAILED"
        add_evidence(root)
        if transition(root, task_dir, "check")[0] != 0:
            return "DO_TO_CHECK_FAILED"
        add_check_requirements(root, task_dir, include_confirmation=True)
        if transition(root, task_dir, "act")[0] != 0:
            return "CHECK_TO_ACT_FAILED"
        _, payload = transition(root, task_dir, "archive")
        return rejected_observation(payload, "DISPOSITION_MISSING")


LIFECYCLE_FIXTURES: tuple[tuple[str, str, Callable[[Path], str]], ...] = (
    ("lifecycle-success", "archived", lifecycle_success),
    ("lifecycle-plan-confirmation", "FINAL_CONFIRMATION_MISSING", lifecycle_plan_confirmation),
    ("lifecycle-do-prd", "PRD_MISSING", lifecycle_do_prd),
    ("lifecycle-do-evidence", "EVIDENCE_MANIFEST_MISSING", lifecycle_do_evidence),
    ("lifecycle-do-convergence", "CONVERGENCE_MAP_MISSING", lifecycle_do_convergence),
    ("lifecycle-check-conclusion", "CONCLUSION_MISSING", lifecycle_check_conclusion),
    ("lifecycle-check-verdict", "VERDICT_MISSING", lifecycle_check_verdict),
    ("lifecycle-check-confirmation", "CHECK_CONFIRMATION_MISSING", lifecycle_check_confirmation),
    ("lifecycle-act-disposition", "DISPOSITION_MISSING", lifecycle_act_disposition),
)


CONTRACT_FIXTURES: tuple[tuple[str, str, Callable[[Path], str]], ...] = (
    ("execution-development-normal", "A", lambda root: execution_observation(root, "development")),
    ("execution-bugfix-normal", "B", lambda root: execution_observation(root, "bugfix")),
    ("execution-marker-order", "EXECUTION_MARKER_ORDER_DRIFT", execution_marker_order_observation),
    ("invocation-grill-alias", "grill", invocation_alias_observation),
    ("invocation-manual-edge", "INVOCATION_EDGE_FORBIDDEN", invocation_manual_edge_observation),
    ("invocation-stale-alias", "INVOCATION_ALIAS_UNDECLARED", invocation_stale_alias_observation),
)


def context_bytes(root: Path) -> int:
    path = root / "ontology/process/flow-do.md"
    return len(path.read_bytes()) if path.is_file() else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", required=True)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    root = repo_root(args.root)
    fixture_file = root / "tests/fixtures/ai-friendliness-scenarios.json"
    fixtures = json.loads(fixture_file.read_text(encoding="utf-8"))["fixtures"]

    results: list[dict[str, Any]] = []
    for fixture in fixtures:
        kind = fixture["kind"]
        if kind == "route":
            observed = route_observation(root, fixture["scenario"])
        elif kind == "reference":
            observed = reference_observation(root)
        else:
            observed = "FIXTURE_KIND_INVALID"
        results.append(
            {
                "id": fixture["id"],
                "scenario": fixture["scenario"],
                "expected": fixture["expected"],
                "observed": observed,
                "pass": observed == fixture["expected"],
            }
        )

    for identifier, expected, runner in CONTRACT_FIXTURES:
        observed = runner(root)
        results.append(
            {
                "id": identifier,
                "scenario": "contract",
                "expected": expected,
                "observed": observed,
                "pass": observed == expected,
            }
        )

    for identifier, expected, runner in LIFECYCLE_FIXTURES:
        observed = runner(root)
        results.append(
            {
                "id": identifier,
                "scenario": "lifecycle",
                "expected": expected,
                "observed": observed,
                "pass": observed == expected,
            }
        )

    payload = {
        "schema": "pdca.fixture-results/v2",
        "evaluation_scope": "deterministic route, execution, invocation, document, reference, and lifecycle contracts only",
        "context_bytes": {
            "metric": "utf8_bytes",
            "value": context_bytes(root),
            "note": "A reproducible content-size proxy, not an LLM token, latency, or success metric.",
        },
        "fixture_count": len(results),
        "passed": sum(item["pass"] for item in results),
        "failed": sum(not item["pass"] for item in results),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
