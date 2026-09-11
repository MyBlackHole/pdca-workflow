from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .errors import RuntimeContractError
from .io import atomic_write_json, current_task_path, load_json
from .lifecycle import (
    _load_receipts,
    bind_agent,
    build_context_manifest,
    derive_execution_state,
    prepare_dispatch_request,
    record_conformance_decision,
    record_agent_result,
    record_user_confirmation,
    resume_for_conformance,
    write_context_manifest,
)
from .projection import build_projection_manifest, verify_projection_manifest, write_projection_manifest
from .task import load_executable_task


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _task(args: argparse.Namespace):
    return load_executable_task(args.root.resolve(), args.task_dir.resolve())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Current-task PDCA execution runtime")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--task-dir", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("validate-task")

    project = commands.add_parser("project")
    project.add_argument("--selected-id", action="append", required=True)
    project.add_argument("--bindings", type=Path, required=True)
    project.add_argument("--output", type=Path, required=True)

    verify = commands.add_parser("verify-projection")
    verify.add_argument("--manifest", type=Path, required=True)

    context = commands.add_parser("build-context")
    context.add_argument("--path", action="append", required=True)
    context.add_argument("--output", type=Path, required=True)

    prepare = commands.add_parser("prepare-dispatch")
    prepare.add_argument("--projection", type=Path, required=True)
    prepare.add_argument("--context", type=Path, required=True)
    prepare.add_argument("--spawn-status", choices=["available", "missing"], required=True)
    prepare.add_argument("--output", type=Path)

    bind = commands.add_parser("bind")
    bind.add_argument("--request", type=Path, required=True)
    bind.add_argument("--adapter-receipt", type=Path, required=True)
    bind.add_argument("--projection", type=Path, required=True)
    bind.add_argument("--context", type=Path, required=True)

    commands.add_parser("state")

    result = commands.add_parser("record-result")
    result.add_argument("--status", choices=["completed", "failed", "awaiting_confirmation"], required=True)
    result.add_argument("--agent-id", required=True)
    result.add_argument("--request-digest", required=True)
    result.add_argument("--artifact", action="append")
    result.add_argument("--evidence-manifest")
    result.add_argument("--message")

    commands.add_parser("resume-conformance")

    confirmation = commands.add_parser("record-user-confirmation")
    confirmation.add_argument("--clarification-digest", required=True)

    decision = commands.add_parser("record-conformance-decision")
    decision.add_argument("--decision", choices=["confirmed", "rejected"], required=True)
    decision.add_argument("--reason", required=True)
    decision.add_argument("--review-digest", required=True)
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    task = _task(args)
    if args.command == "validate-task":
        return {
            "status": "passed",
            "task_id": task.task_id,
            "ontology_role": task.ontology_role,
            "execution_contract_digest": task.execution_contract_digest,
        }
    if args.command == "project":
        bindings_path = current_task_path(task.task_dir, args.bindings)
        output = current_task_path(task.task_dir, args.output, must_exist=False)
        bindings = load_json(bindings_path, "ACTION_BINDING_INVALID")
        if not isinstance(bindings, list):
            raise RuntimeContractError("ACTION_BINDING_INVALID", str(args.bindings), "bindings must be an array")
        manifest = build_projection_manifest(task, args.selected_id, bindings)
        write_projection_manifest(output, manifest)
        return {"status": "written", "path": str(output), "digest": manifest["digest"]}
    if args.command == "verify-projection":
        return verify_projection_manifest(task, current_task_path(task.task_dir, args.manifest))
    if args.command == "build-context":
        manifest = build_context_manifest(task, args.path)
        output = current_task_path(task.task_dir, args.output, must_exist=False)
        write_context_manifest(output, manifest)
        return {"status": "written", "path": str(output), "digest": manifest["digest"]}
    if args.command == "prepare-dispatch":
        projection = current_task_path(task.task_dir, args.projection)
        context = current_task_path(task.task_dir, args.context)
        request = prepare_dispatch_request(task, projection, context, spawn_status=args.spawn_status)
        if args.output:
            output = current_task_path(task.task_dir, args.output, must_exist=False)
            atomic_write_json(output, request)
            return {"status": "written", "path": str(output), "request_digest": request["request_digest"]}
        return request
    if args.command == "bind":
        return bind_agent(
            args.root,
            args.task_dir,
            load_json(current_task_path(task.task_dir, args.request), "DISPATCH_REQUEST_INVALID"),
            load_json(current_task_path(task.task_dir, args.adapter_receipt), "ADAPTER_RECEIPT_INVALID"),
            current_task_path(task.task_dir, args.projection),
            current_task_path(task.task_dir, args.context),
        )
    if args.command == "state":
        return {"task_id": task.task_id, "state": derive_execution_state(_load_receipts(task))}
    if args.command == "record-result":
        return record_agent_result(
            args.root,
            args.task_dir,
            status=args.status,
            agent_id=args.agent_id,
            request_digest=args.request_digest,
            artifacts=args.artifact,
            evidence_manifest=args.evidence_manifest,
            message=args.message,
        )
    if args.command == "resume-conformance":
        return resume_for_conformance(args.root, args.task_dir)
    if args.command == "record-user-confirmation":
        return record_user_confirmation(
            args.root,
            args.task_dir,
            clarification_digest=args.clarification_digest,
        )
    if args.command == "record-conformance-decision":
        return record_conformance_decision(
            args.root,
            args.task_dir,
            decision=args.decision,
            reason=args.reason,
            review_digest=args.review_digest,
        )
    raise RuntimeContractError("COMMAND_INVALID", "/command", "unsupported command")


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = run(args)
    except RuntimeContractError as exc:
        _emit({"status": "error", **exc.as_dict()})
        print(str(exc), file=sys.stderr)
        return 1
    _emit(payload)
    return 0
