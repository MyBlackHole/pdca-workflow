#!/usr/bin/env python3
"""Strict PDCA validation primitives shared by repository scripts."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

PHASES = ("plan", "do", "check", "act", "archive")
PHASE_STATUS = {
    "plan": ("Pending", True),
    "do": ("InProgress", True),
    "check": ("Completed", True),
    "act": ("Completed", True),
    "archive": ("Completed", False),
}
PROTECTED_PREFIXES = ("records", "knowledge", "pdca/journal")
ACCEPTANCE_HEADING = "## 验收标准"
ACCEPTANCE_CHECKBOX = re.compile(r"^- \[[ xX]\] ")


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def repo_root(explicit: str | Path | None = None) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
    elif os.environ.get("PDCA_HOME"):
        candidate = Path(os.environ["PDCA_HOME"]).expanduser().resolve()
    else:
        candidate = Path(__file__).resolve().parents[1]
    if not (candidate / "flows/flow-plan/SKILL.md").is_file():
        raise ValueError(f"not a PDCA workflow root: {candidate}")
    return candidate


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            text = raw.strip()
            if not text:
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: entry must be an object")
            entries.append(value)
    return entries


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _validator(root: Path, schema_name: str) -> Draft202012Validator:
    schema = load_json(root / "schemas" / schema_name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def schema_issues(root: Path, value: Any, schema_name: str) -> list[Issue]:
    issues: list[Issue] = []
    for error in sorted(_validator(root, schema_name).iter_errors(value), key=lambda item: list(item.path)):
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        issues.append(Issue("SCHEMA_INVALID", pointer or "/", error.message))
    return issues


def _confirmed(entries: Iterable[dict[str, Any]], source: str, responses: set[str]) -> bool:
    return any(entry.get("source") == source and entry.get("response") in responses for entry in entries)


def confirmation_time_issues(task: dict[str, Any], entries: list[dict[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    created_at = datetime.fromisoformat(task["meta"]["created_at"])
    for index, entry in enumerate(entries):
        if entry.get("source") != "final_confirmation":
            continue
        try:
            confirmed_at = datetime.fromisoformat(str(entry["at"]))
        except (KeyError, ValueError):
            continue
        if confirmed_at < created_at:
            issues.append(
                Issue(
                    "FINAL_CONFIRMATION_TIME_ORDER",
                    f"clarifications.jsonl[{index}]/at",
                    "final confirmation cannot predate task creation",
                )
            )
    return issues


def clarification_issues(root: Path, task_dir: Path) -> tuple[list[dict[str, Any]], list[Issue]]:
    path = task_dir / "clarifications.jsonl"
    if not path.is_file():
        return [], [Issue("CLARIFICATIONS_MISSING", "clarifications.jsonl", "file is required")]
    try:
        entries = load_jsonl(path)
    except ValueError as exc:
        return [], [Issue("CLARIFICATIONS_INVALID", "clarifications.jsonl", str(exc))]
    issues: list[Issue] = []
    for index, entry in enumerate(entries):
        for issue in schema_issues(root, entry, "clarification.schema.json"):
            issues.append(Issue(issue.code, f"clarifications.jsonl[{index}]{issue.path}", issue.message))
    return entries, issues


def evidence_issues(root: Path, task: dict[str, Any]) -> list[Issue]:
    record_id = task.get("meta", {}).get("record")
    if not record_id:
        return [Issue("RECORD_MISSING", "/meta/record", "record is required after Do")]
    record_dir = (root / "records" / record_id).resolve()
    records_root = (root / "records").resolve()
    if record_dir.parent != records_root:
        return [Issue("RECORD_PATH_INVALID", "/meta/record", "record must be a direct child of records/")]
    manifest = record_dir / "evidence" / "manifest.jsonl"
    if not manifest.is_file():
        return [Issue("EVIDENCE_MANIFEST_MISSING", str(manifest.relative_to(root)), "manifest is required")]
    try:
        entries = load_jsonl(manifest)
    except ValueError as exc:
        return [Issue("EVIDENCE_MANIFEST_INVALID", str(manifest.relative_to(root)), str(exc))]
    if not entries:
        return [Issue("EVIDENCE_EMPTY", str(manifest.relative_to(root)), "manifest must contain entries")]
    issues: list[Issue] = []
    for index, entry in enumerate(entries):
        for issue in schema_issues(root, entry, "evidence-entry.schema.json"):
            issues.append(Issue(issue.code, f"{manifest.relative_to(root)}[{index}]{issue.path}", issue.message))
        evidence_dir = (record_dir / "evidence").resolve()
        artifact = (evidence_dir / str(entry.get("file", ""))).resolve()
        try:
            artifact.relative_to(evidence_dir)
        except ValueError:
            issues.append(
                Issue(
                    "EVIDENCE_PATH_ESCAPE",
                    f"{manifest.relative_to(root)}[{index}]/file",
                    "artifact must stay inside the record evidence directory",
                )
            )
            continue
        if not artifact.is_file():
            issues.append(Issue("EVIDENCE_FILE_MISSING", str(artifact), "artifact is missing"))
            continue
        expected_size = entry.get("size")
        if isinstance(expected_size, int) and artifact.stat().st_size != expected_size:
            issues.append(Issue("EVIDENCE_SIZE_MISMATCH", str(artifact.relative_to(root)), "size does not match manifest"))
        expected_digest = entry.get("digest")
        if isinstance(expected_digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", expected_digest):
            if sha256_file(artifact) != expected_digest:
                issues.append(Issue("EVIDENCE_DIGEST_MISMATCH", str(artifact.relative_to(root)), "digest does not match"))
    return issues


def acceptance_criteria(task_dir: Path) -> tuple[list[str], list[Issue]]:
    prd = task_dir / "prd.md"
    if not prd.is_file():
        return [], [Issue("ACCEPTANCE_CRITERIA_MISSING", "prd.md", "canonical acceptance section is required")]
    in_section = False
    criteria: list[str] = []
    for line in prd.read_text(encoding="utf-8").splitlines():
        if line == ACCEPTANCE_HEADING:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and ACCEPTANCE_CHECKBOX.match(line):
            criteria.append(f"AC-{len(criteria) + 1}")
    if not criteria:
        return [], [
            Issue(
                "ACCEPTANCE_CRITERIA_MISSING",
                "prd.md",
                f"{ACCEPTANCE_HEADING} must contain Markdown checkboxes",
            )
        ]
    return criteria, []


def convergence_issues(root: Path, task_dir: Path) -> list[Issue]:
    task = load_json(task_dir / "task.json")
    criteria, issues = acceptance_criteria(task_dir)
    record_id = task.get("meta", {}).get("record")
    if not record_id:
        return issues + [Issue("CONVERGENCE_MAP_MISSING", "/meta/record", "record is required")]
    evidence_dir = root / "records" / str(record_id) / "evidence"
    manifest_path = evidence_dir / "manifest.jsonl"
    if not manifest_path.is_file():
        return issues + [
            Issue("CONVERGENCE_MAP_MISSING", str(manifest_path), "registered convergence map is required")
        ]
    try:
        entries = load_jsonl(manifest_path)
    except ValueError as exc:
        return issues + [Issue("CONVERGENCE_MAP_INVALID", str(manifest_path), str(exc))]

    map_entries = [
        entry
        for entry in entries
        if entry.get("id") == "convergence-map" and entry.get("kind") == "convergence-map"
    ]
    if len(map_entries) != 1:
        issues.append(
            Issue(
                "CONVERGENCE_MAP_MISSING",
                str(manifest_path.relative_to(root)),
                "exactly one entry with id and kind convergence-map is required",
            )
        )
        return issues

    support_entries = [
        entry
        for entry in entries
        if entry.get("id") != "convergence-map" and entry.get("kind") != "convergence-map"
    ]
    support_by_id = {str(entry.get("id")): entry for entry in support_entries}
    for criterion in criteria:
        if not any(criterion in entry.get("criteria", []) for entry in support_entries):
            issues.append(
                Issue(
                    "ACCEPTANCE_CRITERION_UNCOVERED",
                    criterion,
                    "criterion must be covered by non-map evidence",
                )
            )

    map_entry = map_entries[0]
    map_path = (evidence_dir / str(map_entry.get("file", ""))).resolve()
    try:
        map_path.relative_to(evidence_dir.resolve())
        mapping = load_json(map_path)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        issues.append(Issue("CONVERGENCE_MAP_INVALID", str(map_path), str(exc)))
        return issues
    map_schema_issues = schema_issues(root, mapping, "convergence.schema.json")
    if map_schema_issues:
        issues.extend(
            Issue("CONVERGENCE_MAP_INVALID", f"{map_path}[{issue.path}]", issue.message)
            for issue in map_schema_issues
        )
        return issues

    items_by_index: dict[int, list[dict[str, Any]]] = {}
    task_convergence = task["meta"]["convergence"]
    for item in mapping["items"]:
        index = item["index"]
        items_by_index.setdefault(index, []).append(item)
        if index > len(task_convergence):
            issues.append(
                Issue("CONVERGENCE_ITEM_UNKNOWN", f"{map_path}[{index}]", "index is outside task convergence")
            )

    known_criteria = set(criteria)
    for index, text in enumerate(task_convergence, 1):
        matches = items_by_index.get(index, [])
        if not matches:
            issues.append(
                Issue("CONVERGENCE_ITEM_MISSING", f"/meta/convergence/{index - 1}", "mapping item is required")
            )
            continue
        if len(matches) > 1:
            issues.append(
                Issue("CONVERGENCE_ITEM_DUPLICATE", f"{map_path}[{index}]", "index must occur exactly once")
            )
            continue
        item = matches[0]
        if item["text"] != text:
            issues.append(
                Issue(
                    "CONVERGENCE_TEXT_MISMATCH",
                    f"{map_path}[{index}]/text",
                    "text must equal the Plan convergence value",
                )
            )
        for criterion in item["criteria"]:
            if criterion not in known_criteria:
                issues.append(
                    Issue(
                        "CONVERGENCE_CRITERION_UNKNOWN",
                        f"{map_path}[{index}]/criteria",
                        f"{criterion} is not defined by the PRD",
                    )
                )
                continue
            cited_entries = [
                support_by_id[evidence_id]
                for evidence_id in item["evidence_ids"]
                if evidence_id in support_by_id
            ]
            if not any(criterion in entry.get("criteria", []) for entry in cited_entries):
                issues.append(
                    Issue(
                        "CONVERGENCE_SUPPORT_MISSING",
                        f"{map_path}[{index}]",
                        f"listed evidence does not support {criterion}",
                    )
                )
        for evidence_id in item["evidence_ids"]:
            if evidence_id not in support_by_id:
                issues.append(
                    Issue(
                        "CONVERGENCE_EVIDENCE_UNKNOWN",
                        f"{map_path}[{index}]/evidence_ids",
                        f"{evidence_id} is not registered support evidence",
                    )
                )
    return issues


def task_issues(root: Path, task_dir: Path, include_phase_requirements: bool = True) -> list[Issue]:
    task_path = task_dir / "task.json"
    if not task_path.is_file():
        return [Issue("TASK_MISSING", "task.json", "file is required")]
    try:
        task = load_json(task_path)
    except (json.JSONDecodeError, OSError) as exc:
        return [Issue("TASK_INVALID_JSON", "task.json", str(exc))]
    issues = schema_issues(root, task, "task.schema.json")
    if issues:
        return issues

    phase = task["meta"]["phase"]
    expected_status, expected_active = PHASE_STATUS[phase]
    if task["status"] != expected_status:
        issues.append(Issue("STATUS_PHASE_MISMATCH", "/status", f"{phase} requires {expected_status}"))
    if task["meta"]["active"] is not expected_active:
        issues.append(Issue("ACTIVE_PHASE_MISMATCH", "/meta/active", f"{phase} requires active={expected_active}"))

    states = task["states"]
    current_index = PHASES.index(phase)
    for index, state_name in enumerate(PHASES):
        value = states[state_name]
        if index <= current_index and value is None:
            issues.append(Issue("STATE_TIMESTAMP_MISSING", f"/states/{state_name}", f"required in {phase}"))
        if index > current_index and value is not None:
            issues.append(Issue("FUTURE_STATE_SET", f"/states/{state_name}", f"must be null in {phase}"))

    ordered_values = [states[name] for name in PHASES[: current_index + 1]]
    parsed: list[datetime] = []
    try:
        parsed = [datetime.fromisoformat(value) for value in ordered_values if value is not None]
    except ValueError as exc:
        issues.append(Issue("STATE_TIME_INVALID", "/states", str(exc)))
    if parsed and parsed != sorted(parsed):
        issues.append(Issue("STATE_TIME_ORDER", "/states", "timestamps must be nondecreasing"))

    if not include_phase_requirements:
        return issues

    entries, clarification_errors = clarification_issues(root, task_dir)
    issues.extend(clarification_errors)
    issues.extend(confirmation_time_issues(task, entries))
    if current_index >= PHASES.index("do") and not _confirmed(entries, "final_confirmation", {"confirmed"}):
        issues.append(Issue("FINAL_CONFIRMATION_MISSING", "clarifications.jsonl", "confirmed response is required"))
    if current_index >= PHASES.index("check"):
        issues.extend(evidence_issues(root, task))
    if current_index >= PHASES.index("act"):
        record_id = task["meta"].get("record")
        conclusion = root / "records" / str(record_id) / "conclusion.md"
        if not conclusion.is_file():
            issues.append(Issue("CONCLUSION_MISSING", str(conclusion.relative_to(root)), "conclusion is required"))
        if "verdict" not in task["meta"]:
            issues.append(Issue("VERDICT_MISSING", "/meta/verdict", "verdict is required"))
        if not _confirmed(entries, "check_confirmation", {"confirmed", "rejected", "partial"}):
            issues.append(Issue("CHECK_CONFIRMATION_MISSING", "clarifications.jsonl", "check confirmation is required"))
    if phase == "archive" and "disposition" not in task["meta"]:
        issues.append(Issue("DISPOSITION_MISSING", "/meta/disposition", "disposition is required"))
    return issues


def gate_issues(root: Path, task_dir: Path) -> tuple[str | None, list[Issue]]:
    base = task_issues(root, task_dir, include_phase_requirements=False)
    if base:
        return None, base
    task = load_json(task_dir / "task.json")
    phase = task["meta"]["phase"]
    entries, issues = clarification_issues(root, task_dir)
    issues.extend(confirmation_time_issues(task, entries))
    if phase == "plan":
        if not _confirmed(entries, "final_confirmation", {"confirmed"}):
            issues.append(Issue("FINAL_CONFIRMATION_MISSING", "clarifications.jsonl", "confirmed response is required"))
    elif phase == "do":
        if not (task_dir / "prd.md").is_file():
            issues.append(Issue("PRD_MISSING", "prd.md", "PRD is required"))
        issues.extend(evidence_issues(root, task))
        issues.extend(convergence_issues(root, task_dir))
    elif phase == "check":
        record_id = task["meta"].get("record")
        conclusion = root / "records" / str(record_id) / "conclusion.md"
        if not conclusion.is_file():
            issues.append(Issue("CONCLUSION_MISSING", str(conclusion.relative_to(root)), "conclusion is required"))
        if "verdict" not in task["meta"]:
            issues.append(Issue("VERDICT_MISSING", "/meta/verdict", "verdict is required"))
        if not _confirmed(entries, "check_confirmation", {"confirmed", "rejected", "partial"}):
            issues.append(Issue("CHECK_CONFIRMATION_MISSING", "clarifications.jsonl", "check confirmation is required"))
    elif phase == "act":
        if "disposition" not in task["meta"]:
            issues.append(Issue("DISPOSITION_MISSING", "/meta/disposition", "disposition is required"))
    elif phase == "archive":
        issues.extend(task_issues(root, task_dir, include_phase_requirements=True))
    return phase, issues


def path_is_protected(root: Path, target: Path) -> bool:
    relative = target.resolve().relative_to(root.resolve()).as_posix()
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in PROTECTED_PREFIXES)
