from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(file_path.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


class OperationsTest(unittest.TestCase):
    def test_register_evidence_computes_metadata_and_rejects_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ontology/process/flow-plan").mkdir(parents=True)
            (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            source = root / "artifact.txt"
            source.write_text("verified\n", encoding="utf-8")
            command = [
                "python3",
                str(ROOT / "scripts/register-evidence.py"),
                "--record",
                "R9001",
                "--source",
                str(source),
                "--id",
                "unit-result",
                "--kind",
                "test",
                "--criterion",
                "AC-1",
                "--root",
                str(root),
            ]
            first = subprocess.run(command, check=True, capture_output=True, text=True)
            result = json.loads(first.stdout)
            self.assertEqual("registered", result["status"])
            manifest = root / "records/R9001/evidence/manifest.jsonl"
            entry = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(["AC-1"], entry["criteria"])
            self.assertEqual(len(b"verified\n"), entry["size"])
            self.assertEqual("sha256:" + hashlib.sha256(b"verified\n").hexdigest(), entry["digest"])
            duplicate = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(0, duplicate.returncode)
            self.assertIn("duplicate evidence id", duplicate.stderr)

    def test_doctor_fails_closed_when_spawn_is_missing(self) -> None:
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PDCA_HOME", "PDCA_AGENT_SPAWN", "PDCA_NETWORK_FETCH"}
        }
        completed = subprocess.run(
            ["python3", "scripts/pdca-doctor.py", "--json"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertNotEqual(0, completed.returncode)
        self.assertFalse(result["valid"])
        self.assertEqual("repository-fallback", result["pdca_home_source"])
        capabilities = {item["name"]: item for item in result["capabilities"]}
        self.assertEqual("missing", capabilities["agent.spawn"]["status"])
        self.assertNotIn("fallback", capabilities["agent.spawn"])
        self.assertIn("agent.spawn", result["missing_required"])
        self.assertEqual("filesystem-search", capabilities["context.retrieve"]["fallback"])

    def test_doctor_reports_seam_contracts_segment(self) -> None:
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PDCA_HOME", "PDCA_AGENT_SPAWN", "PDCA_NETWORK_FETCH"}
        }
        environment["PDCA_AGENT_SPAWN"] = "available"
        completed = subprocess.run(
            ["python3", "scripts/pdca-doctor.py", "--json"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertIn("seam_contracts", result)
        self.assertIsInstance(result["seam_contracts"]["checked"], int)
        self.assertIsInstance(result["seam_contracts"]["issues"], dict)

    def test_doctor_invalid_when_seam_broken(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ontology/process/flow-plan").mkdir(parents=True)
            (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# AGENTS\n\nminimal fixture, no references.\n",
                encoding="utf-8",
            )
            shutil.copytree(ROOT / "schemas", root / "schemas")
            shutil.copytree(ROOT / "config", root / "config")
            (root / "records").mkdir()
            task_dir = root / "pdca/tasks/0809-broken-seam"
            task_dir.mkdir(parents=True)
            (task_dir / "prd.md").write_text(
                "# PRD\n\n### 声明的测试接缝\n\n- seam: tests/missing_test.py -> src/x.py\n",
                encoding="utf-8",
            )
            environment = {
                key: value
                for key, value in os.environ.items()
                if key not in {"PDCA_HOME", "PDCA_AGENT_SPAWN", "PDCA_NETWORK_FETCH"}
            }
            completed = subprocess.run(
                ["python3", "scripts/pdca-doctor.py", "--json", "--root", str(root)],
                env=environment,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertFalse(result["valid"])
            self.assertTrue(any(
                "测试文件缺失" in issue
                for issues in result["seam_contracts"]["issues"].values()
                for issue in issues
            ))
            self.assertNotEqual(0, completed.returncode)

    def test_generated_index_is_current(self) -> None:
        subprocess.run(
            ["python3", "scripts/generate-skills-index.py", "--check"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_transition_is_adjacent_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ontology/process/flow-plan").mkdir(parents=True)
            (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            (root / "records").mkdir()
            task_dir = root / "pdca/tasks/0728-transition-test"
            task_dir.mkdir(parents=True)
            task = {
                "id": "T9998",
                "slug": "0728-transition-test",
                "title": "transition fixture",
                "parent": None,
                "children": [],
                "status": "Pending",
                "meta": {
                    "phase": "plan",
                    "active": True,
                    "ontology_role": "ontology_projection",
                    "created_at": "2026-07-28T10:00:00+08:00",
                    "convergence": ["transition succeeds"],
                },
                "states": {
                    "created": "2026-07-28T10:00:00+08:00",
                    "plan": "2026-07-28T10:00:00+08:00",
                    "do": None,
                    "check": None,
                    "act": None,
                    "archive": None,
                },
            }
            (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
            (task_dir / "prd.md").write_text(
                "# PRD\n\n## 验收标准\n\n- [ ] AC-1: transition succeeds\n",
                encoding="utf-8",
            )
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(
                    {
                        "source": "final_confirmation",
                        "summary": "approved after grilling round 1",
                        "response": "confirmed",
                        "at": "2026-07-28T10:00:01+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            command = [
                "python3",
                str(ROOT / "scripts/transition-phase.py"),
                str(task_dir),
                "--to",
                "do",
                "--root",
                str(root),
            ]
            first = subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual("transitioned", json.loads(first.stdout)["status"])
            second = subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual("unchanged", json.loads(second.stdout)["status"])
            updated = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
            self.assertEqual("do", updated["meta"]["phase"])
            self.assertEqual("InProgress", updated["status"])
            self.assertTrue((task_dir / "transition-receipts/plan-to-do.json").is_file())
            sys.path.insert(0, str(ROOT / "scripts"))
            from pdca_core import task_issues

            self.assertEqual([], task_issues(root, task_dir, include_phase_requirements=False))


class PlanTimestampBackfillTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def _scaffold(self, root: Path, task_dir: Path, states: dict) -> None:
        (root / "ontology/process/flow-plan").mkdir(parents=True)
        (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
        shutil.copytree(ROOT / "schemas", root / "schemas")
        (root / "records").mkdir()
        task_dir.mkdir(parents=True)
        task = {
            "id": "T9999",
            "slug": "0809-backfill-test",
            "title": "backfill fixture",
            "parent": None,
            "children": [],
            "status": "Pending",
            "meta": {
                "phase": "plan",
                "active": True,
                "ontology_role": "ontology_projection",
                "created_at": "2026-07-28T10:00:00+08:00",
                "convergence": ["backfill succeeds"],
            },
            "states": states,
        }
        (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
        (task_dir / "prd.md").write_text(
            "# PRD\n\n## 验收标准\n\n- [ ] AC-1: backfill succeeds\n",
            encoding="utf-8",
        )

    def test_plan_backfilled_from_confirmation_moment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task_dir = root / "pdca/tasks/0809-backfill-test"
            self._scaffold(
                root,
                task_dir,
                {
                    "created": "2026-07-28T10:00:00+08:00",
                    "plan": None,
                    "do": None,
                    "check": None,
                    "act": None,
                    "archive": None,
                },
            )
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(
                    {
                        "source": "final_confirmation",
                        "summary": "approved after grilling round 1",
                        "response": "confirmed",
                        "at": "2026-07-28T10:05:00+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            command = [
                "python3",
                str(self.ROOT / "scripts/transition-phase.py"),
                str(task_dir),
                "--to",
                "do",
                "--root",
                str(root),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual("transitioned", json.loads(result.stdout)["status"])
            updated = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
            self.assertEqual("2026-07-28T10:05:00+08:00", updated["states"]["plan"])

    def test_plan_backfilled_to_now_without_confirmation(self) -> None:
        import importlib.util

        scripts_dir = self.ROOT / "scripts"
        sys.path.insert(0, str(scripts_dir))
        try:
            spec = importlib.util.spec_from_file_location(
                "transition_phase", scripts_dir / "transition-phase.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(str(scripts_dir))
        backfill_plan_timestamp = module.backfill_plan_timestamp

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task_dir = root / "pdca/tasks/0809-backfill-test"
            task_dir.mkdir(parents=True)
            task = {
                "id": "T9999",
                "slug": "0809-backfill-test",
                "title": "backfill fixture",
                "parent": None,
                "children": [],
                "status": "Pending",
                "meta": {"phase": "plan", "active": True, "ontology_role": "ontology_projection"},
                "states": {
                    "created": "2026-07-28T10:00:00+08:00",
                    "plan": None,
                    "do": None,
                    "check": None,
                    "act": None,
                    "archive": None,
                },
            }
            (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(
                    {
                        "source": "clarification",
                        "summary": "a question",
                        "response": "answered",
                        "at": "2026-07-28T10:01:00+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            value = backfill_plan_timestamp(task_dir, task, task_dir / "task.json")
            self.assertIsNotNone(value)
            updated = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
            self.assertIsNotNone(updated["states"]["plan"])

    def test_existing_plan_timestamp_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task_dir = root / "pdca/tasks/0809-backfill-test"
            self._scaffold(
                root,
                task_dir,
                {
                    "created": "2026-07-28T10:00:00+08:00",
                    "plan": "2026-07-28T10:02:00+08:00",
                    "do": None,
                    "check": None,
                    "act": None,
                    "archive": None,
                },
            )
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(
                    {
                        "source": "final_confirmation",
                        "summary": "approved after grilling round 1",
                        "response": "confirmed",
                        "at": "2026-07-28T10:05:00+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            command = [
                "python3",
                str(self.ROOT / "scripts/transition-phase.py"),
                str(task_dir),
                "--to",
                "do",
                "--root",
                str(root),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual("transitioned", json.loads(result.stdout)["status"])
            updated = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
            self.assertEqual("2026-07-28T10:02:00+08:00", updated["states"]["plan"])


if __name__ == "__main__":
    unittest.main()
