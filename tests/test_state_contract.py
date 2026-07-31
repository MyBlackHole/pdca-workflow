from __future__ import annotations

import json
import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdca_core import gate_issues, task_issues  # noqa: E402


def base_task(phase: str = "plan") -> dict:
    phases = ["plan", "do", "check", "act", "archive"]
    index = phases.index(phase)
    times = {
        "created": "2026-07-28T10:00:00+08:00",
        "plan": "2026-07-28T10:00:00+08:00" if index >= 0 else None,
        "do": "2026-07-28T10:01:00+08:00" if index >= 1 else None,
        "check": "2026-07-28T10:02:00+08:00" if index >= 2 else None,
        "act": "2026-07-28T10:03:00+08:00" if index >= 3 else None,
        "archive": "2026-07-28T10:04:00+08:00" if index >= 4 else None,
    }
    status = {"plan": "Pending", "do": "InProgress", "check": "Completed", "act": "Completed", "archive": "Completed"}[phase]
    return {
        "id": "T9000",
        "slug": "0728-test-task",
        "title": "fixture",
        "parent": None,
        "children": [],
        "status": status,
        "meta": {
            "phase": phase,
            "active": phase != "archive",
            "scenario_type": "development",
            "created_at": "2026-07-28T10:00:00+08:00",
            "convergence": ["fixture passes"],
        },
        "states": times,
    }


class ContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "flows/flow-plan").mkdir(parents=True)
        (self.root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "records").mkdir()
        self.task_dir = self.root / "pdca/tasks/0728-test-task"
        self.task_dir.mkdir(parents=True)
        (self.task_dir / "prd.md").write_text("# PRD\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_task(self, task: dict) -> None:
        (self.task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")

    def write_clarifications(self, *entries: dict) -> None:
        text = "".join(json.dumps(entry) + "\n" for entry in entries)
        (self.task_dir / "clarifications.jsonl").write_text(text, encoding="utf-8")

    def test_plan_gate_accepts_confirmed_response(self) -> None:
        self.write_task(base_task())
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "approved",
                "response": "confirmed",
                "at": "2026-07-28T10:00:01+08:00",
            }
        )
        phase, issues = gate_issues(self.root, self.task_dir)
        self.assertEqual("plan", phase)
        self.assertEqual([], issues)

    def test_every_phase_accepts_a_complete_valid_task(self) -> None:
        for phase in ["plan", "do", "check", "act", "archive"]:
            with self.subTest(phase=phase):
                task = base_task(phase)
                entries = [
                    {
                        "source": "final_confirmation",
                        "summary": "approved",
                        "response": "confirmed",
                        "at": "2026-07-28T10:00:01+08:00",
                    }
                ]
                if phase in {"check", "act", "archive"}:
                    task["meta"]["record"] = "R9000"
                    evidence_dir = self.root / "records/R9000/evidence"
                    evidence_dir.mkdir(parents=True, exist_ok=True)
                    artifact = evidence_dir / "result.txt"
                    artifact.write_text("pass\n", encoding="utf-8")
                    (evidence_dir / "manifest.jsonl").write_text(
                        json.dumps(
                            {
                                "id": "result",
                                "file": "result.txt",
                                "kind": "test",
                                "size": 5,
                                "digest": "sha256:" + hashlib.sha256(b"pass\n").hexdigest(),
                                "at": "2026-07-28T10:02:00+08:00",
                                "criteria": ["AC-1"],
                            }
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                if phase in {"act", "archive"}:
                    (self.root / "records/R9000/conclusion.md").write_text("# conclusion\n", encoding="utf-8")
                    task["meta"]["verdict"] = {
                        "outcome": "confirmed",
                        "reason": "fixture passed",
                        "verdict_id": "V9000",
                        "at": "2026-07-28T10:03:00+08:00",
                    }
                    entries.append(
                        {
                            "source": "check_confirmation",
                            "summary": "accepted",
                            "response": "confirmed",
                            "at": "2026-07-28T10:03:00+08:00",
                        }
                    )
                if phase == "archive":
                    task["meta"]["disposition"] = {
                        "outcome": "task_only",
                        "reason": "fixture only",
                        "at": "2026-07-28T10:04:00+08:00",
                    }
                self.write_task(task)
                self.write_clarifications(*entries)
                self.assertEqual([], task_issues(self.root, self.task_dir))

    def test_plan_gate_rejects_unconfirmed_response(self) -> None:
        self.write_task(base_task())
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "not approved",
                "response": "rejected",
                "at": "2026-07-28T10:00:01+08:00",
            }
        )
        _, issues = gate_issues(self.root, self.task_dir)
        codes = {issue.code for issue in issues}
        self.assertIn("SCHEMA_INVALID", codes)
        self.assertIn("FINAL_CONFIRMATION_MISSING", codes)

    def test_archive_inconsistency_is_rejected(self) -> None:
        task = base_task("archive")
        task["status"] = "InProgress"
        task["states"]["archive"] = None
        self.write_task(task)
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "approved",
                "response": "confirmed",
                "at": "2026-07-28T10:00:01+08:00",
            }
        )
        issues = task_issues(self.root, self.task_dir)
        codes = {issue.code for issue in issues}
        self.assertIn("STATUS_PHASE_MISMATCH", codes)
        self.assertIn("STATE_TIMESTAMP_MISSING", codes)
        self.assertIn("DISPOSITION_MISSING", codes)

    def test_empty_disposition_is_rejected(self) -> None:
        task = base_task("archive")
        task["meta"]["disposition"] = {}
        self.write_task(task)
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "approved",
                "response": "confirmed",
                "at": "2026-07-28T10:00:01+08:00",
            }
        )
        issues = task_issues(self.root, self.task_dir)
        self.assertIn("SCHEMA_INVALID", {issue.code for issue in issues})

    def test_future_state_timestamp_is_rejected(self) -> None:
        task = base_task("do")
        task["states"]["check"] = "2026-07-28T10:02:00+08:00"
        self.write_task(task)
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "approved",
                "response": "confirmed",
                "at": "2026-07-28T10:00:01+08:00",
            }
        )
        issues = task_issues(self.root, self.task_dir, include_phase_requirements=False)
        self.assertIn("FUTURE_STATE_SET", {issue.code for issue in issues})

    def test_final_confirmation_cannot_predate_task(self) -> None:
        self.write_task(base_task("do"))
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "impossible ordering",
                "response": "confirmed",
                "at": "2026-07-28T09:59:59+08:00",
            }
        )
        issues = task_issues(self.root, self.task_dir)
        self.assertIn("FINAL_CONFIRMATION_TIME_ORDER", {issue.code for issue in issues})

    def test_evidence_requires_criteria_and_cannot_escape_record(self) -> None:
        task = base_task("check")
        task["meta"]["record"] = "R9000"
        self.write_task(task)
        self.write_clarifications(
            {
                "source": "final_confirmation",
                "summary": "approved",
                "response": "confirmed",
                "at": "2026-07-28T10:00:01+08:00",
            }
        )
        evidence_dir = self.root / "records/R9000/evidence"
        evidence_dir.mkdir(parents=True)
        (self.root / "records/R9000/outside.txt").write_text("outside", encoding="utf-8")
        (evidence_dir / "manifest.jsonl").write_text(
            json.dumps(
                {
                    "id": "escape",
                    "file": "../outside.txt",
                    "kind": "test",
                    "size": 7,
                    "digest": "sha256:" + "0" * 64,
                    "at": "2026-07-28T10:02:00+08:00",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        issues = task_issues(self.root, self.task_dir)
        codes = {issue.code for issue in issues}
        self.assertIn("SCHEMA_INVALID", codes)
        self.assertIn("EVIDENCE_PATH_ESCAPE", codes)


if __name__ == "__main__":
    unittest.main()
