"""TICKETS_MISSING叶票递归回归测试（T2084）。

口径：有parent无children的非research票为叶票，豁免TICKETS；无parent无children仍阻断；research单票不变。
"""
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
    scenario: str,
    parent: str | None,
    children: list[str],
) -> None:
    task = {
        "id": task_id,
        "slug": slug,
        "title": f"fixture {task_id}",
        "parent": parent,
        "children": children,
        "status": "Pending",
        "meta": {
            "phase": "plan",
            "active": True,
            "scenario_type": scenario,
            "created_at": "2026-09-09T10:00:00+08:00",
            "convergence": ["leaf converges"],
            "ontology_fragment": "ontology",
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
    (task_dir / "clarifications.jsonl").write_text(
        json.dumps(
            {
                "round": 1,
                "question": "scope",
                "answer": "ok",
                "source": "grilling",
                "captured": True,
                "at": "2026-09-09T10:00:01+08:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (task_dir / "prd.md").write_text(
        "# PRD\n\n## 验收标准\n\n- [ ] AC-1 leaf converges\n", encoding="utf-8"
    )


def tickets_blocked(root: Path, task_dir: Path) -> bool:
    _phase, issues = gate_issues(root, task_dir)
    return any(i.code == "TICKETS_MISSING" for i in issues)


class TicketsLeafGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_leaf_with_parent_exempted(self) -> None:
        d = self.root / "pdca/tasks/0909-leaf"
        make_task(d, "T9001", "0909-leaf", "development", "T9000", [])
        self.assertFalse(tickets_blocked(self.root, d))

    def test_parentless_without_children_blocked(self) -> None:
        d = self.root / "pdca/tasks/0909-root"
        make_task(d, "T9002", "0909-root", "development", None, [])
        self.assertTrue(tickets_blocked(self.root, d))

    def test_research_single_unchanged(self) -> None:
        d = self.root / "pdca/tasks/0909-res"
        make_task(d, "T9003", "0909-res", "research", None, [])
        self.assertFalse(tickets_blocked(self.root, d))


if __name__ == "__main__":
    unittest.main()
