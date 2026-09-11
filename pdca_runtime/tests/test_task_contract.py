from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pdca_runtime import ONTOLOGY_ROLES, RuntimeContractError, load_executable_task
from pdca_runtime.io import validate_schema
from pdca_runtime.tests.runtime_fixtures import make_runtime_root, write_json


class ExecutableTaskContractTest(unittest.TestCase):
    def test_all_three_roles_are_executable(self) -> None:
        for role in ONTOLOGY_ROLES:
            with self.subTest(role=role), tempfile.TemporaryDirectory() as temporary:
                root, task_dir = make_runtime_root(Path(temporary), role)
                self.assertEqual(role, load_executable_task(root, task_dir).ontology_role)

    def test_contract_requires_exactly_four_fields(self) -> None:
        mutations = [
            lambda contract: contract.pop("testable_signal"),
            lambda contract: contract.update({"control_mode": "legacy"}),
        ]
        for mutate in mutations:
            with tempfile.TemporaryDirectory() as temporary:
                root, task_dir = make_runtime_root(Path(temporary))
                task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
                mutate(task["meta"]["execution_contract"])
                write_json(task_dir / "task.json", task)
                with self.assertRaises(RuntimeContractError) as caught:
                    load_executable_task(root, task_dir)
                self.assertEqual("EXECUTABLE_TASK_INVALID", caught.exception.code)

    def test_old_role_is_rejected(self) -> None:
        root, task_dir = make_runtime_root(Path(tempfile.mkdtemp()))
        task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        task["meta"]["ontology_role"] = "development"
        write_json(task_dir / "task.json", task)
        with self.assertRaises(RuntimeContractError):
            load_executable_task(root, task_dir)

    def test_lifecycle_schema_does_not_authorize_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
            task["meta"].pop("execution_contract")
            task["meta"]["phase"] = "plan"
            task["status"] = "Pending"
            task["states"]["do"] = None
            validate_schema(root, task, "task.schema.json", "TASK_INVALID")
            write_json(task_dir / "task.json", task)
            with self.assertRaises(RuntimeContractError):
                load_executable_task(root, task_dir)

    def test_task_relationships_are_not_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            loaded = load_executable_task(root, task_dir)
            self.assertFalse(hasattr(loaded, "parent"))
            self.assertFalse(hasattr(loaded, "children"))
            self.assertFalse(hasattr(loaded, "dependencies"))


if __name__ == "__main__":
    unittest.main()
