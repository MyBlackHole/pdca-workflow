"""当前任务的先调研门禁回归测试。

口径：plan→do 只接受当前任务自身的合格 research-report；关联任务的 archive 状态不得代理当前任务准入。
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

PASSING_REPORT = """# R

```mermaid
graph TD
  A-->B
```
Source: https://example.com/a

```mermaid
sequenceDiagram
  A->>B: x
```
Source: https://example.com/b

```mermaid
stateDiagram-v2
  [*]-->S
```
Source: file:line

## 参考资料
- https://example.com/a
- https://example.com/b
"""


def make_task(
    task_dir: Path,
    task_id: str,
    slug: str,
    scenario: str,
    parent: str | None,
    children: list[str],
    exempt: bool = False,
    required_actions: list[str] | None = None,
    work_product: str = "implementation",
) -> None:
    meta: dict = {
        "phase": "plan",
        "active": True,
        "ontology_role": scenario,
        "created_at": "2026-09-09T10:00:00+08:00",
        "convergence": ["evidence ready"],
        "ontology_fragment": "ontology",
        "execution_contract": {
            "work_product": work_product,
            "required_actions": required_actions or ["implement change"],
            "constraints": [],
            "testable_signal": "tests pass",
        },
    }
    if exempt:
        meta["ontology_exempt"] = True
        meta["ontology_exempt_reason"] = "ontology自举任务豁免先调研门禁"
    task = {
        "id": task_id,
        "slug": slug,
        "title": f"fixture {task_id}",
        "parent": parent,
        "children": children,
        "status": "Pending",
        "meta": meta,
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
        "# PRD\n\n## 验收标准\n\n- [ ] AC-1 evidence ready\n", encoding="utf-8"
    )


def research_first_blocked(root: Path, task_dir: Path) -> bool:
    _phase, issues = gate_issues(root, task_dir)
    return any(i.code == "RESEARCH_FIRST_MISSING" for i in issues)


class ResearchFirstGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "ontology").mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _tasks(self, *specs: tuple) -> dict[str, Path]:
        out = {}
        for task_id, slug, scenario, parent, children, exempt in specs:
            d = self.root / "pdca/tasks" / slug
            make_task(d, task_id, slug, scenario, parent, children, exempt)
            out[task_id] = d
        return out

    def test_role_alone_does_not_imply_research(self) -> None:
        ds = self._tasks(("T9001", "0909-nodev", "ontology_projection", None, [], False))
        self.assertFalse(research_first_blocked(self.root, ds["T9001"]))

    def test_explicit_research_action_without_report_is_blocked(self) -> None:
        task_dir = self.root / "pdca/tasks/0909-explicit-research"
        make_task(
            task_dir,
            "T9010",
            "0909-explicit-research",
            "ontology_projection",
            None,
            [],
            required_actions=["执行技术调研", "implement change"],
        )
        self.assertTrue(research_first_blocked(self.root, task_dir))

    def test_archived_related_task_does_not_satisfy_current_task(self) -> None:
        ds = self._tasks(
            ("T9002", "0909-padev", "ontology_projection", None, ["T9003"], False),
            ("T9003", "0909-chres", "ontology_modeling", "T9002", [], False),
        )
        child = json.loads((ds["T9003"] / "task.json").read_text(encoding="utf-8"))
        child["meta"]["phase"] = "archive"
        (ds["T9003"] / "task.json").write_text(json.dumps(child), encoding="utf-8")
        parent = json.loads((ds["T9002"] / "task.json").read_text(encoding="utf-8"))
        parent["meta"]["execution_contract"]["required_actions"] = ["执行技术调研"]
        (ds["T9002"] / "task.json").write_text(json.dumps(parent), encoding="utf-8")
        self.assertTrue(research_first_blocked(self.root, ds["T9002"]))

    def test_dev_with_passing_report_passes(self) -> None:
        ds = self._tasks(("T9004", "0909-repdev", "ontology_projection", None, [], False))
        task = json.loads((ds["T9004"] / "task.json").read_text(encoding="utf-8"))
        task["meta"]["execution_contract"]["required_actions"] = ["perform research"]
        (ds["T9004"] / "task.json").write_text(json.dumps(task), encoding="utf-8")
        (ds["T9004"] / "research-report.md").write_text(PASSING_REPORT, encoding="utf-8")
        self.assertFalse(research_first_blocked(self.root, ds["T9004"]))

    def test_exempt_skips(self) -> None:
        ds = self._tasks(("T9005", "0909-exempt", "ontology_projection", None, [], True))
        self.assertFalse(research_first_blocked(self.root, ds["T9005"]))

    def test_research_producer_exempted(self) -> None:
        """T2103 生产者豁免：research票自身即调研，免自身门禁（他人引用仍须证据）。"""
        task_dir = self.root / "pdca/tasks/0909-resleaf"
        make_task(
            task_dir,
            "T9006",
            "0909-resleaf",
            "ontology_modeling",
            None,
            [],
            required_actions=["perform research"],
            work_product="research-report.md",
        )
        self.assertFalse(research_first_blocked(self.root, task_dir))


if __name__ == "__main__":
    unittest.main()
