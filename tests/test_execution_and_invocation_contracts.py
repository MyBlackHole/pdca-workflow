from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pdca_runtime.tests.runtime_fixtures import make_runtime_root


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_CLI = ROOT / "scripts/pdca-runtime.py"


class ExecutionContractTest(unittest.TestCase):
    def test_runtime_cli_validates_role_and_four_field_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            completed = subprocess.run(
                [
                    "python3",
                    str(RUNTIME_CLI),
                    "--root",
                    str(root),
                    "--task-dir",
                    str(task_dir),
                    "validate-task",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("ontology_projection", payload["ontology_role"])
            self.assertRegex(payload["execution_contract_digest"], r"^sha256:[0-9a-f]{64}$")

    def test_legacy_control_contracts_and_resolvers_are_removed(self) -> None:
        removed = [
            "pdca/ai-" + "execution-contract.json",
            "pdca/ai-friendliness-" + "route-contract.json",
            "schemas/ai-" + "execution-contract.schema.json",
            "schemas/ai-friendliness-" + "route-contract.schema.json",
            "scripts/resolve-ai-" + "execution-contract.py",
            "scripts/resolve-ai-friendliness-" + "route.py",
        ]
        self.assertEqual([], [path for path in removed if (ROOT / path).exists()])


class InvocationContractTest(unittest.TestCase):
    def test_skill_invocation_contract_remains_separate_from_task_execution(self) -> None:
        contract = json.loads((ROOT / "pdca/skill-invocation-contract.json").read_text(encoding="utf-8"))
        self.assertEqual("pdca.skill-invocation-contract/v1", contract["schema"])
        runtime_source = (ROOT / "pdca_runtime/task.py").read_text(encoding="utf-8")
        self.assertNotIn("skill-invocation-contract", runtime_source)
        audit_source = (ROOT / "scripts/audit-skill-content.py").read_text(encoding="utf-8")
        self.assertIn("pdca/skill-invocation-contract.json", audit_source)


if __name__ == "__main__":
    unittest.main()
