"""Keep OpenCode approval rules compatible with the pinned V1 and local V2 CLIs."""
from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OpenCodePermissionPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        cls.permission = cls.config.get("permission", {})

    def test_discovery_and_shell_tools_require_approval(self) -> None:
        self.assertNotIn("permissions", self.config, "V1.18.32 rejects the V2 permissions array")
        for action in ("glob", "grep", "list", "bash", "shell", "task", "subagent"):
            with self.subTest(action=action):
                self.assertEqual("ask", self.permission.get(action), f"missing {action} approval rule")

    def test_central_records_reads_and_edits_require_approval(self) -> None:
        for action in ("read", "edit"):
            rules = self.permission.get(action)
            self.assertIsInstance(rules, dict, f"{action} must use granular path rules")
            for resource in ("records", "records/**", "*/records", "*/records/**"):
                with self.subTest(action=action, resource=resource):
                    self.assertEqual("ask", rules.get(resource), f"missing {action} permission for {resource}")
