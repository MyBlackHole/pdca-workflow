from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdca_core import identity_diagnostics  # noqa: E402

# seam 契约锚点：被测模块 scripts/pdca_core.py（pdca_core.py 为被测模块）
SEAM_TARGET = "scripts/pdca_core.py"


class IdentityDiagnosticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "flows/flow-plan").mkdir(parents=True)
        (self.root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "records").mkdir()
        (self.root / "pdca/tasks").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_task(self, task_id: str, slug: str) -> Path:
        task_dir = self.root / "pdca/tasks" / slug
        task_dir.mkdir(parents=True, exist_ok=True)
        task = {
            "id": task_id,
            "slug": slug,
            "title": "fixture",
            "parent": None,
            "children": [],
            "status": "Pending",
            "meta": {
                "phase": "plan",
                "active": True,
                "scenario_type": "development",
                "created_at": "2026-08-14T10:00:00+08:00",
                "convergence": ["fixture"],
                "record": f"{task_id}-{slug}",
            },
            "states": {
                "created": "2026-08-14T10:00:00+08:00",
                "plan": "2026-08-14T10:00:00+08:00",
                "do": None,
                "check": None,
                "act": None,
                "archive": None,
            },
        }
        (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
        return task_dir

    def write_event(self, record_id: str, event_id: str, payload_record_id: str) -> None:
        path = self.root / "records" / record_id / "flow-events" / f"{event_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        value = {
            "schema": "pdca.flow-issue-occurrence/v1",
            "event_id": event_id,
            "record_id": payload_record_id,
            "task_id": "T9001",
            "idempotency_key": f"diag-{event_id}",
            "source": "user",
            "category": "tooling-failure",
            "phase": "do",
            "transition": None,
            "rule": {"id": "diag", "version": 1},
            "affected_component": "scripts.transition-phase",
            "normalized_location": "scripts/transition-phase.py:1",
            "issue_code": "DIAG",
            "occurred_at": "2026-08-14T10:00:00+08:00",
            "facts": {"confidence": "observed", "gate_effect": "blocked"},
            "evidence_refs": [],
        }
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_unique_ids_and_slugs_yield_clean_report(self) -> None:
        self.write_task("T9101", "0814-diag-a")
        self.write_task("T9102", "0814-diag-b")
        report = identity_diagnostics(self.root)
        self.assertEqual([], report["duplicate_task_ids"])
        self.assertEqual([], report["duplicate_slugs"])
        self.assertEqual([], report["event_path_mismatches"])
        self.assertTrue(report["valid"])

    def test_duplicate_task_id_is_reported(self) -> None:
        self.write_task("T9101", "0814-diag-a")
        self.write_task("T9101", "0814-diag-b")
        report = identity_diagnostics(self.root)
        self.assertEqual(
            [
                {
                    "task_id": "T9101",
                    "paths": [
                        "pdca/tasks/0814-diag-a/task.json",
                        "pdca/tasks/0814-diag-b/task.json",
                    ],
                }
            ],
            report["duplicate_task_ids"],
        )
        self.assertFalse(report["valid"])

    def test_duplicate_slug_is_reported(self) -> None:
        first = self.write_task("T9101", "0814-diag-same")
        second_dir = self.root / "pdca/tasks/copy"
        second_dir.mkdir(parents=True)
        second = json.loads((first / "task.json").read_text(encoding="utf-8"))
        second["id"] = "T9102"
        second["slug"] = "0814-diag-same"
        (second_dir / "task.json").write_text(json.dumps(second), encoding="utf-8")
        report = identity_diagnostics(self.root)
        self.assertEqual(
            [
                {
                    "slug": "0814-diag-same",
                    "paths": [
                        "pdca/tasks/0814-diag-same/task.json",
                        "pdca/tasks/copy/task.json",
                    ],
                }
            ],
            report["duplicate_slugs"],
        )
        self.assertFalse(report["valid"])

    def test_event_path_mismatch_is_reported(self) -> None:
        self.write_event("R9001", "E9001", "R9002")
        report = identity_diagnostics(self.root)
        self.assertEqual(1, len(report["event_path_mismatches"]))
        mismatch = report["event_path_mismatches"][0]
        self.assertEqual("R9001", mismatch["directory_record_id"])
        self.assertEqual("R9002", mismatch["payload_record_id"])
        self.assertFalse(report["valid"])

    def test_matching_event_payload_is_clean(self) -> None:
        self.write_event("R9001", "E9001", "R9001")
        report = identity_diagnostics(self.root)
        self.assertEqual([], report["event_path_mismatches"])
        self.assertTrue(report["valid"])

    def test_record_derived_mismatch_is_reported(self) -> None:
        task_dir = self.write_task("T9101", "0814-diag-a")
        task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        task["meta"]["record"] = "R9101-something-else"
        (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
        report = identity_diagnostics(self.root)
        self.assertEqual(1, len(report["record_derived_mismatches"]))
        mismatch = report["record_derived_mismatches"][0]
        self.assertEqual("R9101-something-else", mismatch["record"])
        self.assertEqual("T9101-0814-diag-a", mismatch["expected"])
        self.assertFalse(report["valid"])

    def test_missing_record_is_not_a_conflict(self) -> None:
        task_dir = self.write_task("T9101", "0814-diag-a")
        task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        task["meta"]["record"] = None
        (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
        self.write_task("T9102", "0814-diag-b")
        report = identity_diagnostics(self.root)
        self.assertEqual([], report["record_derived_mismatches"])
        self.assertTrue(report["valid"])


if __name__ == "__main__":
    unittest.main()