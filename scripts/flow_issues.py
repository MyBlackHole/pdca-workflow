#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-continuous-improvement（Flow Issue 存储原语）；本体是源、代码是投射。
"""Shared strict storage primitives for Flow Issue CLI commands."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import fcntl

from task_identity import TaskIdentityError, _create_task_unlocked
from pdca_core import load_json, load_jsonl, repo_root, schema_issues


SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
SAFE_LOCATION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
METRIC_NAME = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
TASK_SLUG = re.compile(r"^[0-9]{4}-[a-z0-9][a-z0-9-]*$")
TRANSITIONS = {"plan-to-do", "do-to-check", "check-to-act", "act-to-archive"}


class FlowIssueError(Exception):
    """A stable CLI rejection that can be returned to AI callers."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def payload(self) -> dict[str, str]:
        return {"status": "rejected", "error": self.code, "path": self.path, "message": self.message}


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def run_command(command: Any) -> int:
    """Run a CLI command while preserving the single-JSON-stdout contract."""

    try:
        emit(command())
        return 0
    except FlowIssueError as exc:
        emit(exc.payload())
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return 1
    except Exception as exc:
        failure = FlowIssueError("INTERNAL_ERROR", "/", "unexpected command failure")
        emit(failure.payload())
        print(f"{failure.code}: {exc}", file=sys.stderr)
        return 1


