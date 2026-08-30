from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# seam 契约锚点：被测模块 scripts/task_identity.py（task_identity.py 为被测模块）
SEAM_TARGET = "scripts/task_identity.py"


class TaskIdentityCliTest(unittest.TestCase):
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

    def create_command(self, slug: str, *extra: str) -> list[str]:
        return [
            "python3",
            str(ROOT / "scripts/task_identity.py"),
            "create",
            "--slug",
            slug,
            "--title",
            "identity fixture",
            "--scenario-type",
            "development",
            "--created-at",
            "2026-08-14T10:00:00+08:00",
            *extra,
            "--root",
            str(self.root),
        ]

    def run_create(self, slug: str, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(self.create_command(slug, *extra), capture_output=True, text=True)

    def test_create_task_assigns_unique_id_and_immutable_record_directory(self) -> None:
        completed = self.run_create("0814-identity-first")
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("created", payload["status"])
        task_id = payload["task_id"]
        self.assertRegex(task_id, r"^T[0-9]{4,}$")
        record = payload["record"]
        self.assertRegex(record, r"^T[0-9]{4,}-0814-identity-first$")

        task = json.loads((self.root / "pdca/tasks" / "0814-identity-first" / "task.json").read_text(encoding="utf-8"))
        self.assertEqual(task_id, task["id"])
        self.assertEqual(record, task["meta"]["record"])
        self.assertTrue((self.root / "records" / record).is_dir())

    def test_concurrent_create_keeps_task_ids_unique(self) -> None:
        processes = []
        for index in range(10):
            processes.append(
                subprocess.Popen(
                    self.create_command(f"0814-concurrent-{index:02d}"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            )
        outputs = [process.communicate() for process in processes]
        self.assertTrue(all(process.returncode == 0 for process in processes), outputs)

        task_ids = []
        for task_path in (self.root / "pdca/tasks").glob("**/task.json"):
            task_ids.append(json.loads(task_path.read_text(encoding="utf-8"))["id"])
        self.assertEqual(len(task_ids), len(set(task_ids)), "duplicate task IDs under concurrency")

    def test_duplicate_slug_is_rejected_without_regression(self) -> None:
        first = self.run_create("0814-dup-slug")
        self.assertEqual(0, first.returncode, first.stderr)
        second = self.run_create("0814-dup-slug")
        self.assertEqual(1, second.returncode)
        self.assertIn("TASK_PATH_CONFLICT", second.stderr)
        self.assertFalse((self.root / "pdca/tasks" / "0814-dup-slug-1").exists())

    def test_setting_an_inconsistent_record_is_rejected(self) -> None:
        completed = self.run_create("0814-record-lock", "--record", "T9999-wrong-record")
        self.assertEqual(1, completed.returncode)
        self.assertIn("RECORD_MISMATCH", completed.stderr)
        self.assertFalse((self.root / "pdca/tasks" / "0814-record-lock").exists())
        self.assertFalse((self.root / "records" / "T9999-wrong-record").exists())

    def test_failed_write_rolls_back_partial_files(self) -> None:
        first = self.run_create("0814-rollback")
        self.assertEqual(0, first.returncode, first.stderr)
        payload = json.loads(first.stdout)
        task_dir = self.root / "pdca/tasks" / "0814-rollback"
        (task_dir / "prd.md").unlink()
        record = payload["record"]
        (self.root / "records" / record).mkdir(parents=True, exist_ok=True)
        sealed = self.root / "records" / record / "conclusion.md"
        sealed.write_text("# conclusion\n", encoding="utf-8")
        conflict = self.root / "records" / record / "task.json"
        conflict.write_text("x", encoding="utf-8")

        second = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/task_identity.py"),
                "create",
                "--slug",
                "0814-rollback",
                "--title",
                "identity fixture",
                "--scenario-type",
                "development",
                "--created-at",
                "2026-08-14T10:00:00+08:00",
                "--record",
                record,
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(1, second.returncode, second.stdout)
        self.assertTrue(sealed.read_text(encoding="utf-8").startswith("# conclusion"))

    def test_create_task_accepts_explicit_convergence(self) -> None:
        completed = self.run_create(
            "0814-convergence",
            "--convergence",
            "hotspots 基于近 N 天 git log 频次返回高变更路径|HTML 报告写入任务目录可提交",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        task = json.loads((self.root / "pdca/tasks" / "0814-convergence" / "task.json").read_text(encoding="utf-8"))
        self.assertEqual(
            ["hotspots 基于近 N 天 git log 频次返回高变更路径", "HTML 报告写入任务目录可提交"],
            task["meta"]["convergence"],
        )

    def test_create_task_defaults_convergence_to_identity_invariant(self) -> None:
        completed = self.run_create("0814-convergence-default")
        self.assertEqual(0, completed.returncode, completed.stderr)
        task = json.loads(
            (self.root / "pdca/tasks" / "0814-convergence-default" / "task.json").read_text(encoding="utf-8")
        )
        self.assertEqual(["task identity is unique and immutable"], task["meta"]["convergence"])

    def _make_ontology_fragment(self) -> str:
        fragment = self.root / "ontology" / "concept"
        fragment.mkdir(parents=True)
        return "ontology/concept"

    def test_create_with_ontology_node_type_writes_meta(self) -> None:
        completed = self.run_create(
            "0814-ont-node",
            "--ontology-node-type",
            "concept",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        task = json.loads((self.root / "pdca/tasks" / "0814-ont-node" / "task.json").read_text(encoding="utf-8"))
        self.assertEqual("concept", task["meta"]["ontology_node_type"])

    def test_create_invalid_ontology_node_type_rejected(self) -> None:
        completed = self.run_create(
            "0814-ont-bad",
            "--ontology-node-type",
            "not-a-type",
        )
        self.assertEqual(1, completed.returncode)
        self.assertIn("ONTOLOGY_NODE_TYPE_INVALID", completed.stderr)

    def test_create_ontology_fragment_missing_dir_rejected(self) -> None:
        completed = self.run_create(
            "0814-ont-frag",
            "--ontology-fragment",
            "ontology/missing",
        )
        self.assertEqual(1, completed.returncode)
        self.assertIn("ONTOLOGY_FRAGMENT_MISSING", completed.stderr)

    def test_create_ontology_fragment_valid_dir_accepted(self) -> None:
        self._make_ontology_fragment()
        completed = self.run_create(
            "0814-ont-frag-ok",
            "--ontology-fragment",
            "ontology/concept",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        task = json.loads((self.root / "pdca/tasks" / "0814-ont-frag-ok" / "task.json").read_text(encoding="utf-8"))
        self.assertEqual("ontology/concept", task["meta"]["ontology_fragment"])

    def test_create_inherits_parent_ontology_meta(self) -> None:
        self._make_ontology_fragment()
        parent = self.run_create(
            "0814-ont-parent",
            "--ontology-fragment",
            "ontology/concept",
            "--ontology-node-type",
            "concept",
        )
        self.assertEqual(0, parent.returncode, parent.stderr)
        parent_id = json.loads(parent.stdout)["task_id"]
        child = self.run_create(
            "0814-ont-child",
            "--parent",
            parent_id,
        )
        self.assertEqual(0, child.returncode, child.stderr)
        child_task = json.loads((self.root / "pdca/tasks" / "0814-ont-child" / "task.json").read_text(encoding="utf-8"))
        self.assertEqual("ontology/concept", child_task["meta"]["ontology_fragment"])
        self.assertEqual("concept", child_task["meta"]["ontology_node_type"])

    def test_default_prd_has_ontology_section(self) -> None:
        completed = self.run_create("0814-prd-ont")
        self.assertEqual(0, completed.returncode, completed.stderr)
        prd = (self.root / "pdca/tasks" / "0814-prd-ont" / "prd.md").read_text(encoding="utf-8")
        self.assertIn("## 关联本体节点", prd)


if __name__ == "__main__":
    unittest.main()