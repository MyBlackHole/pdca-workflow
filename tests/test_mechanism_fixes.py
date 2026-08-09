"""T0238 机制修正测试。

seam: tests/test_mechanism_fixes.py -> scripts/check-design-vocab.py
seam: tests/test_mechanism_fixes.py -> scripts/pdca_core.py

覆盖：
- check-design-vocab --doc-type 场景限定（design 检查 / other 跳过）
- STATE_TIME_ORDER 触发时的 guidance 断言
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdca_core import timeline_issues  # noqa: E402

VOCAB_SCRIPT = ROOT / "scripts/check-design-vocab.py"

DESIGN_TEXT = "我们设计了一个 deep module，接口是 module 的 interface，放在 seam 上。"
FORBIDDEN_TEXT = "这是 component 的 API boundary 和 service。"


def run_vocab(text: str, doc_type: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(VOCAB_SCRIPT), "--doc-type", doc_type],
        input=text,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.splitlines()[-1])


class DesignVocabScopedTest(unittest.TestCase):
    def test_default_doc_type_is_design(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VOCAB_SCRIPT)],
            input=DESIGN_TEXT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        result = json.loads(proc.stdout.splitlines()[-1])
        self.assertTrue(result["vocab_ok"])
        self.assertFalse(result["skipped"])
        self.assertEqual(result["doc_type"], "design")

    def test_design_doc_type_checks_forbidden_terms(self) -> None:
        result = run_vocab(FORBIDDEN_TEXT, "design")
        self.assertFalse(result["vocab_ok"])
        self.assertFalse(result["skipped"])
        for term in ("component", "API", "boundary", "service"):
            self.assertIn(term, result["violations"])

    def test_design_doc_type_accepts_vocab_terms(self) -> None:
        result = run_vocab(DESIGN_TEXT, "design")
        self.assertTrue(result["vocab_ok"])
        self.assertEqual(result["violations"], [])

    def test_other_doc_type_skips_check(self) -> None:
        result = run_vocab(FORBIDDEN_TEXT, "other")
        self.assertTrue(result["vocab_ok"])
        self.assertEqual(result["violations"], [])
        self.assertTrue(result["skipped"])
        self.assertEqual(result["doc_type"], "other")

    def test_other_doc_type_does_not_misreport_prd_text(self) -> None:
        prd_text = "服务端提供 API 供客户端调用，边界 clear。"
        result = run_vocab(prd_text, "other")
        self.assertTrue(result["vocab_ok"])
        self.assertEqual(result["violations"], [])


class StateTimeOrderGuidanceTest(unittest.TestCase):
    def _make_task(self, plan: str, do: str) -> dict:
        return {
            "id": "T9001",
            "slug": "2026-0809-tmp-time-order",
            "title": "time order test",
            "parent": None,
            "children": [],
            "status": "InProgress",
            "meta": {
                "phase": "do",
                "active": True,
                "scenario_type": "development",
                "created_at": "2026-07-28T09:00:00+08:00",
                "convergence": ["T9001"],
            },
            "states": {
                "created": "2026-07-28T09:00:00+08:00",
                "plan": plan,
                "do": do,
                "check": None,
                "act": None,
                "archive": None,
            },
        }

    def _issues_for(self, task: dict) -> list:
        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td) / "task"
            task_dir.mkdir()
            (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
            return timeline_issues(ROOT, task_dir)

    def test_out_of_order_timestamps_report_guidance(self) -> None:
        task = self._make_task(
            plan="2026-07-28T10:00:00.500000+08:00",  # 带微秒，晚于 do
            do="2026-07-28T10:00:00+08:00",  # 无微秒，更早
        )
        issues = self._issues_for(task)
        order = [i for i in issues if i.code == "STATE_TIME_ORDER"]
        self.assertEqual(len(order), 1)
        self.assertIn("transition-phase", order[0].guidance)
        self.assertIn("never hand-write states timestamps", order[0].guidance)

    def test_ordered_timestamps_have_no_issue(self) -> None:
        task = self._make_task(
            plan="2026-07-28T10:00:00+08:00",
            do="2026-07-28T10:01:00+08:00",
        )
        order = [i for i in self._issues_for(task) if i.code == "STATE_TIME_ORDER"]
        self.assertEqual(order, [])


if __name__ == "__main__":
    unittest.main()
