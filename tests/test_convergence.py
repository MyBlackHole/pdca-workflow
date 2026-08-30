from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdca_core import convergence_issues, evidence_issues, gate_issues  # noqa: E402


class ConvergenceContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "ontology/process/flow-plan").mkdir(parents=True)
        (self.root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        self.task_dir = self.root / "pdca/tasks/0728-convergence-fixture"
        self.task_dir.mkdir(parents=True)
        self.record_dir = self.root / "records/R9001"
        self.evidence_dir = self.record_dir / "evidence"
        self.evidence_dir.mkdir(parents=True)
        self.task = {
            "id": "T9001",
            "slug": "0728-convergence-fixture",
            "title": "convergence fixture",
            "parent": None,
            "children": [],
            "status": "InProgress",
            "meta": {
                "phase": "do",
                "active": True,
                "scenario_type": "development",
                "created_at": "2026-07-28T10:00:00+08:00",
                "convergence": ["tests prove behavior", "gate rejects unsupported claims"],
                "record": "R9001",
            },
            "states": {
                "created": "2026-07-28T10:00:00+08:00",
                "plan": "2026-07-28T10:00:00+08:00",
                "do": "2026-07-28T10:01:00+08:00",
                "check": None,
                "act": None,
                "archive": None,
            },
        }
        (self.task_dir / "task.json").write_text(json.dumps(self.task), encoding="utf-8")
        (self.task_dir / "clarifications.jsonl").write_text(
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
        (self.task_dir / "prd.md").write_text(
            "# PRD\n\n## 验收标准\n\n- [ ] first behavior\n- [ ] second behavior\n\n## 范围外\n",
            encoding="utf-8",
        )
        self.write_artifact("unit-result", "unit.txt", "unit-test", ["AC-1"], b"unit pass\n")
        self.write_artifact("gate-result", "gate.txt", "integration-test", ["AC-2"], b"gate pass\n")
        mapping = {
            "schema": "pdca.convergence/v1",
            "items": [
                {
                    "index": 1,
                    "text": "tests prove behavior",
                    "criteria": ["AC-1"],
                    "evidence_ids": ["unit-result"],
                },
                {
                    "index": 2,
                    "text": "gate rejects unsupported claims",
                    "criteria": ["AC-2"],
                    "evidence_ids": ["gate-result"],
                },
            ],
        }
        raw = (json.dumps(mapping, ensure_ascii=False, indent=2) + "\n").encode()
        self.write_artifact("convergence-map", "convergence.json", "convergence-map", ["AC-1", "AC-2"], raw)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_artifact(
        self,
        evidence_id: str,
        filename: str,
        kind: str,
        criteria: list[str],
        content: bytes,
    ) -> None:
        artifact = self.evidence_dir / filename
        artifact.write_bytes(content)
        entry = {
            "id": evidence_id,
            "file": filename,
            "kind": kind,
            "size": len(content),
            "digest": "sha256:" + hashlib.sha256(content).hexdigest(),
            "at": "2026-07-28T10:02:00+08:00",
            "criteria": criteria,
        }
        with (self.evidence_dir / "manifest.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    def manifest(self) -> list[dict]:
        return [
            json.loads(line)
            for line in (self.evidence_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
        ]

    def write_manifest(self, entries: list[dict]) -> None:
        text = "".join(json.dumps(entry) + "\n" for entry in entries)
        (self.evidence_dir / "manifest.jsonl").write_text(text, encoding="utf-8")

    def mapping(self) -> dict:
        return json.loads((self.evidence_dir / "convergence.json").read_text(encoding="utf-8"))

    def write_mapping(self, mapping: dict) -> None:
        raw = (json.dumps(mapping, ensure_ascii=False, indent=2) + "\n").encode()
        (self.evidence_dir / "convergence.json").write_bytes(raw)
        entries = self.manifest()
        for entry in entries:
            if entry["id"] == "convergence-map":
                entry["size"] = len(raw)
                entry["digest"] = "sha256:" + hashlib.sha256(raw).hexdigest()
        self.write_manifest(entries)

    def codes(self) -> set[str]:
        return {issue.code for issue in convergence_issues(self.root, self.task_dir)}

    def test_complete_support_chain_is_valid(self) -> None:
        self.assertEqual([], convergence_issues(self.root, self.task_dir))

    def test_prd_without_canonical_checklist_is_rejected(self) -> None:
        (self.task_dir / "prd.md").write_text("# PRD\n\n## Tests\n\n- [ ] behavior\n", encoding="utf-8")
        self.assertIn("ACCEPTANCE_CRITERIA_MISSING", self.codes())

    def test_map_does_not_count_as_acceptance_evidence(self) -> None:
        entries = self.manifest()
        entries = [entry for entry in entries if entry["id"] != "gate-result"]
        self.write_manifest(entries)
        self.assertIn("ACCEPTANCE_CRITERION_UNCOVERED", self.codes())

    def test_missing_registered_map_is_rejected(self) -> None:
        entries = [entry for entry in self.manifest() if entry["id"] != "convergence-map"]
        self.write_manifest(entries)
        self.assertIn("CONVERGENCE_MAP_MISSING", self.codes())

    def test_wrong_map_kind_is_rejected(self) -> None:
        entries = self.manifest()
        for entry in entries:
            if entry["id"] == "convergence-map":
                entry["kind"] = "report"
        self.write_manifest(entries)
        self.assertIn("CONVERGENCE_MAP_MISSING", self.codes())

    def test_invalid_map_json_is_rejected(self) -> None:
        (self.evidence_dir / "convergence.json").write_text("{", encoding="utf-8")
        self.assertIn("CONVERGENCE_MAP_INVALID", self.codes())

    def test_map_schema_violation_is_rejected(self) -> None:
        mapping = self.mapping()
        mapping["extra"] = True
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_MAP_INVALID", self.codes())

    def test_missing_convergence_item_is_rejected(self) -> None:
        mapping = self.mapping()
        mapping["items"].pop()
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_ITEM_MISSING", self.codes())

    def test_duplicate_convergence_item_is_rejected(self) -> None:
        mapping = self.mapping()
        mapping["items"].append(dict(mapping["items"][0]))
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_ITEM_DUPLICATE", self.codes())

    def test_unknown_convergence_index_is_rejected(self) -> None:
        mapping = self.mapping()
        mapping["items"].append(
            {"index": 3, "text": "extra", "criteria": ["AC-1"], "evidence_ids": ["unit-result"]}
        )
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_ITEM_UNKNOWN", self.codes())

    def test_changed_plan_text_is_rejected(self) -> None:
        mapping = self.mapping()
        mapping["items"][0]["text"] = "changed"
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_TEXT_MISMATCH", self.codes())

    def test_unknown_criterion_is_rejected(self) -> None:
        mapping = self.mapping()
        mapping["items"][0]["criteria"] = ["AC-99"]
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_CRITERION_UNKNOWN", self.codes())

    def test_unknown_or_self_evidence_is_rejected(self) -> None:
        for evidence_id in ["missing-result", "convergence-map"]:
            with self.subTest(evidence_id=evidence_id):
                mapping = self.mapping()
                mapping["items"][0]["evidence_ids"] = [evidence_id]
                self.write_mapping(mapping)
                self.assertIn("CONVERGENCE_EVIDENCE_UNKNOWN", self.codes())

    def test_evidence_must_support_the_cited_criterion(self) -> None:
        mapping = self.mapping()
        mapping["items"][0]["criteria"] = ["AC-2"]
        mapping["items"][0]["evidence_ids"] = ["unit-result"]
        self.write_mapping(mapping)
        self.assertIn("CONVERGENCE_SUPPORT_MISSING", self.codes())

    def test_new_gate_rejects_error_accepted_by_evidence_gate(self) -> None:
        mapping = self.mapping()
        mapping["items"].pop()
        self.write_mapping(mapping)
        self.assertEqual([], evidence_issues(self.root, self.task))
        self.assertIn("CONVERGENCE_ITEM_MISSING", self.codes())

    def test_do_to_check_gate_uses_convergence_validation(self) -> None:
        mapping = self.mapping()
        mapping["items"].pop()
        self.write_mapping(mapping)
        phase, issues = gate_issues(self.root, self.task_dir)
        self.assertEqual("do", phase)
        self.assertIn("CONVERGENCE_ITEM_MISSING", {issue.code for issue in issues})

    def test_do_to_check_transition_fails_closed(self) -> None:
        mapping = self.mapping()
        mapping["items"].pop()
        self.write_mapping(mapping)
        completed = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/transition-phase.py"),
                str(self.task_dir),
                "--to",
                "check",
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(1, completed.returncode)
        self.assertIn(
            "CONVERGENCE_ITEM_MISSING",
            {item["code"] for item in json.loads(completed.stdout)["issues"]},
        )
        self.assertEqual("do", json.loads((self.task_dir / "task.json").read_text())["meta"]["phase"])

    def test_cli_reports_json_and_exit_status(self) -> None:
        command = [
            "python3",
            str(ROOT / "scripts/validate-convergence.py"),
            "--task-dir",
            str(self.task_dir),
            "--root",
            str(self.root),
        ]
        valid = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, valid.returncode)
        self.assertTrue(json.loads(valid.stdout)["valid"])
        mapping = self.mapping()
        mapping["items"].pop()
        self.write_mapping(mapping)
        invalid = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(1, invalid.returncode)
        self.assertIn("CONVERGENCE_ITEM_MISSING", {item["code"] for item in json.loads(invalid.stdout)["issues"]})


if __name__ == "__main__":
    unittest.main()
