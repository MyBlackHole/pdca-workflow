"""Keep centralized PDCA records out of recursive search results."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RG = shutil.which("rg")


def workspace_tmpdir() -> Path:
    """Resolve TMPDIR only when it points inside this checkout's tests tree."""
    configured = os.environ.get("TMPDIR", "")
    if not configured or not Path(configured).is_absolute():
        raise RuntimeError("Set TMPDIR to an absolute directory under the workspace tests/ before running tests")
    tests_root = (ROOT / "tests").resolve(strict=True)
    temp_root = Path(configured).resolve(strict=True)
    if temp_root != tests_root and tests_root not in temp_root.parents:
        raise RuntimeError(f"TMPDIR must resolve inside {tests_root}, got {temp_root}")
    return temp_root


def setUpModule() -> None:
    workspace_tmpdir()


class RecordsSearchGuardTests(unittest.TestCase):
    def test_recursive_ripgrep_hides_only_root_records_directory(self) -> None:
        if RG is None:
            self.skipTest("ripgrep is required to test OpenCode's search backend")

        ignore_file = ROOT / ".ignore"
        self.assertTrue(ignore_file.is_file(), "root .ignore must define the search boundary")

        with tempfile.TemporaryDirectory(prefix="pdca-search-guard-", dir=workspace_tmpdir()) as temporary:
            fixture = Path(temporary)
            shutil.copyfile(ignore_file, fixture / ".ignore")
            (fixture / "records").mkdir()
            (fixture / "docs" / "records").mkdir(parents=True)
            (fixture / "records" / "private.md").write_text("synthetic private marker\n", encoding="utf-8")
            (fixture / "docs" / "records" / "example.md").write_text("public fixture marker\n", encoding="utf-8")

            listed = subprocess.run(
                [RG, "--files", "--glob", "**/*.md"],
                cwd=fixture,
                check=True,
                capture_output=True,
                text=True,
            )
            paths = set(listed.stdout.splitlines())
            self.assertNotIn("records/private.md", paths)
            self.assertIn("docs/records/example.md", paths)

            searched = subprocess.run(
                [RG, "--files-with-matches", "--glob", "**/*.md", "marker"],
                cwd=fixture,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, searched.returncode, searched.stderr)
            self.assertEqual(["docs/records/example.md"], searched.stdout.splitlines())
