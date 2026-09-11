from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from flow_audit import _do_checks  # noqa: E402
from pdca_core import schema_issues  # noqa: E402


class FixConfirmationContractTest(unittest.TestCase):
    def test_clarification_channel_remains_valid(self) -> None:
        entry = {
            "source": "fix_confirmation",
            "summary": "root cause and proposed correction",
            "response": "confirmed",
            "at": "2026-09-04T10:00:00+08:00",
        }
        self.assertEqual([], schema_issues(ROOT, entry, "clarification.schema.json"))

    def test_cli_appends_real_fix_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ontology/process").mkdir(parents=True)
            (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            task_dir = root / "pdca/tasks/0904-fix-confirmation-test"
            task_dir.mkdir(parents=True)
            (task_dir / "clarifications.jsonl").write_text("", encoding="utf-8")
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/append-confirmation.py"),
                    "--task-dir",
                    str(task_dir),
                    "--source",
                    "fix_confirmation",
                    "--response",
                    "confirmed",
                    "--summary",
                    "root cause and proposed correction",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)

    def test_fix_gate_is_declared_as_required_action(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "schemas", root / "schemas")
            task_dir = root / "pdca/tasks/0911-fix-action"
            task_dir.mkdir(parents=True)
            (task_dir / "prd.md").write_text("# PRD\n\n- [ ] AC-1: fixed\n", encoding="utf-8")
            (task_dir / "clarifications.jsonl").write_text("", encoding="utf-8")
            task = {
                "meta": {
                    "record": "R1",
                    "execution_contract": {
                        "work_product": "fix",
                        "required_actions": ["确认修复方案", "apply correction"],
                        "constraints": [],
                        "testable_signal": "test passes",
                    },
                    "convergence": ["fixed"],
                }
            }
            (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
            check = next(item for item in _do_checks(root, task_dir, task) if item["id"] == "fix-confirmation")
            self.assertIn("FIX_CONFIRMATION_MISSING", {item["code"] for item in check["issues"]})
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(
                    {
                        "source": "fix_confirmation",
                        "summary": "approved correction",
                        "response": "confirmed",
                        "at": "2026-09-11T10:00:00+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            check = next(item for item in _do_checks(root, task_dir, task) if item["id"] == "fix-confirmation")
            self.assertEqual([], check["issues"])

    def test_task_schema_has_no_extra_fix_control(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text(encoding="utf-8"))
        properties = schema["properties"]["meta"]["properties"]["execution_contract"]["properties"]
        self.assertEqual(
            {"work_product", "required_actions", "constraints", "testable_signal"},
            set(properties),
        )


if __name__ == "__main__":
    unittest.main()
