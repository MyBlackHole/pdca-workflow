from __future__ import annotations

import fcntl
import json
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import yaml

from .errors import RuntimeContractError
from .io import (
    atomic_write_json,
    atomic_write_text,
    confined_path,
    digest_file,
    digest_value,
    load_json,
    relative_path,
    validate_schema,
)
from .projection import verify_projection_manifest
from .task import ExecutableTask, load_executable_task


RECEIPTS_FILE = "agent-execution-receipts.jsonl"
LOCK_FILE = ".pdca-runtime.lock"
USER_CONFIRMATION_SOURCES = {
    "final_confirmation",
    "check_confirmation",
    "direction_confirm",
    "fix_confirmation",
    "user_decision",
}


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@contextmanager
def _task_lock(task_dir: Path) -> Iterator[None]:
    if not task_dir.is_dir():
        raise RuntimeContractError("TASK_SCOPE_INVALID", str(task_dir), "current task directory must already exist")
    with (task_dir / LOCK_FILE).open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_receipts(task: ExecutableTask) -> list[dict[str, Any]]:
    path = task.task_dir / RECEIPTS_FILE
    if not path.is_file():
        return []
    receipts: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeContractError("RECEIPT_LOG_INVALID", RECEIPTS_FILE, "receipt log is unreadable") from exc
    previous: str | None = None
    for index, line in enumerate(lines):
        if not line.strip():
            raise RuntimeContractError("RECEIPT_LOG_INVALID", f"{RECEIPTS_FILE}:{index + 1}", "blank receipt line")
        try:
            receipt = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeContractError("RECEIPT_LOG_INVALID", f"{RECEIPTS_FILE}:{index + 1}", "invalid JSON receipt") from exc
        validate_schema(task.root, receipt, "agent-execution-receipt.schema.json", "RECEIPT_SCHEMA_INVALID")
        if receipt["sequence"] != index + 1 or receipt["previous_receipt_digest"] != previous:
            raise RuntimeContractError("RECEIPT_CHAIN_INVALID", f"{RECEIPTS_FILE}:{index + 1}", "sequence or previous digest mismatch")
        expected = digest_value({key: value for key, value in receipt.items() if key != "receipt_digest"})
        if receipt["receipt_digest"] != expected:
            raise RuntimeContractError("RECEIPT_DIGEST_MISMATCH", f"{RECEIPTS_FILE}:{index + 1}", "receipt was modified")
        if receipt["task_id"] != task.task_id:
            raise RuntimeContractError("RECEIPT_TASK_MISMATCH", f"{RECEIPTS_FILE}:{index + 1}", "receipt belongs to another task")
        receipts.append(receipt)
        previous = receipt["receipt_digest"]
    return receipts


