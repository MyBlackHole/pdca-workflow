from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FlowAuditTest(unittest.TestCase):
    def test_audit_confines_malicious_record_id_to_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            task_dir = root / "pdca/tasks/active/0730-path-audit"
            task_dir.mkdir(parents=True)
            task = {
                "id": "T9004",
                "slug": "0730-path-audit",
                "title": "path confinement fixture",
                "parent": None,
                "children": [],
                "status": "Pending",
                "meta": {
                    "phase": "plan",
                    "active": True,
                    "scenario_type": "development",
                    "created_at": "2026-07-30T10:00:00+08:00",
                    "convergence": ["audit stays confined"],
                    "record": "..",
                },
                "states": {
                    "created": "2026-07-30T10:00:00+08:00",
                    "plan": "2026-07-30T10:00:00+08:00",
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
                        "at": "2026-07-30T10:00:01+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/transition-phase.py"),
                    str(task_dir),
                    "--to",
                    "do",
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertFalse((root / "flow-audit.json").exists())
            self.assertTrue((root / "records/T9004/flow-audit.json").is_file())

    def test_cli_audits_all_transitions_and_preserves_failed_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "flows/flow-plan").mkdir(parents=True)
            (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
            shutil.copytree(ROOT / "schemas", root / "schemas")

            task_dir = root / "pdca/tasks/active/0730-flow-audit"
            task_dir.mkdir(parents=True)
            task = {
                "id": "T9002",
                "slug": "0730-flow-audit",
                "title": "flow audit fixture",
                "parent": None,
                "children": ["T9003"],
                "status": "Pending",
                "meta": {
                    "phase": "plan",
                    "active": True,
                    "scenario_type": "development",
                    "created_at": "2026-07-30T10:00:00+08:00",
                    "convergence": ["audit every transition"],
                    "record": "R9002",
                },
                "states": {
                    "created": "2026-07-30T10:00:00+08:00",
                    "plan": "2026-07-30T10:00:00+08:00",
                    "do": None,
                    "check": None,
                    "act": None,
                    "archive": None,
                },
            }
            task_path = task_dir / "task.json"
            task_path.write_text(json.dumps(task), encoding="utf-8")
            (task_dir / "prd.md").write_text(
                "# PRD\n\n## 验收标准\n- [ ] audit works\n", encoding="utf-8"
            )
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(
                    {
                        "source": "final_confirmation",
                        "summary": "approved",
                        "response": "confirmed",
                        "at": "2026-07-30T10:00:01+08:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            child_dir = root / "pdca/tasks/active/0730-inactive-child"
            child_dir.mkdir(parents=True)
            (child_dir / "task.json").write_text(
                json.dumps({"id": "T9003", "parent": "T9002", "meta": {"active": False}}),
                encoding="utf-8",
            )

            def transition(target: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [
                        "python3",
                        str(ROOT / "scripts/transition-phase.py"),
                        str(task_dir),
                        "--to",
                        target,
                        "--root",
                        str(root),
                    ],
                    capture_output=True,
                    text=True,
                )

            plan_result = transition("do")
            self.assertEqual(0, plan_result.returncode, plan_result.stderr)
            audit_path = root / "records/R9002/flow-audit.json"
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            plan_attempt = audit["transitions"]["plan-to-do"]["attempts"][0]
            self.assertFalse(plan_attempt["passed"])
            self.assertIn("CHILD_INACTIVE", {issue["code"] for issue in plan_attempt["issues"]})

            rejected = transition("check")
            self.assertNotEqual(0, rejected.returncode)
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            failed_attempt = audit["transitions"]["do-to-check"]["attempts"][0]
            self.assertFalse(failed_attempt["passed"])
            failed_checks = {check["id"]: check["passed"] for check in failed_attempt["checks"]}
            self.assertTrue(
                all(
                    not failed_checks[identifier]
                    for identifier in {
                        "evidence-registered",
                        "ac-coverage",
                        "evidence-integrity",
                        "convergence-map",
                    }
                )
            )

            evidence_dir = root / "records/R9002/evidence"
            evidence_dir.mkdir(parents=True)
            (evidence_dir / "manifest.jsonl").write_text("not-json\n", encoding="utf-8")
            malformed = transition("check")
            self.assertNotEqual(0, malformed.returncode)
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            malformed_checks = {
                check["id"]: check["passed"]
                for check in audit["transitions"]["do-to-check"]["latest"]["checks"]
            }
            self.assertFalse(malformed_checks["evidence-integrity"])

            result = evidence_dir / "result.txt"
            result.write_text("pass\n", encoding="utf-8")
            mapping = evidence_dir / "convergence.json"
            mapping.write_text(
                json.dumps(
                    {
                        "schema": "pdca.convergence/v1",
                        "items": [
                            {
                                "index": 1,
                                "text": "audit every transition",
                                "criteria": ["AC-1"],
                                "evidence_ids": ["result"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            def entry(identifier: str, file: Path, kind: str) -> dict:
                content = file.read_bytes()
                return {
                    "id": identifier,
                    "file": file.name,
                    "kind": kind,
                    "size": len(content),
                    "digest": "sha256:" + hashlib.sha256(content).hexdigest(),
                    "at": "2026-07-30T10:02:00+08:00",
                    "criteria": ["AC-1"],
                }

            (evidence_dir / "manifest.jsonl").write_text(
                json.dumps(entry("result", result, "test"))
                + "\n"
                + json.dumps(entry("convergence-map", mapping, "convergence-map"))
                + "\n",
                encoding="utf-8",
            )
            do_result = transition("check")
            self.assertEqual(0, do_result.returncode, do_result.stderr)

            task = json.loads(task_path.read_text(encoding="utf-8"))
            task["meta"]["verdict"] = {
                "outcome": "confirmed",
                "reason": "fixture passed",
                "verdict_id": "V9002",
                "at": "2026-07-30T10:03:00+08:00",
            }
            task_path.write_text(json.dumps(task), encoding="utf-8")
            (root / "records/R9002/conclusion.md").write_text("# conclusion\n", encoding="utf-8")
            with (task_dir / "clarifications.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "source": "check_confirmation",
                            "summary": "accepted",
                            "response": "confirmed",
                            "at": "2026-07-30T10:03:01+08:00",
                        }
                    )
                    + "\n"
                )
            check_result = transition("act")
            self.assertEqual(0, check_result.returncode, check_result.stderr)

            task = json.loads(task_path.read_text(encoding="utf-8"))
            task["meta"]["disposition"] = {
                "outcome": "task_only",
                "reason": "fixture only",
                "at": "2026-07-30T10:04:00+08:00",
            }
            task_path.write_text(json.dumps(task), encoding="utf-8")
            act_result = transition("archive")
            self.assertEqual(0, act_result.returncode, act_result.stderr)

            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {"plan-to-do", "do-to-check", "check-to-act", "act-to-archive"},
                set(audit["transitions"]),
            )
            self.assertEqual(3, len(audit["transitions"]["do-to-check"]["attempts"]))
            self.assertTrue(audit["transitions"]["do-to-check"]["latest"]["passed"])
            self.assertTrue(audit["transitions"]["check-to-act"]["latest"]["passed"])
            self.assertTrue(audit["transitions"]["act-to-archive"]["latest"]["passed"])


if __name__ == "__main__":
    unittest.main()
