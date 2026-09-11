from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HarnessTest(unittest.TestCase):
    def test_runtime_cli_exposes_current_task_commands(self) -> None:
        completed = subprocess.run(
            ["python3", "scripts/pdca-runtime.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("prepare-dispatch", completed.stdout)
        self.assertIn("resume-conformance", completed.stdout)
        self.assertNotIn("poll", completed.stdout)


if __name__ == "__main__":
    unittest.main()
