from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCRIPT = "scripts/out-of-scope-manager.py"
TRIAGE = ROOT / "skills" / "triage-work" / "SKILL.md"


class OutOfScopeManagerTest(unittest.TestCase):
    """out-of-scope 知识库聚合状态机行为测试（T0266 增量 1）。"""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        self.dir = self.root / "out-of-scope"
        self.dir.mkdir()

    def tearDown(self) -> None:
        self._temp.cleanup()

    def run_manager(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", SCRIPT, "--dir", str(self.dir), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_add_creates_new_file_for_new_concept(self) -> None:
        result = self.run_manager(
            "add", "--concept", "dark-mode", "--reason", "渲染管线假设单一调色板",
            "--request", "#42 支持暗色模式",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        target = self.dir / "out-of-scope-dark-mode.md"
        self.assertTrue(target.is_file(), "new concept must create a new file")
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nschema: pdca.asset/v1\n"), "must emit ontology frontmatter")
        self.assertIn("type: domain", text)
        self.assertIn("# Dark Mode", text)
        self.assertIn("## Why this is out of scope", text)
        self.assertIn("## Prior requests", text)
        self.assertIn("#42", text)

    def test_add_same_concept_appends_existing_file(self) -> None:
        self.run_manager("add", "--concept", "dark-mode", "--reason", "渲染管线假设单一调色板", "--request", "#42")
        files_before = sorted(p.name for p in self.dir.glob("*.md"))
        result = self.run_manager(
            "add", "--concept", "dark-mode", "--reason", "渲染管线假设单一调色板", "--request", "#87",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        files_after = sorted(p.name for p in self.dir.glob("*.md"))
        self.assertEqual(files_before, files_after, "same concept must not create a new file")
        text = (self.dir / "out-of-scope-dark-mode.md").read_text(encoding="utf-8")
        self.assertIn("#42", text)
        self.assertIn("#87", text, "prior request must be appended")

    def test_add_different_concept_creates_separate_file(self) -> None:
        self.run_manager("add", "--concept", "dark-mode", "--reason", "r", "--request", "#42")
        self.run_manager("add", "--concept", "plugin-system", "--reason", "r", "--request", "#99")
        self.assertTrue((self.dir / "out-of-scope-dark-mode.md").is_file())
        self.assertTrue((self.dir / "out-of-scope-plugin-system.md").is_file())

    def test_implemented_rejection_does_not_write(self) -> None:
        result = self.run_manager(
            "add", "--concept", "dark-mode", "--reason", "已实现",
            "--request", "#42", "--implemented",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            0,
            len(list(self.dir.glob("*.md"))),
            "implemented rejection must not pollute out-of-scope",
        )
        payload = json.loads(result.stdout)
        self.assertEqual("rejected-implemented", payload["status"])

    def test_check_surfaces_prior_rejection(self) -> None:
        self.run_manager("add", "--concept", "dark-mode", "--reason", "渲染管线假设单一调色板", "--request", "#42")
        result = self.run_manager("check", "--concept", "dark-mode")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["match"], "check must surface matching prior rejection")
        self.assertEqual("out-of-scope-dark-mode.md", payload["file"])
        self.assertIn("渲染管线假设单一调色板", payload["reason"])


class TriageOutOfScopeContractTest(unittest.TestCase):
    """triage-work wontfix 分支必须描述概念聚合机制（结构契约）。"""

    def test_triage_describes_concept_aggregation(self) -> None:
        text = TRIAGE.read_text(encoding="utf-8")
        for marker in ("## Prior requests", "concept", "已实现", "dedup", "enhancement"):
            self.assertIn(marker, text, f"triage-work wontfix missing marker: {marker}")

    def test_triage_references_manager_script(self) -> None:
        text = TRIAGE.read_text(encoding="utf-8")
        self.assertIn("out-of-scope-manager.py", text)


if __name__ == "__main__":
    unittest.main()
