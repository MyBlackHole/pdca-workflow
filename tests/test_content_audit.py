from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContentAuditTest(unittest.TestCase):
    def run_audit(self) -> dict:
        completed = subprocess.run(
            [
                "python3",
                "scripts/audit-skill-content.py",
                "--format",
                "json",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def test_metrics_are_deterministic(self) -> None:
        first = self.run_audit()
        second = self.run_audit()
        self.assertEqual(first, second)
        self.assertEqual("bytes", first["cost_metric"])
        self.assertEqual(0, first["totals"]["broken_references"])


if __name__ == "__main__":
    unittest.main()
