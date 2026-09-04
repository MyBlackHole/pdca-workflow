#!/usr/bin/env python3
"""Non-blocking, transition-level PDCA conformance audit."""

from __future__ import annotations

import json
import os
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from flow_issues import create_occurrence, cutover_is_active
from pdca_core import (
    acceptance_criteria,
    clarification_issues,
    convergence_issues,
    evidence_issues,
    load_json,
    load_jsonl,
)


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _check(identifier: str, description: str, issues: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "id": identifier,
        "description": description,
        "passed": not issues,
        "issues": issues,
    }


def _audit_location(issue: dict[str, str]) -> str:
    """Turn arbitrary validation paths into a safe, stable fingerprint location."""

    source = issue["path"].replace("\\", "/")
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    return f"audit/{issue['code'].lower()}-{digest}"


def _record_cutover_occurrences(
    root: Path,
    task: dict[str, Any],
    record_id: str,
    attempt: dict[str, Any],
) -> Path:
    for issue in attempt["issues"]:
        digest = hashlib.sha256(
            json.dumps(
                {
                    "at": attempt["at"],
                    "transition": f"{attempt['from']}-to-{attempt['to']}",
                    "issue": issue,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        create_occurrence(
            root,
            record_id=record_id,
            task_id=task["id"],
            source="transition-audit",
            category="conformance-deviation",
            phase=task["meta"]["phase"],
            transition=f"{attempt['from']}-to-{attempt['to']}",
            rule_id="transition-audit",
            rule_version="v2",
            affected_component="scripts.transition-phase",
            normalized_location=_audit_location(issue),
            issue_code=issue["code"],
            idempotency_key=f"audit:{task['id']}:{attempt['from']}-to-{attempt['to']}:{digest}",
            occurred_at=attempt["at"],
            evidence_refs=[f"audit:{attempt['from']}-to-{attempt['to']}:{digest}"],
            confidence="observed",
            gate_effect="blocked",
            before_state=attempt["from"],
            after_state=attempt["to"],
            summary=issue["message"],
        )
    return root / "records" / record_id / "flow-events"


def _plan_checks(root: Path, task_dir: Path, task: dict[str, Any]) -> list[dict[str, Any]]:
    task_index: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in (root / "pdca/tasks").glob("**/task.json"):
        try:
            candidate = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        candidate_id = candidate.get("id")
        if isinstance(candidate_id, str):
            task_index[candidate_id] = (path, candidate)

    creation_issues: list[dict[str, str]] = []
    inactive_issues: list[dict[str, str]] = []
    for child_id in task["children"]:
        indexed = task_index.get(child_id)
        if indexed is None:
            creation_issues.append(
                _issue("CHILD_MISSING", f"/children/{child_id}", "declared child task was not created")
            )
            continue
        path, child = indexed
        relative = path.relative_to(root).as_posix()
        if child.get("parent") != task["id"]:
            creation_issues.append(
                _issue("CHILD_PARENT_MISMATCH", relative, f"child parent must be {task['id']}")
            )
        if child.get("meta", {}).get("active") is False:
            inactive_issues.append(
                _issue("CHILD_INACTIVE", relative, "child task is inactive before parent enters Do")
            )

    entries, clarification_errors = clarification_issues(root, task_dir)
    confirmation_issues = [issue.as_dict() for issue in clarification_errors]
    if not any(
        entry.get("source") == "final_confirmation" and entry.get("response") == "confirmed"
        for entry in entries
    ):
        confirmation_issues.append(
            _issue("FINAL_CONFIRMATION_MISSING", "clarifications.jsonl", "confirmed response is required")
        )
    return [
        _check("children-created", "all declared child tasks exist and reference the parent", creation_issues),
        _check("children-active", "declared child tasks are active", inactive_issues),
        _check("final-confirmation", "Plan direction has final user confirmation", confirmation_issues),
    ]


def _do_checks(root: Path, task_dir: Path, task: dict[str, Any]) -> list[dict[str, Any]]:
    # HITL fix-confirmation gate (audit only, non-blocking for存量兼容): bugfix 需 fix_confirmation:confirmed
    entries_for_fix, _ = clarification_issues(root, task_dir)
    fix_issues: list[dict[str, str]] = []
    if task.get("meta", {}).get("scenario_type") == "bugfix":
        if not any(entry.get("source") == "fix_confirmation" and entry.get("response") == "confirmed" for entry in entries_for_fix):
            fix_issues.append(
                _issue("FIX_CONFIRMATION_MISSING", "clarifications.jsonl", "fix_confirmation:confirmed is required before code fix (HITL gate, audit WARN)")
            )
    evidence = evidence_issues(root, task)
    registration_codes = {"RECORD_MISSING", "RECORD_PATH_INVALID", "EVIDENCE_MANIFEST_MISSING", "EVIDENCE_MANIFEST_INVALID", "EVIDENCE_EMPTY", "EVIDENCE_FILE_MISSING"}
    integrity_codes = {
        "EVIDENCE_MANIFEST_INVALID",
        "EVIDENCE_EMPTY",
        "EVIDENCE_PATH_ESCAPE",
        "EVIDENCE_SIZE_MISMATCH",
        "EVIDENCE_DIGEST_MISMATCH",
        "SCHEMA_INVALID",
    }
    registration = [issue.as_dict() for issue in evidence if issue.code in registration_codes]
    integrity = [issue.as_dict() for issue in evidence if issue.code in integrity_codes]

    criteria, criterion_errors = acceptance_criteria(task_dir)
    coverage = [issue.as_dict() for issue in criterion_errors]
    record_id = task.get("meta", {}).get("record")
    manifest = root / "records" / str(record_id) / "evidence" / "manifest.jsonl"
    manifest_available = bool(record_id) and manifest.is_file()
    if not manifest_available:
        coverage.append(
            _issue(
                "AC_COVERAGE_UNVERIFIABLE",
                "/meta/record" if not record_id else manifest.relative_to(root).as_posix(),
                "acceptance coverage cannot be verified without an evidence manifest",
            )
        )
        integrity.append(
            _issue(
                "EVIDENCE_INTEGRITY_UNVERIFIABLE",
                "/meta/record" if not record_id else manifest.relative_to(root).as_posix(),
                "evidence integrity cannot be verified without a manifest",
            )
        )
    if manifest_available and criteria:
        try:
            entries = load_jsonl(manifest)
        except (OSError, ValueError):
            entries = []
        support = [entry for entry in entries if entry.get("kind") != "convergence-map"]
        for criterion in criteria:
            if not any(criterion in entry.get("criteria", []) for entry in support):
                coverage.append(
                    _issue("ACCEPTANCE_CRITERION_UNCOVERED", criterion, "criterion has no registered support evidence")
                )
    convergence = [issue.as_dict() for issue in convergence_issues(root, task_dir)]
    return [
        _check("evidence-registered", "evidence manifest and referenced artifacts exist", registration),
        _check("ac-coverage", "every PRD acceptance criterion has non-map evidence", coverage),
        _check("evidence-integrity", "evidence size and SHA-256 match the manifest", integrity),
        _check("convergence-map", "Plan convergence maps to criteria and evidence", convergence),
        _check("fix-confirmation", "bugfix has fix_confirmation before code change (HITL gate)", fix_issues),
    ]


def _check_checks(root: Path, _task_dir: Path, task: dict[str, Any]) -> list[dict[str, Any]]:
    record_id = task.get("meta", {}).get("record")
    conclusion = root / "records" / str(record_id) / "conclusion.md"
    conclusion_issues = [] if conclusion.is_file() else [
        _issue("CONCLUSION_MISSING", conclusion.relative_to(root).as_posix(), "conclusion is required")
    ]
    verdict_issues = [] if task.get("meta", {}).get("verdict") else [
        _issue("VERDICT_MISSING", "/meta/verdict", "verdict is required")
    ]
    return [
        _check("conclusion-recorded", "Check conclusion exists", conclusion_issues),
        _check("verdict-recorded", "Check verdict is recorded", verdict_issues),
    ]


def _act_checks(_root: Path, _task_dir: Path, task: dict[str, Any]) -> list[dict[str, Any]]:
    issues = [] if task.get("meta", {}).get("disposition") else [
        _issue("DISPOSITION_MISSING", "/meta/disposition", "knowledge disposition is required")
    ]
    return [_check("disposition-recorded", "Act knowledge disposition is recorded", issues)]


CHECKS: dict[str, Callable[[Path, Path, dict[str, Any]], list[dict[str, Any]]]] = {
    "plan-to-do": _plan_checks,
    "do-to-check": _do_checks,
    "check-to-act": _check_checks,
    "act-to-archive": _act_checks,
}


def _quarantine_audit(
    root: Path,
    task: dict[str, Any],
    transition: str,
    attempt: dict[str, Any],
) -> Path:
    quarantine_dir = root / "records" / "__quarantine"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    path = quarantine_dir / "flow-audit.json"
    payload = {
        "schema": "pdca.flow-audit/v1",
        "task_id": task["id"],
        "record_id": None,
        "transitions": {transition: {"latest": attempt, "attempts": [attempt]}},
    }
    _atomic_json(path, payload)
    return path


def audit_transition(root: Path, task_dir: Path, target: str) -> Path:
    task = load_json(task_dir / "task.json")
    transition = f"{task['meta']['phase']}-to-{target}"
    checks = CHECKS[transition](root, task_dir, task)
    record_id = task.get("meta", {}).get("record")
    records_root = (root / "records").resolve()
    record_path_issues: list[dict[str, str]] = []
    record_dir: Path | None = None
    if not record_id:
        record_path_issues.append(
            _issue(
                "RECORD_MISSING",
                "/meta/record",
                "record identity is missing; no task.id fallback is allowed",
            )
        )
    else:
        candidate_dir = (records_root / str(record_id)).resolve()
        if candidate_dir.parent != records_root:
            record_path_issues.append(
                _issue(
                    "AUDIT_RECORD_PATH_INVALID",
                    "/meta/record",
                    "audit record must be a direct child of records",
                )
            )
        else:
            record_dir = candidate_dir
    checks.append(_check("audit-record-path", "audit output stays inside records", record_path_issues))
    issues = [issue for check in checks for issue in check["issues"]]
    attempt = {
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "from": task["meta"]["phase"],
        "to": target,
        "passed": not issues,
        "checks": checks,
        "issues": issues,
    }
    if cutover_is_active(root):
        if record_dir is not None:
            return _record_cutover_occurrences(root, task, record_id or "", attempt)
        return _quarantine_audit(root, task, transition, attempt)
    if record_dir is None:
        return _quarantine_audit(root, task, transition, attempt)

    path = record_dir / "flow-audit.json"
    if path.is_file():
        payload = load_json(path)
    else:
        payload = {
            "schema": "pdca.flow-audit/v1",
            "task_id": task["id"],
            "record_id": record_id,
            "transitions": {},
        }
    bucket = payload["transitions"].setdefault(transition, {"latest": attempt, "attempts": []})
    bucket["attempts"].append(attempt)
    bucket["latest"] = attempt
    _atomic_json(path, payload)
    return path
