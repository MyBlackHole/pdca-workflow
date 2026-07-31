from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdca_core import acceptance_criteria, confirmation_time_issues  # noqa: E402


def make_root(temporary: str) -> Path:
    root = Path(temporary)
    (root / "flows/flow-plan").mkdir(parents=True)
    (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
    shutil.copytree(ROOT / "schemas", root / "schemas")
    (root / "records").mkdir()
    return root


def make_task(root: Path, phase: str = "plan", ac_text: str | None = None) -> Path:
    task_dir = root / "pdca/tasks/0728-ai-usability"
    task_dir.mkdir(parents=True)
    index = ["plan", "do", "check", "act", "archive"].index(phase)
    times = {}
    for name in ["created", "plan", "do", "check", "act", "archive"]:
        times[name] = None
    times["created"] = "2026-07-28T10:00:00+08:00"
    times["plan"] = "2026-07-28T10:00:00+08:00"
    if index >= 1:
        times["do"] = "2026-07-28T10:01:00+08:00"
    if index >= 2:
        times["check"] = "2026-07-28T10:02:00+08:00"
    if index >= 3:
        times["act"] = "2026-07-28T10:03:00+08:00"
    if index >= 4:
        times["archive"] = "2026-07-28T10:04:00+08:00"
    status = {"plan": "Pending", "do": "InProgress", "check": "Completed", "act": "Completed", "archive": "Completed"}[phase]
    task = {
        "id": "T9001",
        "slug": "0728-ai-usability",
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
    (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
    if ac_text is not None:
        (task_dir / "prd.md").write_text(ac_text, encoding="utf-8")
    return task_dir


class AppendConfirmationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = make_root(self.temporary.name)
        self.task_dir = make_task(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def append(self, *args: str) -> subprocess.CompletedProcess:
        command = [
            "python3",
            str(ROOT / "scripts/append-confirmation.py"),
            "--task-dir",
            str(self.task_dir),
            "--root",
            str(self.root),
            *args,
        ]
        return subprocess.run(command, capture_output=True, text=True)

    def test_appends_final_confirmation_with_real_timestamp(self) -> None:
        completed = self.append(
            "--source", "final_confirmation", "--response", "confirmed", "--summary", "approved"
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        stamped = datetime.fromisoformat(payload["at"])
        self.assertAlmostEqual(datetime.now().astimezone().timestamp(), stamped.timestamp(), delta=60)
        entries = json.loads(
            (self.task_dir / "clarifications.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
        )
        self.assertEqual("final_confirmation", entries["source"])
        self.assertEqual(payload["at"], entries["at"])

    def test_rejects_final_confirmation_response_other_than_confirmed(self) -> None:
        completed = self.append(
            "--source", "final_confirmation", "--response", "partial", "--summary", "approved"
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertFalse((self.task_dir / "clarifications.jsonl").is_file())

    def test_duplicate_final_confirmation_is_rejected_without_file_change(self) -> None:
        self.append("--source", "final_confirmation", "--response", "confirmed", "--summary", "first")
        before = (self.task_dir / "clarifications.jsonl").read_bytes()
        completed = self.append(
            "--source", "final_confirmation", "--response", "confirmed", "--summary", "second"
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual(before, (self.task_dir / "clarifications.jsonl").read_bytes())


class GuidanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = make_root(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_acceptance_criteria_missing_carries_executable_guidance(self) -> None:
        task_dir = make_task(self.root, ac_text="# PRD\n\n### AC-1 wrong format\n")
        criteria, issues = acceptance_criteria(task_dir)
        self.assertEqual([], criteria)
        missing = [issue for issue in issues if issue.code == "ACCEPTANCE_CRITERIA_MISSING"]
        self.assertEqual(1, len(missing))
        self.assertIsNotNone(missing[0].guidance)
        self.assertIn("## 验收标准", missing[0].guidance)
        self.assertIn("- [ ]", missing[0].guidance)

    def test_confirmation_after_transition_carries_guidance(self) -> None:
        task = {
            "meta": {"created_at": "2026-07-28T10:00:00+08:00"},
        }
        entries = [
            {"source": "final_confirmation", "response": "confirmed", "at": "2026-07-31T12:00:00+08:00"}
        ]
        issues = confirmation_time_issues(task, entries, now=datetime.fromisoformat("2026-07-28T11:00:00+08:00"))
        found = [issue for issue in issues if issue.code == "FINAL_CONFIRMATION_AFTER_TRANSITION"]
        self.assertEqual(1, len(found))
        self.assertIsNotNone(found[0].guidance)
        self.assertIn("append-confirmation.py", found[0].guidance)

    def test_as_dict_includes_guidance_when_present(self) -> None:
        from pdca_core import Issue

        plain = Issue("X", "/", "message").as_dict()
        self.assertNotIn("guidance", plain)
        guided = Issue("X", "/", "message", "how to fix").as_dict()
        self.assertEqual("how to fix", guided["guidance"])


class ReplaceEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = make_root(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def register(self, source: Path, record: str, id: str, kind: str, file: str) -> dict:
        command = [
            "python3",
            str(ROOT / "scripts/register-evidence.py"),
            "--record", record,
            "--source", str(source),
            "--id", id,
            "--kind", kind,
            "--criterion", "AC-1",
            "--file", file,
            "--root", str(self.root),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stderr)
        return json.loads(completed.stdout)

    def test_replace_keeps_superseded_file_and_marks_manifest(self) -> None:
        old_source = self.root / "old.txt"
        old_source.write_text("v1\n", encoding="utf-8")
        new_source = self.root / "new.txt"
        new_source.write_text("v2\n", encoding="utf-8")
        self.register(old_source, "R9002", "e1", "test", "old.txt")

        command = [
            "python3",
            str(ROOT / "scripts/register-evidence.py"),
            "--record", "R9002",
            "--source", str(new_source),
            "--id", "e2",
            "--kind", "test",
            "--criterion", "AC-1",
            "--file", "new.txt",
            "--replace", "e1",
            "--root", str(self.root),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("replaced", payload["status"])

        evidence_dir = self.root / "records/R9002/evidence"
        self.assertTrue((evidence_dir / "new.txt").is_file())
        superseded = list(evidence_dir.glob("old.superseded.*.txt"))
        self.assertEqual(1, len(superseded))
        self.assertEqual("v1\n", superseded[0].read_text(encoding="utf-8"))

        entries = [
            json.loads(line)
            for line in (evidence_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        by_id = {entry["id"]: entry for entry in entries}
        self.assertEqual("e2", by_id["e1"]["superseded_by"])
        self.assertIn("e2", by_id)
        self.assertNotIn("superseded_by", by_id["e2"])

    def test_replace_unknown_id_fails_without_manifest_change(self) -> None:
        source = self.root / "new.txt"
        source.write_text("v2\n", encoding="utf-8")
        command = [
            "python3",
            str(ROOT / "scripts/register-evidence.py"),
            "--record", "R9003",
            "--source", str(source),
            "--id", "e9",
            "--kind", "test",
            "--criterion", "AC-1",
            "--file", "new.txt",
            "--replace", "does-not-exist",
            "--root", str(self.root),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, completed.returncode)
        self.assertFalse((self.root / "records/R9003/evidence/manifest.jsonl").is_file())

    def test_replace_superseded_entry_is_rejected(self) -> None:
        old_source = self.root / "old.txt"
        old_source.write_text("v1\n", encoding="utf-8")
        new_source = self.root / "new.txt"
        new_source.write_text("v2\n", encoding="utf-8")
        self.register(old_source, "R9005", "e1", "test", "old.txt")
        subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/register-evidence.py"),
                "--record", "R9005",
                "--source", str(new_source),
                "--id", "e2",
                "--kind", "test",
                "--criterion", "AC-1",
                "--file", "new.txt",
                "--replace", "e1",
                "--root", str(self.root),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        completed = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/register-evidence.py"),
                "--record", "R9005",
                "--source", str(new_source),
                "--id", "e3",
                "--kind", "test",
                "--criterion", "AC-1",
                "--file", "new2.txt",
                "--replace", "e1",
                "--root", str(self.root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("already superseded", completed.stderr)

    def test_superseded_entries_are_skipped_by_evidence_checks(self) -> None:
        old_source = self.root / "old.txt"
        old_source.write_text("v1\n", encoding="utf-8")
        new_source = self.root / "new.txt"
        new_source.write_text("v2\n", encoding="utf-8")
        self.register(old_source, "R9004", "e1", "test", "old.txt")
        command = [
            "python3",
            str(ROOT / "scripts/register-evidence.py"),
            "--record", "R9004",
            "--source", str(new_source),
            "--id", "e2",
            "--kind", "test",
            "--criterion", "AC-1",
            "--file", "new.txt",
            "--replace", "e1",
            "--root", str(self.root),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)

        from pdca_core import evidence_issues

        task = {"meta": {"record": "R9004"}}
        issues = evidence_issues(self.root, task)
        codes = [issue.code for issue in issues]
        self.assertNotIn("EVIDENCE_FILE_MISSING", codes)


class EarlyPrdGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = make_root(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def transition(self, task_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/transition-phase.py"),
                str(task_dir),
                "--to",
                "do",
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )

    def test_plan_to_do_rejects_heading_style_acceptance(self) -> None:
        task_dir = make_task(self.root, ac_text="# PRD\n\n### AC-1 thing\n\n### AC-2 other\n")
        (task_dir / "clarifications.jsonl").write_text(
            json.dumps(
                {
                    "source": "final_confirmation",
                    "summary": "approved",
                    "response": "confirmed",
                    "at": "2026-07-28T10:00:01+08:00",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        completed = self.transition(task_dir)
        self.assertNotEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("rejected", payload["status"])
        codes = [issue["code"] for issue in payload["issues"]]
        self.assertIn("PRD_ACCEPTANCE_FORMAT_INVALID", codes)
        self.assertEqual("plan", json.loads((task_dir / "task.json").read_text(encoding="utf-8"))["meta"]["phase"])

    def test_plan_to_do_accepts_checkbox_style_acceptance(self) -> None:
        task_dir = make_task(
            self.root, ac_text="# PRD\n\n## 验收标准\n\n- [ ] AC-1: works\n- [ ] AC-2: verified\n"
        )
        (task_dir / "clarifications.jsonl").write_text(
            json.dumps(
                {
                    "source": "final_confirmation",
                    "summary": "approved",
                    "response": "confirmed",
                    "at": "2026-07-28T10:00:01+08:00",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        completed = self.transition(task_dir)
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("transitioned", payload["status"])
        self.assertEqual("do", json.loads((task_dir / "task.json").read_text(encoding="utf-8"))["meta"]["phase"])


if __name__ == "__main__":
    unittest.main()
