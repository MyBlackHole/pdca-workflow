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
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
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

    def test_doctor_uses_explicit_fallbacks(self) -> None:
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PDCA_HOME", "PDCA_AGENT_SPAWN", "PDCA_NETWORK_FETCH"}
        }
        completed = subprocess.run(
            ["python3", "scripts/pdca-doctor.py", "--json"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertEqual("repository-fallback", result["pdca_home_source"])
        capabilities = {item["name"]: item for item in result["capabilities"]}
        self.assertEqual("execute-in-main-session", capabilities["agent.spawn"]["fallback"])
        self.assertEqual("filesystem-search", capabilities["context.retrieve"]["fallback"])

    def test_generated_index_is_current(self) -> None:
        subprocess.run(
            ["python3", "scripts/generate-skills-index.py", "--check"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_unrecoverable_history_requires_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            target = root / "pdca/tasks/archive/fixture"
            target.mkdir(parents=True)
            (target / "task.json").write_text("{}\n", encoding="utf-8")
            digest = hashlib.sha256()
            digest.update(b"task.json\0{}\n\0")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "pdca.deletion-manifest/v1",
                        "mode": "dry-run",
                        "scope": "archive",
                        "target_count": 1,
                        "targets": [
                            {
                                "path": "pdca/tasks/archive/fixture",
                                "digest": "sha256:" + digest.hexdigest(),
                                "git_recoverable": False,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/audit-history.py"),
                    "--apply",
                    str(manifest),
                    "--confirm-target-count",
                    "1",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("not recoverable by Git", completed.stderr)
            self.assertTrue(target.is_dir())

    def test_active_history_dry_run_excludes_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            active = root / "pdca/tasks/0728-invalid-active"
            archived = root / "pdca/tasks/archive/2026-07/0728-invalid-archive"
            active.mkdir(parents=True)
            archived.mkdir(parents=True)
            (active / "task.json").write_text("{}\n", encoding="utf-8")
            (archived / "task.json").write_text("{}\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
            subprocess.run(["git", "add", "pdca/tasks"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/audit-history.py"),
                    "--dry-run",
                    "--scope",
                    "active",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("active", payload["scope"])
            self.assertEqual(1, payload["target_count"])
            self.assertEqual("pdca/tasks/0728-invalid-active", payload["targets"][0]["path"])
            self.assertIn(payload["source_commit"], payload["targets"][0]["recovery"])

    def test_active_history_rejects_unsafe_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            for unsafe in [
                "pdca/tasks",
                "pdca/tasks/archive/fixture",
                "records/fixture",
                "knowledge/fixture",
                "pdca/journal/fixture",
                "pdca/tasks/*",
            ]:
                with self.subTest(path=unsafe):
                    manifest = root / "manifest.json"
                    manifest.write_text(
                        json.dumps(
                            {
                                "schema": "pdca.deletion-manifest/v1",
                                "mode": "dry-run",
                                "scope": "active",
                                "target_count": 1,
                                "targets": [
                                    {
                                        "path": unsafe,
                                        "digest": "sha256:" + "0" * 64,
                                        "git_recoverable": True,
                                    }
                                ],
                            }
                        ),
                        encoding="utf-8",
                    )
                    completed = subprocess.run(
                        [
                            "python3",
                            str(ROOT / "scripts/audit-history.py"),
                            "--apply",
                            str(manifest),
                            "--confirm-target-count",
                            "1",
                            "--root",
                            str(root),
                        ],
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(0, completed.returncode)

    def test_active_history_count_or_digest_mismatch_deletes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            target = root / "pdca/tasks/0728-invalid-active"
            target.mkdir(parents=True)
            (target / "task.json").write_text("{}\n", encoding="utf-8")
            manifest = root / "manifest.json"
            payload = {
                "schema": "pdca.deletion-manifest/v1",
                "mode": "dry-run",
                "scope": "active",
                "target_count": 1,
                "targets": [
                    {
                        "path": "pdca/tasks/0728-invalid-active",
                        "digest": directory_digest(target),
                        "git_recoverable": True,
                    }
                ],
            }
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            wrong_count = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/audit-history.py"),
                    "--apply",
                    str(manifest),
                    "--confirm-target-count",
                    "2",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, wrong_count.returncode)
            self.assertTrue(target.is_dir())
            (target / "task.json").write_text('{"changed":true}\n', encoding="utf-8")
            changed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/audit-history.py"),
                    "--apply",
                    str(manifest),
                    "--confirm-target-count",
                    "1",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, changed.returncode)
            self.assertTrue(target.is_dir())

    def test_active_history_apply_deletes_only_manifest_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            target = root / "pdca/tasks/0728-invalid-active"
            survivor = root / "pdca/tasks/0728-survivor"
            target.mkdir(parents=True)
            survivor.mkdir(parents=True)
            (target / "task.json").write_text("{}\n", encoding="utf-8")
            (survivor / "task.json").write_text("{}\n", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "pdca.deletion-manifest/v1",
                        "mode": "dry-run",
                        "scope": "active",
                        "target_count": 1,
                        "targets": [
                            {
                                "path": "pdca/tasks/0728-invalid-active",
                                "digest": directory_digest(target),
                                "git_recoverable": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/audit-history.py"),
                    "--apply",
                    str(manifest),
                    "--confirm-target-count",
                    "1",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertFalse(target.exists())
            self.assertTrue(survivor.is_dir())

    def test_active_history_apply_rejects_valid_task(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            target = root / "pdca/tasks/0728-valid-active"
            target.mkdir(parents=True)
            task = {
                "id": "T9999",
                "slug": "0728-valid-active",
                "title": "valid",
                "parent": None,
                "children": [],
                "status": "Pending",
                "meta": {
                    "phase": "plan",
                    "active": True,
                    "scenario_type": "development",
                    "created_at": "2026-07-28T10:00:00+08:00",
                    "convergence": ["valid task survives"],
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
            (target / "task.json").write_text(json.dumps(task), encoding="utf-8")
            (target / "clarifications.jsonl").write_text(
                json.dumps({"source": "triage", "at": "2026-07-28T10:00:00+08:00"}) + "\n",
                encoding="utf-8",
            )
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "pdca.deletion-manifest/v1",
                        "mode": "dry-run",
                        "scope": "active",
                        "target_count": 1,
                        "targets": [
                            {
                                "path": "pdca/tasks/0728-valid-active",
                                "digest": directory_digest(target),
                                "git_recoverable": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/audit-history.py"),
                    "--apply",
                    str(manifest),
                    "--confirm-target-count",
                    "1",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("valid strict task", completed.stderr)
            self.assertTrue(target.is_dir())

    def test_transition_is_adjacent_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
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
                    "scenario_type": "development",
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


if __name__ == "__main__":
    unittest.main()
