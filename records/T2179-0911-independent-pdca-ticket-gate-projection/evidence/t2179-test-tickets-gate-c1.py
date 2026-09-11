"""Independent PDCA tasks do not require decomposition for Plan admission."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdca_core import gate_issues  # noqa: E402


def make_task(
    task_dir: Path,
    task_id: str,
    slug: str,
    ontology_role: str,
) -> None:
    task = {
        "id": task_id,
        "slug": slug,
        "title": f"fixture {task_id}",
        "parent": None,
        "children": [],
        "dependencies": [],
        "status": "Pending",
        "meta": {
            "phase": "plan",
            "active": True,
            "ontology_role": ontology_role,
            "created_at": "2026-09-09T10:00:00+08:00",
            "convergence": ["independent task converges"],
            "ontology_fragment": "ontology",
            "ontology_exempt": True,
            "ontology_exempt_reason": "fixture isolates independent task admission",
        },
        "states": {
            "created": "2026-09-09T10:00:00+08:00",
            "plan": "2026-09-09T10:00:00+08:00",
            "do": None,
            "check": None,
            "act": None,
            "archive": None,
        },
    }
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
    clarifications = [
        {
            "round": 1,
            "question": "scope",
            "answer": "ok",
            "source": "grilling",
            "captured": True,
            "at": "2026-09-09T10:00:01+08:00",
        },
        {
            "source": "final_confirmation",
            "summary": "confirmed after grilling round 1",
            "response": "confirmed",
            "at": "2026-09-09T10:00:02+08:00",
            "verified": True,
        },
    ]
    (task_dir / "clarifications.jsonl").write_text(
        "".join(json.dumps(entry) + "\n" for entry in clarifications),
        encoding="utf-8",
    )
    (task_dir / "prd.md").write_text(
        "# PRD\n\n## 验收标准\n\n- [ ] AC-1 independent task converges\n",
        encoding="utf-8",
    )


class IndependentTicketsGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_parentless_tasks_without_children_pass_for_all_ontology_roles(self) -> None:
        roles = (
            "ontology_modeling",
            "ontology_projection",
            "ontology_conformance_verification",
        )
        for index, role in enumerate(roles, start=1):
            with self.subTest(ontology_role=role):
                task_dir = self.root / f"pdca/tasks/0909-independent-{index}"
                make_task(task_dir, f"T900{index}", task_dir.name, role)

                phase, issues = gate_issues(self.root, task_dir)

                self.assertEqual("plan", phase)
                self.assertEqual([], issues)


if __name__ == "__main__":
    unittest.main()