def _append_events(task: ExecutableTask, receipts: list[dict[str, Any]], events: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    previous = receipts[-1]["receipt_digest"] if receipts else None
    appended: list[dict[str, Any]] = []
    for event, payload in events:
        receipt = {
            "schema": "pdca.agent-execution-receipt/v1",
            "sequence": len(receipts) + len(appended) + 1,
            "previous_receipt_digest": previous,
            "recorded_at": _now(),
            "task_id": task.task_id,
            "event": event,
            "payload": payload,
        }
        receipt["receipt_digest"] = digest_value(receipt)
        validate_schema(task.root, receipt, "agent-execution-receipt.schema.json", "RECEIPT_SCHEMA_INVALID")
        appended.append(receipt)
        previous = receipt["receipt_digest"]
    all_receipts = [*receipts, *appended]
    atomic_write_text(
        task.task_dir / RECEIPTS_FILE,
        "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in all_receipts),
    )
    return appended


def derive_execution_state(receipts: list[dict[str, Any]]) -> str:
    state = "undispatched"
    transitions = {
        "undispatched": {"dispatch_requested": "dispatch_pending"},
        "dispatch_pending": {"agent_bound": "suspended_waiting_agent"},
        "suspended_waiting_agent": {
            "agent_awaiting_confirmation": "awaiting_confirmation",
            "agent_completed": "awaiting_conformance_verification",
            "agent_failed": "failed",
        },
        "awaiting_confirmation": {
            "user_confirmation_recorded": "suspended_waiting_agent",
            "agent_failed": "failed",
        },
        "awaiting_conformance_verification": {
            "conformance_verified": "completed",
            "conformance_failed": "failed",
        },
        "failed": {},
        "completed": {},
    }
    for index, receipt in enumerate(receipts):
        event = receipt["event"]
        if event not in transitions[state]:
            raise RuntimeContractError(
                "RECEIPT_STATE_INVALID",
                f"/events/{index}",
                f"event {event} is invalid while state is {state}",
            )
        state = transitions[state][event]
    return state


def _validate_scoped_context_path(task: ExecutableTask, relative: str) -> None:
    if "__pycache__" in Path(relative).parts or relative.endswith((".pyc", ".pyo")):
        raise RuntimeContractError("CACHE_ARTIFACT_FORBIDDEN", relative, "generated cache files are not context inputs")
    if relative.startswith("pdca/tasks/archive/"):
        raise RuntimeContractError("CROSS_TASK_CONTEXT_FORBIDDEN", relative, "archived task context is forbidden")
    if relative.startswith("pdca/tasks/") and not relative.startswith(task.relative_dir + "/"):
        raise RuntimeContractError("CROSS_TASK_CONTEXT_FORBIDDEN", relative, "context cannot include another task")
    if relative.startswith("records/") and not relative.startswith(f"records/{task.record_id}/"):
        raise RuntimeContractError("CROSS_TASK_CONTEXT_FORBIDDEN", relative, "context cannot include another task record")
    if relative.startswith(task.relative_dir + "/") or relative.startswith(f"records/{task.record_id}/"):
        return
    authority_files = {"AGENTS.md", "SKILLS-INDEX.md", "pdca/CONTEXT.md"}
    authority_roots = ("ontology/", "config/", "schemas/", "pdca_runtime/", "scripts/", "tests/")
    if relative not in authority_files and not relative.startswith(authority_roots):
        raise RuntimeContractError(
            "CONTEXT_PATH_SCOPE_INVALID",
            relative,
            "context paths must be current-task persistence or an explicit repository authority/source input",
        )


def build_context_manifest(task: ExecutableTask, paths: list[str]) -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for value in paths:
        path = confined_path(task.root, value)
        relative = relative_path(task.root, path)
        if relative in seen:
            raise RuntimeContractError("CONTEXT_PATH_DUPLICATE", relative, "context path is duplicated")
        seen.add(relative)
        _validate_scoped_context_path(task, relative)
        entries.append({"path": relative, "digest": digest_file(path)})
    manifest: dict[str, Any] = {
        "schema": "pdca.agent-context-manifest/v1",
        "task_id": task.task_id,
        "files": sorted(entries, key=lambda item: item["path"]),
    }
    manifest["digest"] = digest_value(manifest)
    validate_schema(task.root, manifest, "agent-context-manifest.schema.json", "CONTEXT_MANIFEST_INVALID")
    _verify_context_manifest(task, manifest)
    return manifest


def _verify_context_manifest(task: ExecutableTask, context: dict[str, Any]) -> None:
    validate_schema(task.root, context, "agent-context-manifest.schema.json", "CONTEXT_MANIFEST_INVALID")
    if context["task_id"] != task.task_id:
        raise RuntimeContractError("CONTEXT_TASK_MISMATCH", "/task_id", "context belongs to another task")
    expected_digest = digest_value({key: value for key, value in context.items() if key != "digest"})
    if context["digest"] != expected_digest:
        raise RuntimeContractError("CONTEXT_DIGEST_MISMATCH", "/digest", "context manifest was modified")
    required = {f"{task.relative_dir}/task.json", f"{task.relative_dir}/prd.md"}
    observed = {item["path"] for item in context["files"]}
    if not required.issubset(observed):
        raise RuntimeContractError("CONTEXT_REQUIRED_INPUT_MISSING", "/files", "context must bind current task.json and prd.md")
    for item in context["files"]:
        path = confined_path(task.root, item["path"])
        canonical = relative_path(task.root, path)
        if canonical != item["path"]:
            raise RuntimeContractError("CONTEXT_PATH_INVALID", item["path"], "context paths must be canonical")
        _validate_scoped_context_path(task, canonical)
        if digest_file(path) != item["digest"]:
            raise RuntimeContractError("CONTEXT_FILE_DRIFT", canonical, "context input changed after manifest creation")


def _load_capabilities(root: Path) -> dict[str, Any]:
    path = root / "config" / "capabilities.yaml"
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeContractError("CAPABILITY_CONFIG_INVALID", str(path), "capability config is required") from exc
    try:
        spawn = value["capabilities"]["agent.spawn"]
    except (KeyError, TypeError) as exc:
        raise RuntimeContractError("SPAWN_CAPABILITY_MISSING", "config/capabilities.yaml", "agent.spawn capability is required") from exc
    if spawn.get("required") is not True or "fallback" in spawn:
        raise RuntimeContractError("SPAWN_CAPABILITY_INVALID", "config/capabilities.yaml", "agent.spawn must be required and have no fallback")
    return spawn


def prepare_dispatch_request(
    task: ExecutableTask,
    projection_manifest: dict[str, Any] | Path,
    context_manifest: dict[str, Any] | Path,
    *,
    spawn_status: str,
) -> dict[str, Any]:
    _load_capabilities(task.root)
    if spawn_status != "available":
        raise RuntimeContractError("SPAWN_CAPABILITY_MISSING", "agent.spawn", "platform Adapter must report agent.spawn available")
    projection = load_json(projection_manifest, "PROJECTION_INVALID") if isinstance(projection_manifest, Path) else projection_manifest
    context = load_json(context_manifest, "CONTEXT_MANIFEST_INVALID") if isinstance(context_manifest, Path) else context_manifest
    verify_projection_manifest(task, projection)
    _verify_context_manifest(task, context)
    request: dict[str, Any] = {
        "schema": "pdca.agent-dispatch-request/v1",
        "task_id": task.task_id,
        "expected_state": "undispatched",
        "ontology_role": task.ontology_role,
        "execution_contract_digest": task.execution_contract_digest,
        "projection_manifest_digest": projection["digest"],
        "context_manifest_digest": context["digest"],
        "fresh_context_required": True,
        "created_at": _now(),
    }
    request["request_digest"] = digest_value(request)
    validate_schema(task.root, request, "agent-dispatch-request.schema.json", "DISPATCH_REQUEST_INVALID")
    return request


def _validate_dispatch_request(task: ExecutableTask, request: dict[str, Any], projection: dict[str, Any], context: dict[str, Any]) -> None:
    validate_schema(task.root, request, "agent-dispatch-request.schema.json", "DISPATCH_REQUEST_INVALID")
    expected = digest_value({key: value for key, value in request.items() if key != "request_digest"})
    if request["request_digest"] != expected:
        raise RuntimeContractError("DISPATCH_REQUEST_DIGEST_MISMATCH", "/request_digest", "dispatch request was modified")
    expected_fields = {
        "task_id": task.task_id,
        "ontology_role": task.ontology_role,
        "execution_contract_digest": task.execution_contract_digest,
        "projection_manifest_digest": projection["digest"],
        "context_manifest_digest": context["digest"],
    }
    for field, expected_value in expected_fields.items():
        if request[field] != expected_value:
            raise RuntimeContractError("DISPATCH_REQUEST_STALE", f"/{field}", "dispatch request no longer matches current task inputs")


def bind_agent(
    root: Path,
    task_dir: Path,
    request: dict[str, Any],
    adapter_receipt: dict[str, Any],
    projection_manifest: dict[str, Any] | Path,
    context_manifest: dict[str, Any] | Path,
) -> dict[str, Any]:
    load_executable_task(root, task_dir)
    with _task_lock(task_dir):
        task = load_executable_task(root, task_dir)
        receipts = _load_receipts(task)
        if derive_execution_state(receipts) != "undispatched":
            raise RuntimeContractError("DISPATCH_CAS_REJECTED", "/expected_state", "task was already dispatched")
        projection = load_json(projection_manifest, "PROJECTION_INVALID") if isinstance(projection_manifest, Path) else projection_manifest
        context = load_json(context_manifest, "CONTEXT_MANIFEST_INVALID") if isinstance(context_manifest, Path) else context_manifest
        verify_projection_manifest(task, projection)
        _verify_context_manifest(task, context)
        _validate_dispatch_request(task, request, projection, context)
        if adapter_receipt.get("task_id") != task.task_id or adapter_receipt.get("request_digest") != request["request_digest"]:
            raise RuntimeContractError("ADAPTER_RECEIPT_MISMATCH", "/adapter_receipt", "Adapter receipt does not bind this request")
        agent_id = adapter_receipt.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise RuntimeContractError("ADAPTER_AGENT_ID_MISSING", "/adapter_receipt/agent_id", "Adapter must return a non-empty agent id")
        if adapter_receipt.get("fresh_context") is not True or adapter_receipt.get("fork_context") is not False:
            raise RuntimeContractError("ADAPTER_CONTEXT_NOT_FRESH", "/adapter_receipt/fresh_context", "Adapter must attest fresh_context=true and fork_context=false")
        adapter = adapter_receipt.get("adapter")
        if not isinstance(adapter, str) or not adapter.strip():
            raise RuntimeContractError("ADAPTER_ID_MISSING", "/adapter_receipt/adapter", "Adapter id is required")
        appended = _append_events(
            task,
            receipts,
            [
                ("dispatch_requested", {"request_digest": request["request_digest"], "request": request}),
                (
                    "agent_bound",
                    {
                        "request_digest": request["request_digest"],
                        "agent_id": agent_id,
                        "adapter": adapter,
                        "fresh_context": True,
                        "fork_context": False,
                        "ontology_role": task.ontology_role,
                        "execution_contract_digest": task.execution_contract_digest,
                        "projection_manifest_digest": projection["digest"],
                        "context_manifest_digest": context["digest"],
                    },
                ),
            ],
        )
        return {"status": "suspended_waiting_agent", "binding_receipt": appended[-1]}


def _bound_identity(receipts: list[dict[str, Any]]) -> tuple[str, str]:
    if len(receipts) < 2 or receipts[1]["event"] != "agent_bound":
        raise RuntimeContractError("AGENT_BINDING_MISSING", "/receipts", "bound Agent receipt is required")
    bound = receipts[1]["payload"]
    return bound["agent_id"], bound["request_digest"]


def _binding(receipts: list[dict[str, Any]]) -> tuple[str, str]:
    if derive_execution_state(receipts) != "suspended_waiting_agent":
        raise RuntimeContractError("AGENT_RESULT_STATE_INVALID", "/state", "task is not waiting for its bound agent")
    return _bound_identity(receipts)


def _clarification_entries(task: ExecutableTask) -> tuple[Path, list[dict[str, Any]]]:
    path = task.task_dir / "clarifications.jsonl"
    if not path.is_file():
        return path, []
    entries: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            raise RuntimeContractError("CLARIFICATION_LOG_INVALID", f"clarifications.jsonl:{index + 1}", "blank clarification line")
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeContractError("CLARIFICATION_LOG_INVALID", f"clarifications.jsonl:{index + 1}", "invalid JSONL") from exc
        validate_schema(task.root, entry, "clarification.schema.json", "CLARIFICATION_LOG_INVALID")
        entries.append(entry)
    return path, entries


def _verify_recorded_confirmations(task: ExecutableTask, receipts: list[dict[str, Any]]) -> None:
    recorded = [receipt for receipt in receipts if receipt["event"] == "user_confirmation_recorded"]
    if not recorded:
        return
    _, entries = _clarification_entries(task)
    for receipt in recorded:
        payload = receipt["payload"]
        index = payload["clarification_index"]
        if index > len(entries) or digest_value(entries[index - 1]) != payload["clarification_digest"]:
            raise RuntimeContractError(
                "CLARIFICATION_DRIFT",
                f"clarifications.jsonl:{index}",
                "recorded user confirmation no longer matches current-task persistence",
            )


def _allowed_result_artifact(task: ExecutableTask, relative: str) -> Path:
    path = confined_path(task.root, relative)
    canonical = relative_path(task.root, path)
    if canonical != relative:
        raise RuntimeContractError("RESULT_PATH_INVALID", relative, "result paths must be canonical")
    task_scoped = canonical.startswith(task.relative_dir + "/")
    record_scoped = canonical.startswith(f"records/{task.record_id}/")
    if not task_scoped and not record_scoped:
        raise RuntimeContractError(
            "CROSS_TASK_ARTIFACT_FORBIDDEN",
            canonical,
            "result artifacts must stay inside the current task or its evidence record",
        )
    return path


def record_agent_result(
    root: Path,
    task_dir: Path,
    *,
    status: str,
    agent_id: str,
    request_digest: str,
    artifacts: list[str] | None = None,
    evidence_manifest: str | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    event_by_status = {
        "completed": "agent_completed",
        "failed": "agent_failed",
        "awaiting_confirmation": "agent_awaiting_confirmation",
    }
    if status not in event_by_status:
        raise RuntimeContractError("AGENT_RESULT_INVALID", "/status", "unsupported agent result status")
    load_executable_task(root, task_dir)
    with _task_lock(task_dir):
        task = load_executable_task(root, task_dir)
        receipts = _load_receipts(task)
        expected_agent, expected_request = _binding(receipts)
        _verify_recorded_confirmations(task, receipts)
        if agent_id != expected_agent or request_digest != expected_request:
            raise RuntimeContractError("AGENT_RESULT_BINDING_MISMATCH", "/agent_id", "result does not belong to the bound agent and request")
        payload: dict[str, Any] = {"agent_id": agent_id, "request_digest": request_digest}
        if status == "completed":
            if not artifacts or not evidence_manifest:
                raise RuntimeContractError("AGENT_RESULT_INCOMPLETE", "/artifacts", "completion requires artifacts and evidence manifest")
            artifact_entries = []
            observed_artifacts: set[str] = set()
            for relative in artifacts:
                if relative in observed_artifacts:
                    raise RuntimeContractError("RESULT_ARTIFACT_DUPLICATE", relative, "result artifact is duplicated")
                observed_artifacts.add(relative)
                path = _allowed_result_artifact(task, relative)
                artifact_entries.append({"path": relative, "digest": digest_file(path)})
            evidence_path = _allowed_result_artifact(task, evidence_manifest)
            expected_manifest = f"records/{task.record_id}/evidence/manifest.jsonl"
            if relative_path(task.root, evidence_path) != expected_manifest:
                raise RuntimeContractError("EVIDENCE_MANIFEST_SCOPE_INVALID", evidence_manifest, "completion must bind the current task evidence manifest")
            payload.update(
                {
                    "artifacts": sorted(artifact_entries, key=lambda item: item["path"]),
                    "evidence_manifest": expected_manifest,
                    "evidence_manifest_digest": digest_file(evidence_path),
                }
            )
        else:
            if not isinstance(message, str) or not message.strip():
                raise RuntimeContractError("AGENT_RESULT_INCOMPLETE", "/message", "failure or confirmation request requires a message")
            payload["message"] = message
            if status == "awaiting_confirmation":
                _, clarification_entries = _clarification_entries(task)
                payload["clarification_count_before"] = len(clarification_entries)
                payload["clarifications_digest_before"] = digest_value(clarification_entries)
        appended = _append_events(task, receipts, [(event_by_status[status], payload)])
        return {"status": derive_execution_state([*receipts, *appended]), "receipt": appended[0]}


def record_user_confirmation(
    root: Path,
    task_dir: Path,
    *,
    clarification_digest: str,
) -> dict[str, Any]:
    """Bind a newly persisted user response and make the same Agent resume-ready."""

    load_executable_task(root, task_dir)
    with _task_lock(task_dir):
        task = load_executable_task(root, task_dir)
        receipts = _load_receipts(task)
        if derive_execution_state(receipts) != "awaiting_confirmation":
            raise RuntimeContractError("CONFIRMATION_STATE_INVALID", "/state", "an unresolved Agent confirmation request is required")
        request_receipt = receipts[-1]
        request_payload = request_receipt["payload"]
        path, entries = _clarification_entries(task)
        before_count = request_payload["clarification_count_before"]
        before_entries = entries[:before_count]
        if len(entries) <= before_count:
            raise RuntimeContractError("USER_CONFIRMATION_MISSING", "clarifications.jsonl", "a new current-task clarification entry is required")
        if digest_value(before_entries) != request_payload["clarifications_digest_before"]:
            raise RuntimeContractError("CLARIFICATION_PREFIX_DRIFT", "clarifications.jsonl", "clarifications preceding the request changed")
        matches = [
            (index, entry)
            for index, entry in enumerate(entries[before_count:], start=before_count + 1)
            if digest_value(entry) == clarification_digest
        ]
        if len(matches) != 1:
            raise RuntimeContractError("USER_CONFIRMATION_DIGEST_INVALID", "/clarification_digest", "digest must identify one new clarification entry")
        index, entry = matches[0]
        if entry.get("source") not in USER_CONFIRMATION_SOURCES or entry.get("response") not in {
            "confirmed",
            "rejected",
            "partial",
        }:
            raise RuntimeContractError(
                "USER_CONFIRMATION_ENTRY_INVALID",
                f"clarifications.jsonl:{index}",
                "bound clarification must be an explicit user confirmation response",
            )
        agent_id, request_digest = _bound_identity(receipts)
        payload = {
            "agent_id": agent_id,
            "request_digest": request_digest,
            "recorded_by": "coordinator",
            "clarifications_path": relative_path(task.root, path),
            "clarifications_file_digest": digest_file(path),
            "clarification_index": index,
            "clarification_digest": clarification_digest,
            "clarification": entry,
        }
        appended = _append_events(task, receipts, [("user_confirmation_recorded", payload)])
        return {"status": derive_execution_state([*receipts, *appended]), "receipt": appended[0]}


def _acceptance_criteria(prd_text: str) -> list[str]:
    return sorted(set(re.findall(r"(?m)^\s*- \[[ xX]\]\s+(AC-[1-9][0-9]*)\s*:", prd_text)))


def _evidence_coverage(task: ExecutableTask, manifest_path: Path) -> tuple[str, list[str], list[dict[str, Any]]]:
    if not manifest_path.is_file():
        raise RuntimeContractError("EVIDENCE_MANIFEST_MISSING", relative_path(task.root, manifest_path), "current task evidence manifest is required")
    entries: list[dict[str, Any]] = []
    for index, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines()):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeContractError("EVIDENCE_MANIFEST_INVALID", f"{manifest_path}:{index + 1}", "invalid JSONL") from exc
        validate_schema(task.root, entry, "evidence-entry.schema.json", "EVIDENCE_MANIFEST_INVALID")
        evidence_file = (manifest_path.parent / str(entry["file"])).resolve()
        try:
            evidence_file.relative_to(manifest_path.parent.resolve())
        except ValueError as exc:
            raise RuntimeContractError("EVIDENCE_PATH_ESCAPE", str(entry["file"]), "evidence must stay in the current record") from exc
        if not evidence_file.is_file():
            raise RuntimeContractError("EVIDENCE_FILE_MISSING", str(entry["file"]), "registered evidence file is missing")
        if evidence_file.stat().st_size != entry["size"] or digest_file(evidence_file) != entry["digest"]:
            raise RuntimeContractError("EVIDENCE_INTEGRITY_MISMATCH", str(entry["file"]), "registered evidence metadata does not match the file")
        if not entry.get("superseded_by"):
            entries.append(entry)
    criteria = _acceptance_criteria((task.task_dir / "prd.md").read_text(encoding="utf-8"))
    supporting = [entry for entry in entries if entry.get("kind") != "convergence-map"]
    uncovered = [criterion for criterion in criteria if not any(criterion in entry.get("criteria", []) for entry in supporting)]
    return digest_file(manifest_path), uncovered, entries


def resume_for_conformance(root: Path, task_dir: Path) -> dict[str, Any]:
    """Resume from current-task persistence only; no relationship field is followed."""

    load_executable_task(root, task_dir)
    with _task_lock(task_dir):
        task = load_executable_task(root, task_dir)
        receipts = _load_receipts(task)
        if derive_execution_state(receipts) != "awaiting_conformance_verification":
            raise RuntimeContractError("RESUME_STATE_INVALID", "/state", "a completed agent receipt is required")
        _verify_recorded_confirmations(task, receipts)
        completion = receipts[-1]["payload"]
        artifact_checks = []
        for artifact in completion["artifacts"]:
            path = _allowed_result_artifact(task, artifact["path"])
            actual = digest_file(path)
            if actual != artifact["digest"]:
                raise RuntimeContractError("RESULT_ARTIFACT_DRIFT", artifact["path"], "work product changed after completion")
            artifact_checks.append({"path": artifact["path"], "digest": actual})
        evidence_path = confined_path(task.root, completion["evidence_manifest"])
        evidence_digest, uncovered, entries = _evidence_coverage(task, evidence_path)
        if evidence_digest != completion["evidence_manifest_digest"]:
            raise RuntimeContractError("RESULT_EVIDENCE_DRIFT", completion["evidence_manifest"], "evidence manifest changed after completion")
        if uncovered:
            raise RuntimeContractError("ACCEPTANCE_COVERAGE_MISSING", "/evidence", f"uncovered acceptance criteria: {uncovered}")

        projection_candidates = []
        for item in artifact_checks:
            if not item["path"].startswith(task.relative_dir + "/"):
                continue
            candidate = confined_path(task.root, item["path"])
            try:
                value = load_json(candidate, "PROJECTION_INVALID")
            except RuntimeContractError:
                continue
            if isinstance(value, dict) and value.get("schema") == "pdca.ontology-projection/v1":
                projection_candidates.append(item)
        if len(projection_candidates) != 1:
            raise RuntimeContractError("PROJECTION_ARTIFACT_MISSING", "/artifacts", "exactly one current-task projection manifest is required")
        projection_path = confined_path(task.root, projection_candidates[0]["path"])
        projection_check = verify_projection_manifest(task, projection_path, verify_sources=True)

        transition_receipts = []
        transition_dir = task.task_dir / "transition-receipts"
        if transition_dir.is_dir():
            for path in sorted(transition_dir.glob("*.json")):
                transition_receipts.append({"path": relative_path(task.root, path), "digest": digest_file(path)})

        review_bundle: dict[str, Any] = {
            "schema": "pdca.ontology-conformance-review/v1",
            "task_id": task.task_id,
            "ontology_role": task.ontology_role,
            "review_action": "ontology_conformance_verification",
            "inputs": {
                "task": {"path": f"{task.relative_dir}/task.json", "digest": digest_file(task.task_dir / "task.json")},
                "agent_receipts": {"path": f"{task.relative_dir}/{RECEIPTS_FILE}", "digest": digest_file(task.task_dir / RECEIPTS_FILE)},
                "transition_receipts": transition_receipts,
                "evidence_manifest": {"path": completion["evidence_manifest"], "digest": evidence_digest},
                "work_products": artifact_checks,
            },
            "gates": {
                "execution_contract": "passed",
                "receipt_chain": "passed",
                "artifact_integrity": "passed",
                "acceptance_coverage": "passed",
                "ontology_projection": projection_check,
            },
            "evidence_entry_count": len(entries),
            "result": "pending",
        }
        review_bundle["digest"] = digest_value(review_bundle)
        validate_schema(task.root, review_bundle, "ontology-conformance-review.schema.json", "CONFORMANCE_REVIEW_INVALID")
        bundle_path = task.task_dir / "ontology-conformance-review.json"
        atomic_write_json(bundle_path, review_bundle)
        return {
            "status": "awaiting_conformance_verification",
            "review_bundle": relative_path(task.root, bundle_path),
            "review_digest": review_bundle["digest"],
        }


def _transition_receipt_inputs(task: ExecutableTask) -> list[dict[str, str]]:
    transition_dir = task.task_dir / "transition-receipts"
    if not transition_dir.is_dir():
        return []
    return [
        {"path": relative_path(task.root, path), "digest": digest_file(path)}
        for path in sorted(transition_dir.glob("*.json"))
    ]


def _require_current_review_input(
    recorded: Any,
    current: Any,
    *,
    code: str,
    path: str,
    message: str,
) -> None:
    if recorded != current:
        raise RuntimeContractError(code, path, message)


def _revalidate_pending_review_inputs(
    task: ExecutableTask,
    receipts: list[dict[str, Any]],
    bundle: dict[str, Any],
) -> None:
    """Revalidate the complete pending bundle while the caller holds the task lock."""

    inputs = bundle["inputs"]
    task_relative = f"{task.relative_dir}/task.json"
    _require_current_review_input(
        inputs["task"],
        {"path": task_relative, "digest": digest_file(task.task_dir / "task.json")},
        code="CONFORMANCE_TASK_DRIFT",
        path=task_relative,
        message="current task input changed after the review bundle was created",
    )

    receipts_relative = f"{task.relative_dir}/{RECEIPTS_FILE}"
    _require_current_review_input(
        inputs["agent_receipts"],
        {"path": receipts_relative, "digest": digest_file(task.task_dir / RECEIPTS_FILE)},
        code="CONFORMANCE_RECEIPT_DRIFT",
        path=receipts_relative,
        message="agent receipt input changed after the review bundle was created",
    )
    _verify_recorded_confirmations(task, receipts)

    current_transitions = _transition_receipt_inputs(task)
    _require_current_review_input(
        inputs["transition_receipts"],
        current_transitions,
        code="CONFORMANCE_TRANSITION_DRIFT",
        path=f"{task.relative_dir}/transition-receipts",
        message="transition receipt inputs changed after the review bundle was created",
    )

    completion = receipts[-1]["payload"]
    expected_manifest = {
        "path": completion["evidence_manifest"],
        "digest": completion["evidence_manifest_digest"],
    }
    _require_current_review_input(
        inputs["evidence_manifest"],
        expected_manifest,
        code="CONFORMANCE_EVIDENCE_DRIFT",
        path=completion["evidence_manifest"],
        message="review bundle does not bind the completed evidence manifest",
    )
    evidence_path = confined_path(task.root, completion["evidence_manifest"])
    if digest_file(evidence_path) != inputs["evidence_manifest"]["digest"]:
        raise RuntimeContractError(
            "CONFORMANCE_EVIDENCE_DRIFT",
            completion["evidence_manifest"],
            "evidence manifest changed after the review bundle was created",
        )
    try:
        _, uncovered, entries = _evidence_coverage(task, evidence_path)
    except RuntimeContractError as exc:
        raise RuntimeContractError(
            "CONFORMANCE_EVIDENCE_DRIFT",
            exc.path,
            f"evidence changed after review: {exc.code}",
        ) from exc
    if uncovered or len(entries) != bundle["evidence_entry_count"]:
        raise RuntimeContractError(
            "CONFORMANCE_EVIDENCE_DRIFT",
            completion["evidence_manifest"],
            "evidence coverage or active entry count changed after review",
        )

    expected_products = sorted(completion["artifacts"], key=lambda item: item["path"])
    _require_current_review_input(
        inputs["work_products"],
        expected_products,
        code="CONFORMANCE_WORK_PRODUCT_DRIFT",
        path="/inputs/work_products",
        message="review bundle does not bind the completed work-product set",
    )
    projection_candidates: list[Path] = []
    for artifact in expected_products:
        artifact_path = _allowed_result_artifact(task, artifact["path"])
        if digest_file(artifact_path) != artifact["digest"]:
            raise RuntimeContractError(
                "CONFORMANCE_WORK_PRODUCT_DRIFT",
                artifact["path"],
                "work product changed after the review bundle was created",
            )
        if not artifact["path"].startswith(task.relative_dir + "/"):
            continue
        try:
            value = load_json(artifact_path, "PROJECTION_INVALID")
        except RuntimeContractError:
            continue
        if isinstance(value, dict) and value.get("schema") == "pdca.ontology-projection/v1":
            projection_candidates.append(artifact_path)
    if len(projection_candidates) != 1:
        raise RuntimeContractError(
            "CONFORMANCE_PROJECTION_DRIFT",
            "/inputs/work_products",
            "exactly one reviewed current-task projection manifest is required",
        )
    verify_projection_manifest(task, projection_candidates[0], verify_sources=True)


def record_conformance_decision(
    root: Path,
    task_dir: Path,
    *,
    decision: str,
    reason: str,
    review_digest: str,
) -> dict[str, Any]:
    """Record the coordinator's semantic review decision for a pending bundle."""

    if decision not in {"confirmed", "rejected"}:
        raise RuntimeContractError("CONFORMANCE_DECISION_INVALID", "/decision", "decision must be confirmed or rejected")
    if not isinstance(reason, str) or not reason.strip():
        raise RuntimeContractError("CONFORMANCE_DECISION_INVALID", "/reason", "a non-empty coordinator reason is required")
    load_executable_task(root, task_dir)
    with _task_lock(task_dir):
        task = load_executable_task(root, task_dir)
        receipts = _load_receipts(task)
        if derive_execution_state(receipts) != "awaiting_conformance_verification":
            raise RuntimeContractError("CONFORMANCE_DECISION_STATE_INVALID", "/state", "pending conformance review is required")
        bundle_path = task.task_dir / "ontology-conformance-review.json"
        bundle = load_json(bundle_path, "CONFORMANCE_REVIEW_MISSING")
        validate_schema(task.root, bundle, "ontology-conformance-review.schema.json", "CONFORMANCE_REVIEW_INVALID")
        expected_digest = digest_value({key: value for key, value in bundle.items() if key != "digest"})
        if bundle.get("digest") != expected_digest or review_digest != expected_digest:
            raise RuntimeContractError("CONFORMANCE_REVIEW_DIGEST_MISMATCH", "/review_digest", "decision does not bind the pending review bundle")
        if (
            bundle.get("task_id") != task.task_id
            or bundle.get("ontology_role") != task.ontology_role
            or bundle.get("review_action") != "ontology_conformance_verification"
            or bundle.get("result") != "pending"
        ):
            raise RuntimeContractError("CONFORMANCE_REVIEW_MISMATCH", str(bundle_path), "review bundle does not match the current task")
        _revalidate_pending_review_inputs(task, receipts, bundle)
        event = "conformance_verified" if decision == "confirmed" else "conformance_failed"
        payload = {
            "recorded_by": "coordinator",
            "decision": decision,
            "reason": reason.strip(),
            "review_action": "ontology_conformance_verification",
            "review_bundle": relative_path(task.root, bundle_path),
            "review_digest": review_digest,
        }
        appended = _append_events(task, receipts, [(event, payload)])
        return {"status": derive_execution_state([*receipts, *appended]), "receipt": appended[0]}


def write_context_manifest(path: Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(path, manifest)