def resolve_root(value: Path | None) -> Path:
    try:
        return repo_root(value)
    except ValueError as exc:
        raise FlowIssueError("ROOT_INVALID", "--root", str(exc)) from exc


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def parse_datetime(value: str, path: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise FlowIssueError("INVALID_TIMESTAMP", path, "must be an ISO-8601 date-time") from exc
    if parsed.tzinfo is None:
        raise FlowIssueError("INVALID_TIMESTAMP", path, "must include a UTC offset")
    return parsed


def _safe_name(value: str, path: str) -> str:
    if not SAFE_NAME.fullmatch(value):
        raise FlowIssueError("PATH_INVALID", path, "must be a safe direct child name")
    return value


def _safe_key(value: str, path: str) -> str:
    if not SAFE_KEY.fullmatch(value) or len(value) > 128:
        raise FlowIssueError("INVALID_IDEMPOTENCY_KEY", path, "must contain only stable safe characters")
    return value


def _safe_component(value: str) -> str:
    if not SAFE_COMPONENT.fullmatch(value) or ".." in value or value.startswith("/"):
        raise FlowIssueError("PATH_INVALID", "--affected-component", "must be a normalized relative component")
    return value


def _safe_location(value: str) -> str:
    normalized = value.replace("\\", "/")
    if (
        not SAFE_LOCATION.fullmatch(normalized)
        or ".." in normalized
        or normalized.startswith("/")
        or "//" in normalized
    ):
        raise FlowIssueError("PATH_INVALID", "--normalized-location", "must be a normalized relative location")
    return normalized


def _validate(root: Path, value: dict[str, Any], schema: str, path: str) -> None:
    issues = schema_issues(root, value, schema)
    if issues:
        first = issues[0]
        raise FlowIssueError(first.code, f"{path}{first.path}", first.message)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _create_only_json(
    root: Path,
    path: Path,
    value: dict[str, Any],
    schema: str,
    corrupt_code: str,
    conflict_code: str,
) -> str:
    """Create one JSON file without replacement, comparing existing canonical content."""

    _validate(root, value, schema, str(path))
    content = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            try:
                existing = load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                raise FlowIssueError(corrupt_code, str(path), "existing immutable artifact is unreadable") from exc
            _validate(root, existing, schema, str(path))
            if canonical_bytes(existing) != content:
                raise FlowIssueError(
                    conflict_code,
                    str(path),
                    "the idempotency key already belongs to different normalized content",
                )
            return "unchanged"
        _fsync_directory(path.parent)
        return "created"
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_replace_json(root: Path, path: Path, value: dict[str, Any], schema: str) -> None:
    _validate(root, value, schema, str(path))
    content = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def cutover_path(root: Path) -> Path:
    return root / "pdca" / "improvements" / "flow-issue-cutover.json"


def create_cutover(root: Path, commit: str, started_at: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{7,64}", commit):
        raise FlowIssueError("INVALID_COMMIT", "--commit", "must be a lowercase Git SHA")
    parse_datetime(started_at, "--started-at")
    value = {
        "schema": "pdca.flow-issue-cutover/v1",
        "commit": commit,
        "occurrence_schema_version": "v1",
        "fingerprint_version": "v1",
        "started_at": started_at,
    }
    path = cutover_path(root)
    status = _create_only_json(
        root,
        path,
        value,
        "flow-issue-cutover.schema.json",
        "CUTOVER_CORRUPT",
        "CUTOVER_CONFLICT",
    )
    return {
        "status": status,
        "path": path.relative_to(root).as_posix(),
        "digest": sha256_bytes(canonical_bytes(value)),
    }


def load_cutover(root: Path) -> dict[str, Any]:
    path = cutover_path(root)
    if not path.is_file():
        raise FlowIssueError("CUTOVER_MISSING", path.relative_to(root).as_posix(), "create a cutover receipt first")
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise FlowIssueError("CUTOVER_CORRUPT", path.relative_to(root).as_posix(), "cutover receipt is unreadable") from exc
    _validate(root, value, "flow-issue-cutover.schema.json", path.relative_to(root).as_posix())
    parse_datetime(value["started_at"], "started_at")
    return value


def cutover_is_active(root: Path) -> bool:
    if not cutover_path(root).is_file():
        return False
    load_cutover(root)
    return True


def event_id(record_id: str, idempotency_key: str) -> str:
    material = f"{record_id}\0{idempotency_key}".encode("utf-8")
    return f"FE-{hashlib.sha256(material).hexdigest()[:24]}"


def create_occurrence(
    root: Path,
    *,
    record_id: str,
    task_id: str,
    source: str,
    category: str,
    phase: str,
    transition: str | None,
    rule_id: str,
    rule_version: str,
    affected_component: str,
    normalized_location: str,
    issue_code: str,
    idempotency_key: str,
    occurred_at: str,
    evidence_refs: list[str],
    confidence: str = "observed",
    gate_effect: str = "unknown",
    exit_code: int | None = None,
    before_state: str | None = None,
    after_state: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    if not re.fullmatch(r"T[0-9]{4,}", task_id):
        raise FlowIssueError("INVALID_TASK_ID", "--task-id", "must be a strict PDCA task ID")
    idempotency_key = _safe_key(idempotency_key, "--idempotency-key")
    if transition is not None and transition not in TRANSITIONS:
        raise FlowIssueError("INVALID_TRANSITION", "--transition", "must name an adjacent PDCA transition")
    if not re.fullmatch(r"[a-z][a-z0-9._-]{0,63}", rule_id):
        raise FlowIssueError("INVALID_RULE", "--rule-id", "must be a stable lowercase identifier")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", rule_version):
        raise FlowIssueError("INVALID_RULE", "--rule-version", "must be a stable version")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{1,63}", issue_code):
        raise FlowIssueError("INVALID_ISSUE_CODE", "--issue-code", "must be an uppercase stable code")
    parse_datetime(occurred_at, "--occurred-at")
    cutover = load_cutover(root)
    if parse_datetime(occurred_at, "--occurred-at") < parse_datetime(cutover["started_at"], "started_at"):
        raise FlowIssueError("OCCURRENCE_BEFORE_CUTOVER", "--occurred-at", "must not predate the cutover")
    if not evidence_refs:
        raise FlowIssueError("EVIDENCE_REFERENCE_MISSING", "--evidence-ref", "at least one evidence reference is required")
    normalized_refs = sorted(set(evidence_refs))
    if len(normalized_refs) != len(evidence_refs) or any(not SAFE_KEY.fullmatch(item) for item in normalized_refs):
        raise FlowIssueError("INVALID_EVIDENCE_REFERENCE", "--evidence-ref", "must be unique stable references")

    value: dict[str, Any] = {
        "schema": "pdca.flow-issue-occurrence/v1",
        "event_id": event_id(record_id, idempotency_key),
        "record_id": record_id,
        "task_id": task_id,
        "idempotency_key": idempotency_key,
        "source": source,
        "category": category,
        "phase": phase,
        "transition": transition,
        "rule": {"id": rule_id, "version": rule_version},
        "affected_component": _safe_component(affected_component),
        "normalized_location": _safe_location(normalized_location),
        "issue_code": issue_code,
        "occurred_at": occurred_at,
        "facts": {
            "confidence": confidence,
            "gate_effect": gate_effect,
            "exit_code": exit_code,
            "before_state": before_state,
            "after_state": after_state,
        },
        "evidence_refs": normalized_refs,
    }
    if summary is not None:
        value["summary"] = summary
    path = root / "records" / record_id / "flow-events" / f"{value['event_id']}.json"
    status = _create_only_json(
        root,
        path,
        value,
        "flow-issue-occurrence.schema.json",
        "OCCURRENCE_CORRUPT",
        "IDEMPOTENCY_CONFLICT",
    )
    return {
        "status": status,
        "event_id": value["event_id"],
        "path": path.relative_to(root).as_posix(),
        "digest": sha256_bytes(canonical_bytes(value)),
    }


def projection_path(root: Path) -> Path:
    return root / "pdca" / "improvements" / "flow-issue-backlog.json"


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise FlowIssueError("EVENT_PATH_ESCAPE", str(path), "event path must stay inside the PDCA root") from exc


def _read_occurrence(root: Path, path: Path) -> tuple[dict[str, Any], str, str]:
    relative = _relative_path(root, path)
    parts = Path(relative).parts
    if len(parts) != 4 or parts[0] != "records" or parts[2] != "flow-events":
        raise FlowIssueError("EVENT_PATH_INVALID", relative, "event must be in records/<record>/flow-events/")
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise FlowIssueError("EVENT_CORRUPT", relative, "event JSON is unreadable") from exc
    _validate(root, value, "flow-issue-occurrence.schema.json", relative)
    if value["record_id"] != parts[1]:
        raise FlowIssueError("EVENT_PATH_MISMATCH", relative, "record_id must match the event directory")
    if path.name != f"{value['event_id']}.json":
        raise FlowIssueError("EVENT_PATH_MISMATCH", relative, "event_id must match the filename")
    parse_datetime(value["occurred_at"], f"{relative}/occurred_at")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise FlowIssueError("EVENT_MISSING", relative, "event disappeared while aggregating") from exc
    return value, relative, sha256_bytes(raw)


def _discover_occurrences(root: Path) -> tuple[dict[str, Any], list[tuple[dict[str, Any], str, str]]]:
    cutover = load_cutover(root)
    started_at = parse_datetime(cutover["started_at"], "cutover.started_at")
    records_root = root / "records"
    discovered: list[tuple[dict[str, Any], str, str]] = []
    if not records_root.is_dir():
        return cutover, discovered
    paths = sorted(records_root.glob("*/flow-events/*.json"), key=lambda item: item.as_posix())
    for path in paths:
        value, relative, digest = _read_occurrence(root, path)
        if parse_datetime(value["occurred_at"], f"{relative}/occurred_at") >= started_at:
            discovered.append((value, relative, digest))
    return cutover, discovered


def _fingerprint(value: dict[str, Any], fingerprint_version: str) -> dict[str, Any]:
    return {
        "fingerprint_version": fingerprint_version,
        "rule_id": value["rule"]["id"],
        "rule_version": value["rule"]["version"],
        "category": value["category"],
        "transition": value["transition"],
        "affected_component": value["affected_component"],
        "normalized_location": value["normalized_location"],
        "issue_code": value["issue_code"],
    }


def _issue_id(fingerprint: dict[str, Any]) -> str:
    return f"FI-{hashlib.sha256(canonical_bytes(fingerprint)).hexdigest()[:24]}"


def _input_digest(events: list[tuple[dict[str, Any], str, str]]) -> str:
    digest = hashlib.sha256()
    for _value, path, content_digest in events:
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content_digest.encode("ascii"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def aggregate_occurrences(
    root: Path,
    projection_version: str = "v1",
    fingerprint_version: str = "v1",
) -> dict[str, Any]:
    if projection_version != "v1":
        raise FlowIssueError("PROJECTION_VERSION_UNSUPPORTED", "--projection-version", "only v1 is supported")
    if fingerprint_version != "v1":
        raise FlowIssueError("FINGERPRINT_VERSION_UNSUPPORTED", "--fingerprint-version", "only v1 is supported")
    cutover, events = _discover_occurrences(root)
    groups: dict[str, dict[str, Any]] = {}
    for value, relative, _digest in events:
        fingerprint = _fingerprint(value, fingerprint_version)
        issue_id = _issue_id(fingerprint)
        group = groups.setdefault(
            issue_id,
            {
                "issue_id": issue_id,
                "fingerprint": fingerprint,
                "events": [],
            },
        )
        group["events"].append((value, relative))

    issues: list[dict[str, Any]] = []
    for group in groups.values():
        event_pairs = sorted(
            group["events"],
            key=lambda item: (parse_datetime(item[0]["occurred_at"], f"{item[1]}/occurred_at"), item[1]),
        )
        issues.append(
            {
                "issue_id": group["issue_id"],
                "fingerprint": group["fingerprint"],
                "event_count": len(event_pairs),
                "event_ids": sorted(item[0]["event_id"] for item in event_pairs),
                "event_paths": sorted(item[1] for item in event_pairs),
                "record_ids": sorted({item[0]["record_id"] for item in event_pairs}),
                "sources": sorted({item[0]["source"] for item in event_pairs}),
                "first_occurred_at": event_pairs[0][0]["occurred_at"],
                "last_occurred_at": event_pairs[-1][0]["occurred_at"],
            }
        )
    issues.sort(key=lambda item: (-item["event_count"], item["issue_id"]))
    backlog = {
        "schema": "pdca.flow-issue-backlog/v1",
        "projection_version": projection_version,
        "fingerprint_version": fingerprint_version,
        "cutover": {"commit": cutover["commit"], "started_at": cutover["started_at"]},
        "input_digest": _input_digest(events),
        "issues": issues,
    }
    path = projection_path(root)
    _atomic_replace_json(root, path, backlog, "flow-issue-backlog.schema.json")
    return {
        "status": "generated",
        "path": path.relative_to(root).as_posix(),
        "issue_count": len(issues),
        "digest": sha256_bytes(canonical_bytes(backlog)),
    }


def load_backlog(root: Path) -> dict[str, Any]:
    path = projection_path(root)
    if not path.is_file():
        raise FlowIssueError("BACKLOG_MISSING", path.relative_to(root).as_posix(), "run aggregate-flow-issues first")
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise FlowIssueError("BACKLOG_CORRUPT", path.relative_to(root).as_posix(), "backlog JSON is unreadable") from exc
    _validate(root, value, "flow-issue-backlog.schema.json", path.relative_to(root).as_posix())
    return value


def _compact_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "issue_id": issue["issue_id"],
        "fingerprint": issue["fingerprint"],
        "event_count": issue["event_count"],
        "record_ids": issue["record_ids"],
        "sources": issue["sources"],
        "first_occurred_at": issue["first_occurred_at"],
        "last_occurred_at": issue["last_occurred_at"],
    }


def query_occurrences(
    root: Path,
    *,
    limit: int = 20,
    cursor: str | None = None,
    issue_id: str | None = None,
) -> dict[str, Any]:
    if not 1 <= limit <= 100:
        raise FlowIssueError("LIMIT_INVALID", "--limit", "must be between 1 and 100")
    backlog = load_backlog(root)
    digest = sha256_bytes(canonical_bytes(backlog))
    issues = backlog["issues"]
    if issue_id is not None:
        matches = [item for item in issues if item["issue_id"] == issue_id]
        if not matches:
            raise FlowIssueError("ISSUE_NOT_FOUND", "--issue-id", "issue is absent from the current backlog")
        issue = matches[0]
        occurrences: list[dict[str, Any]] = []
        for event_path in issue["event_paths"]:
            path = root / event_path
            if not path.is_file():
                raise FlowIssueError("EVENT_MISSING", event_path, "backlog references a missing occurrence")
            occurrence, _relative, _content_digest = _read_occurrence(root, path)
            occurrences.append(occurrence)
        occurrences.sort(key=lambda item: (item["occurred_at"], item["event_id"]))
        return {
            "status": "ok",
            "digest": digest,
            "issue": _compact_issue(issue),
            "occurrences": occurrences,
        }

    start = 0
    if cursor is not None:
        cursor_positions = [index for index, item in enumerate(issues) if item["issue_id"] == cursor]
        if not cursor_positions:
            raise FlowIssueError("CURSOR_INVALID", "--cursor", "must be an issue_id from the current backlog")
        start = cursor_positions[0] + 1
    selected = issues[start : start + limit]
    next_cursor = selected[-1]["issue_id"] if start + len(selected) < len(issues) and selected else None
    return {
        "status": "ok",
        "digest": digest,
        "issues": [_compact_issue(item) for item in selected],
        "next_cursor": next_cursor,
    }


def _require_issue(root: Path, issue_id: str, record_id: str) -> dict[str, Any]:
    if not re.fullmatch(r"FI-[0-9a-f]{24}", issue_id):
        raise FlowIssueError("INVALID_ISSUE_ID", "--issue-id", "must be an issue ID from the backlog")
    issue = next((item for item in load_backlog(root)["issues"] if item["issue_id"] == issue_id), None)
    if issue is None:
        raise FlowIssueError("ISSUE_NOT_FOUND", "--issue-id", "issue is absent from the current backlog")
    if record_id not in issue["record_ids"]:
        raise FlowIssueError("ISSUE_RECORD_MISMATCH", "--record", "record does not contribute to this issue")
    return issue


def _artifact_id(prefix: str, record_id: str, idempotency_key: str) -> str:
    material = f"{record_id}\0{idempotency_key}".encode("utf-8")
    return f"{prefix}-{hashlib.sha256(material).hexdigest()[:24]}"


def candidate_path(root: Path, record_id: str, candidate_id: str) -> Path:
    return root / "records" / record_id / "flow-improvements" / "candidates" / f"{candidate_id}.json"


def decision_path(root: Path, record_id: str, decision_id: str) -> Path:
    return root / "records" / record_id / "flow-improvements" / "decisions" / f"{decision_id}.json"


def _load_immutable_artifact(
    root: Path,
    path: Path,
    schema: str,
    missing_code: str,
    corrupt_code: str,
) -> dict[str, Any]:
    relative = _relative_path(root, path)
    if not path.is_file():
        raise FlowIssueError(missing_code, relative, "immutable artifact does not exist")
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise FlowIssueError(corrupt_code, relative, "immutable artifact is unreadable") from exc
    _validate(root, value, schema, relative)
    return value


def load_candidate(root: Path, record_id: str, candidate_id: str) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    if not re.fullmatch(r"FC-[0-9a-f]{24}", candidate_id):
        raise FlowIssueError("INVALID_CANDIDATE_ID", "--candidate-id", "must be a candidate ID")
    value = _load_immutable_artifact(
        root,
        candidate_path(root, record_id, candidate_id),
        "improvement-candidate.schema.json",
        "CANDIDATE_MISSING",
        "CANDIDATE_CORRUPT",
    )
    if value["candidate_id"] != candidate_id or value["record_id"] != record_id:
        raise FlowIssueError("CANDIDATE_PATH_MISMATCH", "--candidate-id", "candidate identity does not match storage")
    return value


def load_decision(root: Path, record_id: str, decision_id: str) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    if not re.fullmatch(r"FD-[0-9a-f]{24}", decision_id):
        raise FlowIssueError("INVALID_DECISION_ID", "--decision-id", "must be a decision ID")
    value = _load_immutable_artifact(
        root,
        decision_path(root, record_id, decision_id),
        "flow-issue-decision.schema.json",
        "DECISION_MISSING",
        "DECISION_CORRUPT",
    )
    if value["decision_id"] != decision_id or value["record_id"] != record_id:
        raise FlowIssueError("DECISION_PATH_MISMATCH", "--decision-id", "decision identity does not match storage")
    return value


def _normalized_decimal(value: str, path: str) -> str:
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise FlowIssueError("METRIC_INVALID", path, "must be a nonnegative decimal") from exc
    if not number.is_finite() or number < 0:
        raise FlowIssueError("METRIC_INVALID", path, "must be a nonnegative decimal")
    normalized = format(number.normalize(), "f")
    normalized = normalized.rstrip("0").rstrip(".") if "." in normalized else normalized
    return normalized or "0"


def _parse_metrics(values: list[str]) -> list[dict[str, str]]:
    if not values:
        raise FlowIssueError("METRIC_MISSING", "--metric", "at least one metric is required")
    metrics: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in values:
        parts = raw.split(":")
        if len(parts) != 3 or not METRIC_NAME.fullmatch(parts[0]):
            raise FlowIssueError("METRIC_INVALID", "--metric", "use name:baseline:target")
        name, baseline_raw, target_raw = parts
        if name in seen:
            raise FlowIssueError("METRIC_DUPLICATE", "--metric", "metric names must be unique")
        baseline = _normalized_decimal(baseline_raw, "--metric")
        target = _normalized_decimal(target_raw, "--metric")
        if Decimal(target) > Decimal(baseline):
            raise FlowIssueError("METRIC_TARGET_INVALID", "--metric", "target must not exceed the baseline")
        seen.add(name)
        metrics.append({"name": name, "baseline": baseline, "target": target})
    return sorted(metrics, key=lambda item: item["name"])


def create_candidate(
    root: Path,
    *,
    record_id: str,
    issue_id: str,
    event_ids: list[str],
    idempotency_key: str,
    created_at: str,
    root_cause_hypothesis: str,
    target_component: str,
    baseline: str,
    metrics: list[str],
    risks: list[str],
    rule_id: str,
    rule_version: str,
    min_opportunities: int,
    max_observation_days: int,
    kind: str = "improvement",
    status: str = "dry-run",
    origin_verdict_id: str | None = None,
) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    idempotency_key = _safe_key(idempotency_key, "--idempotency-key")
    parse_datetime(created_at, "--created-at")
    issue = _require_issue(root, issue_id, record_id)
    if not event_ids:
        raise FlowIssueError("EVENT_REFERENCE_MISSING", "--event-id", "at least one source event is required")
    normalized_event_ids = sorted(set(event_ids))
    if len(normalized_event_ids) != len(event_ids) or any(
        not re.fullmatch(r"FE-[0-9a-f]{24}", item) for item in normalized_event_ids
    ):
        raise FlowIssueError("EVENT_REFERENCE_INVALID", "--event-id", "must be unique occurrence IDs")
    if any(event_id not in issue["event_ids"] for event_id in normalized_event_ids):
        raise FlowIssueError("EVENT_ISSUE_MISMATCH", "--event-id", "event does not belong to the issue")
    if not root_cause_hypothesis.strip() or not baseline.strip():
        raise FlowIssueError("CANDIDATE_FIELD_MISSING", "/", "root cause and baseline are required")
    if not re.fullmatch(r"[a-z][a-z0-9._-]{0,63}", rule_id):
        raise FlowIssueError("INVALID_RULE", "--rule-id", "must be a stable lowercase identifier")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", rule_version):
        raise FlowIssueError("INVALID_RULE", "--rule-version", "must be a stable version")
    if not 1 <= min_opportunities <= 1_000_000:
        raise FlowIssueError("OBSERVATION_PLAN_INVALID", "--min-opportunities", "must be between 1 and 1000000")
    if not 1 <= max_observation_days <= 3650:
        raise FlowIssueError("OBSERVATION_PLAN_INVALID", "--max-observation-days", "must be between 1 and 3650")
    normalized_risks = sorted({risk.strip() for risk in risks if risk.strip()})
    if not normalized_risks:
        raise FlowIssueError("RISK_MISSING", "--risk", "at least one stated risk is required")
    candidate_id = _artifact_id("FC", record_id, idempotency_key)
    value = {
        "schema": "pdca.improvement-candidate/v1",
        "candidate_id": candidate_id,
        "record_id": record_id,
        "issue_id": issue_id,
        "event_ids": normalized_event_ids,
        "idempotency_key": idempotency_key,
        "kind": kind,
        "status": status,
        "root_cause_hypothesis": root_cause_hypothesis.strip(),
        "target_component": _safe_component(target_component),
        "baseline": baseline.strip(),
        "metrics": _parse_metrics(metrics),
        "risks": normalized_risks,
        "observation_plan": {
            "rule_id": rule_id,
            "rule_version": rule_version,
            "min_opportunities": min_opportunities,
            "max_observation_days": max_observation_days,
        },
        "origin_verdict_id": origin_verdict_id,
        "created_at": created_at,
    }
    path = candidate_path(root, record_id, candidate_id)
    status_value = _create_only_json(
        root,
        path,
        value,
        "improvement-candidate.schema.json",
        "CANDIDATE_CORRUPT",
        "IDEMPOTENCY_CONFLICT",
    )
    return {
        "status": status_value,
        "candidate_id": candidate_id,
        "path": path.relative_to(root).as_posix(),
        "digest": sha256_bytes(canonical_bytes(value)),
        "candidate": value,
    }


def _user_confirmation(
    root: Path,
    task_id: str,
    source: str,
    confirmed_at: str,
    confirmed_by: str,
    action: str,
    issue_id: str,
    candidate_id: str | None,
) -> dict[str, str]:
    if source != "user_decision":
        raise FlowIssueError("CONFIRMATION_INVALID", "--confirmation-source", "must be a bound user_decision receipt")
    if not confirmed_by.strip():
        raise FlowIssueError("CONFIRMATION_INVALID", "--confirmed-by", "must name the confirmer")
    parse_datetime(confirmed_at, "--confirmation-at")
    matches: list[Path] = []
    for task_path in (root / "pdca" / "tasks").glob("**/task.json"):
        try:
            task = load_json(task_path)
        except (OSError, json.JSONDecodeError):
            continue
        if task.get("id") == task_id:
            matches.append(task_path)
    if len(matches) != 1:
        raise FlowIssueError("CONFIRMATION_INVALID", "--confirmation-task-id", "must resolve to exactly one task")
    clarification_path = matches[0].parent / "clarifications.jsonl"
    try:
        entries = load_jsonl(clarification_path)
    except (OSError, ValueError) as exc:
        raise FlowIssueError("CONFIRMATION_INVALID", str(clarification_path), "confirmation log is unreadable") from exc
    for index, entry in enumerate(entries, 1):
        if (
            entry.get("source") == source
            and entry.get("response") == "confirmed"
            and entry.get("at") == confirmed_at
            and entry.get("decision")
            == {
                "action": action,
                "issue_id": issue_id,
                "candidate_id": candidate_id,
            }
        ):
            return {
                "mode": "user-confirmation",
                "reference": f"{task_id}:clarifications.jsonl:{index}",
                "confirmed_by": confirmed_by.strip(),
                "confirmed_at": confirmed_at,
            }
    raise FlowIssueError("CONFIRMATION_INVALID", "--confirmation-at", "no matching confirmed user decision exists")


def create_decision(
    root: Path,
    *,
    record_id: str,
    issue_id: str,
    candidate_id: str | None,
    action: str,
    reason: str,
    idempotency_key: str,
    decided_at: str,
    confirmation_task_id: str,
    confirmation_source: str,
    confirmation_at: str,
    confirmed_by: str,
    impact: str | None = None,
) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    idempotency_key = _safe_key(idempotency_key, "--idempotency-key")
    parse_datetime(decided_at, "--decided-at")
    issue = _require_issue(root, issue_id, record_id)
    if action not in {"false-positive", "accepted-risk", "close", "set-impact", "promote-candidate"}:
        raise FlowIssueError("ACTION_INVALID", "--action", "must be a user-governed decision action")
    if not reason.strip():
        raise FlowIssueError("DECISION_REASON_MISSING", "--reason", "must explain the decision")
    if action == "set-impact":
        if impact not in {"low", "medium", "high", "critical"}:
            raise FlowIssueError("IMPACT_INVALID", "--impact", "set-impact requires low, medium, high, or critical")
    elif impact is not None:
        raise FlowIssueError("IMPACT_INVALID", "--impact", "impact is only valid for set-impact")
    if action == "promote-candidate":
        if candidate_id is None:
            raise FlowIssueError("CANDIDATE_REQUIRED", "--candidate-id", "promotion requires a candidate")
        candidate = load_candidate(root, record_id, candidate_id)
        if candidate["issue_id"] != issue["issue_id"]:
            raise FlowIssueError("CANDIDATE_ISSUE_MISMATCH", "--candidate-id", "candidate does not belong to this issue")
    elif candidate_id is not None:
        raise FlowIssueError("CANDIDATE_UNEXPECTED", "--candidate-id", "candidate is only valid for promotion")

    value = {
        "schema": "pdca.flow-issue-decision/v1",
        "decision_id": _artifact_id("FD", record_id, idempotency_key),
        "record_id": record_id,
        "issue_id": issue_id,
        "candidate_id": candidate_id,
        "idempotency_key": idempotency_key,
        "action": action,
        "reason": reason.strip(),
        "impact": impact if action == "set-impact" else None,
        "authorization": _user_confirmation(
            root,
            confirmation_task_id,
            confirmation_source,
            confirmation_at,
            confirmed_by,
            action,
            issue_id,
            candidate_id,
        ),
        "decided_at": decided_at,
    }
    path = decision_path(root, record_id, value["decision_id"])
    status_value = _create_only_json(
        root,
        path,
        value,
        "flow-issue-decision.schema.json",
        "DECISION_CORRUPT",
        "IDEMPOTENCY_CONFLICT",
    )
    return {
        "status": status_value,
        "decision_id": value["decision_id"],
        "path": path.relative_to(root).as_posix(),
        "digest": sha256_bytes(canonical_bytes(value)),
        "decision": value,
    }


def _find_promoted_task(
    root: Path,
    record_id: str,
    issue_id: str,
    candidate_id: str,
    decision_id: str,
) -> Path | None:
    for task_path in sorted((root / "pdca" / "tasks").glob("**/task.json")):
        try:
            task = load_json(task_path)
        except (OSError, json.JSONDecodeError):
            continue
        source = task.get("meta", {}).get("improvement_source")
        if source == {
            "record_id": record_id,
            "issue_id": issue_id,
            "candidate_id": candidate_id,
            "decision_id": decision_id,
        }:
            return task_path.parent
    return None


def _write_new_file(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass


@contextmanager
def _promotion_lock(root: Path) -> Any:
    """Serialize source de-duplication and task-ID allocation across CLI processes."""

    digest = hashlib.sha256(str(root.resolve()).encode("utf-8")).hexdigest()
    path = Path(tempfile.gettempdir()) / f"pdca-flow-promotion-{digest}.lock"
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def promote_candidate(
    root: Path,
    *,
    record_id: str,
    candidate_id: str,
    decision_id: str,
    slug: str,
    title: str,
    created_at: str,
) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    if not TASK_SLUG.fullmatch(slug):
        raise FlowIssueError("TASK_SLUG_INVALID", "--slug", "must be a strict PDCA task slug")
    if not title.strip():
        raise FlowIssueError("TASK_TITLE_MISSING", "--title", "must be nonempty")
    parse_datetime(created_at, "--created-at")
    candidate = load_candidate(root, record_id, candidate_id)
    decision = load_decision(root, record_id, decision_id)
    if decision["action"] != "promote-candidate" or decision["candidate_id"] != candidate_id:
        raise FlowIssueError("PROMOTION_NOT_AUTHORIZED", "--decision-id", "decision does not authorize this candidate")
    if decision["issue_id"] != candidate["issue_id"]:
        raise FlowIssueError("PROMOTION_NOT_AUTHORIZED", "--decision-id", "decision and candidate issue IDs differ")
    if decision["authorization"]["mode"] != "user-confirmation":
        raise FlowIssueError("PROMOTION_NOT_AUTHORIZED", "--decision-id", "promotion requires a user confirmation")
    with _promotion_lock(root):
        existing = _find_promoted_task(
            root,
            record_id,
            candidate["issue_id"],
            candidate_id,
            decision_id,
        )
        if existing is not None:
            return {
                "status": "unchanged",
                "task_id": load_json(existing / "task.json")["id"],
                "path": existing.relative_to(root).as_posix(),
            }

        active_root = root / "pdca" / "tasks" / "active"
        active_root.mkdir(parents=True, exist_ok=True)
        destination = active_root / slug
        if destination.exists():
            raise FlowIssueError("TASK_PATH_CONFLICT", destination.relative_to(root).as_posix(), "slug already exists")
        source = {
            "record_id": record_id,
            "issue_id": candidate["issue_id"],
            "candidate_id": candidate_id,
            "decision_id": decision_id,
        }
        clarification = {
            "source": "promotion",
            "summary": f"created from {candidate_id} and {decision_id}",
            "at": created_at,
        }
        prd = (
            f"# {title.strip()}\n\n"
            "## 问题陈述\n\n"
            f"由 Improvement Candidate `{candidate_id}` 晋级，来源 issue 为 `{candidate['issue_id']}`。\n\n"
            "## 验收标准\n\n"
            "- [ ] 在 Plan 阶段完成该改进的独立需求澄清、设计与最终确认。\n"
        )
        try:
            result = _create_task_unlocked(
                root,
                slug=slug,
                title=title,
                scenario_type="development",
                created_at=created_at,
                extra_meta={"convergence": [f"{candidate_id} effectiveness verification"], "improvement_source": source},
                initial_clarification=clarification,
                initial_prd=prd,
                task_root=active_root,
            )
        except TaskIdentityError as exc:
            raise FlowIssueError(exc.code, exc.path, exc.message) from exc
        return {
            "status": "created",
            "task_id": result["task_id"],
            "path": result["path"],
            "record": result["record"],
            "source": source,
        }


def verdict_path(root: Path, record_id: str, verdict_id: str) -> Path:
    return root / "records" / record_id / "flow-improvements" / "effectiveness" / f"{verdict_id}.json"


def _parse_observed_metrics(values: list[str], expected: list[dict[str, str]]) -> list[dict[str, str]]:
    if not values:
        raise FlowIssueError("OBSERVED_METRIC_MISSING", "--observed-metric", "all frozen metrics are required")
    actual: dict[str, str] = {}
    for raw in values:
        parts = raw.split(":")
        if len(parts) != 2 or not METRIC_NAME.fullmatch(parts[0]):
            raise FlowIssueError("OBSERVED_METRIC_INVALID", "--observed-metric", "use name:value")
        name, value = parts
        if name in actual:
            raise FlowIssueError("OBSERVED_METRIC_DUPLICATE", "--observed-metric", "metric names must be unique")
        actual[name] = _normalized_decimal(value, "--observed-metric")
    expected_names = {item["name"] for item in expected}
    if set(actual) != expected_names:
        raise FlowIssueError("OBSERVED_METRIC_MISMATCH", "--observed-metric", "must cover exactly the frozen metrics")
    return [{"name": name, "value": actual[name]} for name in sorted(actual)]


def _outcome(candidate: dict[str, Any], observed: list[dict[str, str]]) -> str:
    actual = {item["name"]: Decimal(item["value"]) for item in observed}
    metrics = candidate["metrics"]
    if all(actual[item["name"]] <= Decimal(item["target"]) for item in metrics):
        return "improved"
    if any(actual[item["name"]] > Decimal(item["baseline"]) for item in metrics):
        return "regressed"
    return "neutral"


def _create_verified_decision(
    root: Path,
    *,
    record_id: str,
    issue_id: str,
    verdict_id: str,
    verdict_at: str,
) -> dict[str, Any]:
    idempotency_key = f"effectiveness:{verdict_id}:verified"
    value = {
        "schema": "pdca.flow-issue-decision/v1",
        "decision_id": _artifact_id("FD", record_id, idempotency_key),
        "record_id": record_id,
        "issue_id": issue_id,
        "candidate_id": None,
        "idempotency_key": idempotency_key,
        "action": "verified",
        "reason": "all frozen observation metrics met or beat their target",
        "impact": None,
        "authorization": {
            "mode": "effectiveness-verdict",
            "reference": f"{verdict_id}:effectiveness",
            "confirmed_by": "effectiveness-engine",
            "confirmed_at": verdict_at,
        },
        "decided_at": verdict_at,
    }
    path = decision_path(root, record_id, value["decision_id"])
    status = _create_only_json(
        root,
        path,
        value,
        "flow-issue-decision.schema.json",
        "DECISION_CORRUPT",
        "IDEMPOTENCY_CONFLICT",
    )
    return {
        "status": status,
        "artifact_id": value["decision_id"],
        "path": path.relative_to(root).as_posix(),
    }


def _create_rollback_candidate(
    root: Path,
    *,
    candidate: dict[str, Any],
    verdict_id: str,
    verdict_at: str,
) -> dict[str, Any]:
    key = f"effectiveness:{verdict_id}:rollback"
    result = create_candidate(
        root,
        record_id=candidate["record_id"],
        issue_id=candidate["issue_id"],
        event_ids=candidate["event_ids"],
        idempotency_key=key,
        created_at=verdict_at,
        root_cause_hypothesis=f"regression observed after candidate {candidate['candidate_id']}",
        target_component=candidate["target_component"],
        baseline=candidate["baseline"],
        metrics=[
            f"{metric['name']}:{metric['baseline']}:{metric['target']}"
            for metric in candidate["metrics"]
        ],
        risks=[*candidate["risks"], "rollback requires a separate user confirmation"],
        rule_id=candidate["observation_plan"]["rule_id"],
        rule_version=candidate["observation_plan"]["rule_version"],
        min_opportunities=candidate["observation_plan"]["min_opportunities"],
        max_observation_days=candidate["observation_plan"]["max_observation_days"],
        kind="rollback",
        status="pending-confirmation",
        origin_verdict_id=verdict_id,
    )
    return {
        "status": result["status"],
        "artifact_id": result["candidate_id"],
        "path": result["path"],
    }


def verify_effectiveness(
    root: Path,
    *,
    record_id: str,
    candidate_id: str,
    idempotency_key: str,
    deployment_receipt: str,
    deployed_at: str,
    observed_at: str,
    opportunities: int,
    observed_metrics: list[str],
) -> dict[str, Any]:
    record_id = _safe_name(record_id, "--record")
    idempotency_key = _safe_key(idempotency_key, "--idempotency-key")
    if not SAFE_KEY.fullmatch(deployment_receipt):
        raise FlowIssueError("DEPLOYMENT_RECEIPT_INVALID", "--deployment-receipt", "must be a stable reference")
    candidate = load_candidate(root, record_id, candidate_id)
    if candidate["kind"] != "improvement" or candidate["status"] != "dry-run":
        raise FlowIssueError("CANDIDATE_NOT_DEPLOYABLE", "--candidate-id", "only a dry-run improvement candidate can be observed")
    _require_issue(root, candidate["issue_id"], record_id)
    deployed = parse_datetime(deployed_at, "--deployed-at")
    observed = parse_datetime(observed_at, "--observed-at")
    created = parse_datetime(candidate["created_at"], "candidate.created_at")
    if deployed < created:
        raise FlowIssueError("DEPLOYMENT_TIME_INVALID", "--deployed-at", "cannot predate candidate creation")
    if observed < deployed:
        raise FlowIssueError("OBSERVATION_TIME_INVALID", "--observed-at", "cannot predate deployment")
    plan = candidate["observation_plan"]
    if observed - deployed > timedelta(days=plan["max_observation_days"]):
        raise FlowIssueError("OBSERVATION_WINDOW_EXPIRED", "--observed-at", "exceeds the frozen observation window")
    if not plan["min_opportunities"] <= opportunities <= 1_000_000_000:
        raise FlowIssueError("OBSERVATION_INSUFFICIENT", "--opportunities", "does not satisfy the frozen minimum")
    observed_values = _parse_observed_metrics(observed_metrics, candidate["metrics"])
    outcome = _outcome(candidate, observed_values)
    verdict_id = _artifact_id("FV", record_id, idempotency_key)
    if outcome == "improved":
        follow_up = {
            "kind": "verified-decision",
            "artifact_id": _artifact_id("FD", record_id, f"effectiveness:{verdict_id}:verified"),
        }
    elif outcome == "regressed":
        follow_up = {
            "kind": "rollback-candidate",
            "artifact_id": _artifact_id("FC", record_id, f"effectiveness:{verdict_id}:rollback"),
        }
    else:
        follow_up = {"kind": "retriage", "artifact_id": None}
    value = {
        "schema": "pdca.effectiveness-verdict/v1",
        "verdict_id": verdict_id,
        "record_id": record_id,
        "candidate_id": candidate_id,
        "issue_id": candidate["issue_id"],
        "idempotency_key": idempotency_key,
        "deployment": {"receipt": deployment_receipt, "deployed_at": deployed_at},
        "observation": {
            "observed_at": observed_at,
            "opportunities": opportunities,
            "metrics": observed_values,
        },
        "outcome": outcome,
        "follow_up": follow_up,
        "verdict_at": observed_at,
    }
    path = verdict_path(root, record_id, verdict_id)
    status = _create_only_json(
        root,
        path,
        value,
        "effectiveness-verdict.schema.json",
        "VERDICT_CORRUPT",
        "IDEMPOTENCY_CONFLICT",
    )
    if outcome == "improved":
        generated = _create_verified_decision(
            root,
            record_id=record_id,
            issue_id=candidate["issue_id"],
            verdict_id=verdict_id,
            verdict_at=observed_at,
        )
    elif outcome == "regressed":
        generated = _create_rollback_candidate(
            root,
            candidate=candidate,
            verdict_id=verdict_id,
            verdict_at=observed_at,
        )
    else:
        generated = {"artifact_id": None, "path": None}
    return {
        "status": status,
        "verdict_id": verdict_id,
        "path": path.relative_to(root).as_posix(),
        "digest": sha256_bytes(canonical_bytes(value)),
        "verdict": value,
        "follow_up": {"kind": follow_up["kind"], **generated},
    }
