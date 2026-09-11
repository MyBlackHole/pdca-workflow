from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import RuntimeContractError
from .io import digest_value, load_json, relative_path, validate_schema


ONTOLOGY_ROLES = (
    "ontology_modeling",
    "ontology_projection",
    "ontology_conformance_verification",
)
EXECUTION_CONTRACT_FIELDS = frozenset(
    {"work_product", "required_actions", "constraints", "testable_signal"}
)


@dataclass(frozen=True)
class ExecutableTask:
    root: Path
    task_dir: Path
    relative_dir: str
    task_id: str
    ontology_role: str
    ontology_anchor: str
    record_id: str
    work_product: str
    required_actions: tuple[str, ...]
    constraints: tuple[str, ...]
    testable_signal: str
    steps: tuple[dict[str, str], ...]
    task_digest: str
    execution_contract_digest: str

    def contract_value(self) -> dict[str, Any]:
        return {
            "work_product": self.work_product,
            "required_actions": list(self.required_actions),
            "constraints": list(self.constraints),
            "testable_signal": self.testable_signal,
        }


def _validate_task_location(root: Path, task_dir: Path) -> tuple[Path, str]:
    resolved_root = root.resolve()
    resolved = task_dir.resolve()
    active_root = (resolved_root / "pdca" / "tasks").resolve()
    try:
        relative = resolved.relative_to(active_root)
    except ValueError as exc:
        raise RuntimeContractError(
            "TASK_SCOPE_INVALID", str(task_dir), "task must be inside pdca/tasks"
        ) from exc
    if not relative.parts or "archive" in relative.parts or len(relative.parts) != 1:
        raise RuntimeContractError(
            "TASK_SCOPE_INVALID", str(task_dir), "runtime accepts one direct, non-archived task directory"
        )
    return resolved, relative_path(resolved_root, resolved)


def load_executable_task(root: Path, task_dir: Path) -> ExecutableTask:
    """Load only the named task; relationship fields are never followed."""

    root = root.resolve()
    task_dir, relative_dir = _validate_task_location(root, task_dir)
    task = load_json(task_dir / "task.json", "EXECUTABLE_TASK_INVALID")
    if not isinstance(task, dict):
        raise RuntimeContractError("EXECUTABLE_TASK_INVALID", "/", "task must be an object")
    validate_schema(root, task, "task.schema.json", "EXECUTABLE_TASK_INVALID")
    validate_schema(root, task, "executable-task.schema.json", "EXECUTABLE_TASK_INVALID")

    meta = task["meta"]
    contract = meta["execution_contract"]
    if set(contract) != EXECUTION_CONTRACT_FIELDS:
        raise RuntimeContractError(
            "EXECUTION_CONTRACT_FIELDS_INVALID",
            "/meta/execution_contract",
            "execution contract must contain exactly work_product, required_actions, constraints, and testable_signal",
        )
    role = meta["ontology_role"]
    if role not in ONTOLOGY_ROLES:
        raise RuntimeContractError("ONTOLOGY_ROLE_INVALID", "/meta/ontology_role", "unsupported ontology role")
    anchor = meta.get("ontology_anchor")
    if not isinstance(anchor, str) or not anchor.startswith("ontology:"):
        raise RuntimeContractError(
            "ONTOLOGY_ANCHOR_MISSING", "/meta/ontology_anchor", "an ontology anchor is required for projection"
        )
    record_id = meta.get("record")
    if not isinstance(record_id, str) or not record_id:
        raise RuntimeContractError(
            "TASK_RECORD_MISSING", "/meta/record", "a current-task evidence record is required"
        )

    copied_steps = tuple(copy.deepcopy(meta.get("steps", [])))
    return ExecutableTask(
        root=root,
        task_dir=task_dir,
        relative_dir=relative_dir,
        task_id=task["id"],
        ontology_role=role,
        ontology_anchor=anchor,
        record_id=record_id,
        work_product=contract["work_product"],
        required_actions=tuple(contract["required_actions"]),
        constraints=tuple(contract["constraints"]),
        testable_signal=contract["testable_signal"],
        steps=copied_steps,
        task_digest=digest_value(task),
        execution_contract_digest=digest_value(contract),
    )


def contract_requires_research(meta: dict[str, Any]) -> bool:
    """Research is explicit only when an action says so; ontology role is irrelevant."""

    contract = meta.get("execution_contract")
    if not isinstance(contract, dict):
        return False
    work_product = contract.get("work_product")
    if isinstance(work_product, str) and (
        "research-report" in work_product.casefold() or "调研报告" in work_product
    ):
        return False
    actions = contract.get("required_actions")
    if not isinstance(actions, list):
        return False
    return any(
        isinstance(action, str) and ("research" in action.casefold() or "调研" in action)
        for action in actions
    )


def contract_needs_fix_approval(meta: dict[str, Any]) -> bool:
    contract = meta.get("execution_contract")
    if not isinstance(contract, dict):
        return False
    actions = contract.get("required_actions")
    if not isinstance(actions, list):
        return False
    return any(
        isinstance(action, str)
        and ("fix_confirmation" in action.casefold() or "确认修复方案" in action)
        for action in actions
    )
