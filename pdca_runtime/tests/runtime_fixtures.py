from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from pdca_runtime.io import atomic_write_json
from pdca_runtime.lifecycle import build_context_manifest, prepare_dispatch_request
from pdca_runtime.projection import build_projection_manifest
from pdca_runtime.task import load_executable_task


ROOT = Path(__file__).resolve().parents[2]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_runtime_root(base: Path, role: str = "ontology_projection") -> tuple[Path, Path]:
    root = base
    shutil.copytree(ROOT / "schemas", root / "schemas")
    (root / "config").mkdir()
    (root / "config/capabilities.yaml").write_text(
        "schema: pdca.capabilities/v1\ncapabilities:\n  agent.spawn:\n    required: true\n    probe: environment:PDCA_AGENT_SPAWN\n",
        encoding="utf-8",
    )
    task_dir = root / "pdca/tasks/0911-runtime-fixture"
    task_dir.mkdir(parents=True)
    task = {
        "id": "T9001",
        "slug": "0911-runtime-fixture",
        "title": "runtime fixture",
        "parent": "T9998",
        "children": ["T9999"],
        "dependencies": ["T9997"],
        "status": "InProgress",
        "meta": {
            "phase": "do",
            "active": True,
            "ontology_role": role,
            "ontology_anchor": "ontology:concept/executor-adapter",
            "ontology_fragment": "ontology",
            "record": "T9001-runtime-fixture",
            "created_at": "2026-09-11T10:00:00+08:00",
            "convergence": ["runtime converges"],
            "execution_contract": {
                "work_product": "runtime output",
                "required_actions": ["project constraints", "verify result"],
                "constraints": ["current task only"],
                "testable_signal": "runtime tests pass",
            },
            "steps": [
                {
                    "name": "project",
                    "description": "project runtime",
                    "completion_criterion": "projection is traceable",
                },
                {
                    "name": "verify",
                    "description": "verify runtime",
                    "completion_criterion": "verification passes",
                },
            ],
        },
        "states": {
            "created": "2026-09-11T10:00:00+08:00",
            "plan": "2026-09-11T10:00:00+08:00",
            "do": "2026-09-11T10:01:00+08:00",
            "check": None,
            "act": None,
            "archive": None,
        },
    }
    write_json(task_dir / "task.json", task)
    (task_dir / "prd.md").write_text(
        "# Fixture\n\n## 验收标准\n\n- [ ] AC-1: projection\n- [ ] AC-2: runtime\n",
        encoding="utf-8",
    )
    ontology_values = {
        "ontology/concept/ontology-rule-non-dangling.md": (
            "ontology:concept/ontology-rule-non-dangling",
            [],
        ),
        "ontology/concept/executor-adapter.md": (
            "ontology:concept/executor-adapter",
            ["ontology:concept/pdca-task", "ontology:concept/capability-protocol"],
        ),
        "ontology/concept/pdca-task.md": ("ontology:concept/pdca-task", []),
        "ontology/concept/capability-protocol.md": ("ontology:concept/capability-protocol", []),
        "ontology/concept/unrelated-authority.md": ("ontology:concept/unrelated-authority", []),
    }
    for relative, (node_id, related) in ontology_values.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        rule_spec = (
            "rule_spec:\n"
            "  reference_relation_keys:\n"
            "    - specializes\n"
            "    - instance_of\n"
            "    - composed_of\n"
            "    - configured_by\n"
            "    - part_of\n"
            "    - guides\n"
            "    - relates_to\n"
            if node_id == "ontology:concept/ontology-rule-non-dangling"
            else ""
        )
        path.write_text(
            "---\n"
            "schema: pdca.asset/v1\n"
            f"id: {node_id}\n"
            "type: concept\n"
            "layer: Knowledge\n"
            f"summary: {node_id}\n"
            "status: active\n"
            + rule_spec
            +
            "relations:\n"
            "  relates_to:\n"
            + "".join(f"    - {target}\n" for target in related)
            + "---\n# node\n",
            encoding="utf-8",
        )
    return root, task_dir


def runtime_materials(root: Path, task_dir: Path):
    task = load_executable_task(root, task_dir)
    authority = [
        "ontology/concept/executor-adapter.md",
        "ontology/concept/pdca-task.md",
        "ontology/concept/capability-protocol.md",
    ]
    bindings = [
        {
            "action_index": 1,
            "step_name": "project",
            "ontology_id": "ontology:concept/executor-adapter",
            "depends_on": [],
        },
        {
            "action_index": 2,
            "step_name": "verify",
            "ontology_id": "ontology:concept/capability-protocol",
            "depends_on": ["action-001"],
        },
    ]
    projection = build_projection_manifest(
        task,
        [
            "ontology:concept/executor-adapter",
            "ontology:concept/pdca-task",
            "ontology:concept/capability-protocol",
        ],
        bindings,
    )
    projection_path = task_dir / "projection-manifest.json"
    atomic_write_json(projection_path, projection)
    context = build_context_manifest(
        task,
        [
            f"{task.relative_dir}/task.json",
            f"{task.relative_dir}/prd.md",
            *authority,
        ],
    )
    context_path = task_dir / "context-manifest.json"
    atomic_write_json(context_path, context)
    request = prepare_dispatch_request(task, projection, context, spawn_status="available")
    return task, projection, projection_path, context, context_path, request
