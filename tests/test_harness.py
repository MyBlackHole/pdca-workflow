from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HarnessTest(unittest.TestCase):
    def test_all_deterministic_fixtures_pass(self) -> None:
        completed = subprocess.run(
            ["python3", "scripts/run-ai-friendliness-fixtures.py", "--all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(16, result["fixture_count"])
        self.assertEqual(0, result["failed"])

if __name__ == "__main__":
    unittest.main()
