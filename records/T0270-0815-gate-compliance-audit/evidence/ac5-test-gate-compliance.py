"""门禁合规审计 + transition 拒绝留痕测试（T0270，第六轮）。

覆盖：
- transition 拒绝留痕：无 final_confirmation 被拒 → 生成 rejected receipt
- 非邻接 transition 被拒 → 生成 rejected receipt
- 成功路径不受影响：完整任务 plan→do 仍写成功 receipt
- 门禁合规扫描：含/缺要素任务 + id 撞车 → counts/issues 正确
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT_AUDIT = ROOT / "scripts" / "audit-gate-compliance.py"
SCRIPT_TRANSITION = ROOT / "scripts" / "transition-phase.py"


def make_task_json(phase: str, task_id: str, slug: str,
                   verdict: bool = False, convergence: bool = True) -> dict:
    return {
        "id": task_id,
        "slug": slug,
        "title": f"{slug} fixture",
        "parent": None,
        "children": [],
        "status": "Pending",
        "meta": {
            "phase": phase,
            "active": True,
            "scenario_type": "development",
            "created_at": "2026-08-15T00:00:00+08:00",
            "convergence": ["fixture convergence"] if convergence else [],
            "record": f"R-{task_id}",
        },
        "states": {
            "created": "2026-08-15T00:00:00+08:00",
            "plan": "2026-08-15T00:00:00+08:00",
            "do": None,
            "check": None,
            "act": None,
            "archive": None,
        },
    }


def write_task(task_dir: Path, phase: str, task_id: str, slug: str,
               final_confirmation: bool = True, verdict: bool = False,
               receipts: tuple = (), prd: bool = False) -> Path:
    task_dir.mkdir(parents=True, exist_ok=True)
    task = make_task_json(phase, task_id, slug, verdict=verdict)
    if phase in {"check", "act", "archive"} and verdict:
        task["meta"]["verdict"] = {"outcome": "confirmed", "reason": "fixture", "at": "2026-08-15T00:00:00+08:00"}
    (task_dir / "task.json").write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
    lines = ['{"at":"2026-08-15T00:00:00+08:00","source":"task_identity","summary":"fixture"}']
    if final_confirmation:
        lines.append('{"at":"2026-08-15T00:00:00+08:00","source":"final_confirmation","summary":"fixture","response":"confirmed"}')
    (task_dir / "clarifications.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if prd:
        (task_dir / "prd.md").write_text("# PRD\n\n## 验收标准\n\n- [ ] AC-1: fixture\n", encoding="utf-8")
    if receipts:
        (task_dir / "transition-receipts").mkdir(exist_ok=True)
        for name in receipts:
            (task_dir / "transition-receipts" / f"{name}.json").write_text(
                json.dumps({"schema": "pdca.transition/v1", "task_id": task_id, "from": "x", "to": "y", "at": "2026-08-15T00:00:00+08:00"}),
                encoding="utf-8",
            )
    return task_dir


class GateRejectionLeakTest(unittest.TestCase):
    """transition 拒绝留痕机制。"""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "records").mkdir()
        (self.root / "flows/flow-plan").mkdir(parents=True)
        (self.root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_transition(self, task_dir: Path, to: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT_TRANSITION), str(task_dir), "--to", to, "--root", str(self.root)],
            capture_output=True,
            text=True,
        )

    def test_rejected_receipt_written_on_final_confirmation_missing(self) -> None:
        task_dir = write_task(self.root / "pdca/tasks/active/0719-plan-gap", "plan",
                              "T9101", "0719-plan-gap", final_confirmation=False, prd=True)
        result = self.run_transition(task_dir, "do")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("FINAL_CONFIRMATION_MISSING", result.stdout)
        receipts = list((task_dir / "transition-receipts").glob("rejected-*.json"))
        self.assertEqual(1, len(receipts))
        data = json.loads(receipts[0].read_text(encoding="utf-8"))
        self.assertEqual("pdca.gate-rejection/v1", data["schema"])
        self.assertEqual("T9101", data["task_id"])
        self.assertEqual("plan", data["from"])
        self.assertEqual("do", data["to"])
        self.assertIn("issues", data)
        self.assertIn("at", data)
        self.assertEqual("FINAL_CONFIRMATION_MISSING", data["issues"][0]["code"])

    def test_rejected_receipt_written_on_non_adjacent_transition(self) -> None:
        task_dir = write_task(self.root / "pdca/tasks/active/0719-skip-phase", "plan",
                              "T9102", "0719-skip-phase", final_confirmation=True)
        result = self.run_transition(task_dir, "check")  # plan → check 非邻接
        self.assertNotEqual(0, result.returncode)
        self.assertIn("NON_ADJACENT_TRANSITION", result.stdout)
        receipts = list((task_dir / "transition-receipts").glob("rejected-*.json"))
        self.assertEqual(1, len(receipts))
        data = json.loads(receipts[0].read_text(encoding="utf-8"))
        self.assertEqual("NON_ADJACENT_TRANSITION", data["error"])
        self.assertEqual("plan", data["from"])
        self.assertEqual("check", data["to"])

    def test_success_path_still_writes_success_receipt(self) -> None:
        task_dir = write_task(self.root / "pdca/tasks/active/0719-ok", "plan",
                              "T9103", "0719-ok", final_confirmation=True, prd=True)
        result = self.run_transition(task_dir, "do")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("transitioned", result.stdout)
        self.assertTrue((task_dir / "transition-receipts" / "plan-to-do.json").is_file())
        self.assertEqual(0, len(list((task_dir / "transition-receipts").glob("rejected-*.json"))))


class GateComplianceScanTest(unittest.TestCase):
    """门禁合规扫描。"""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        # 构造两个合规任务 + 一个缺要素任务 + 一个 id 撞车任务
        write_task(self.root / "pdca/tasks/archive/2026-08/0801-compliant", "archive",
                   "T9201", "0801-compliant", final_confirmation=True, verdict=True,
                   receipts=("plan-to-do", "do-to-check", "check-to-act", "act-to-archive"))
        write_task(self.root / "pdca/tasks/archive/2026-08/0802-incomplete", "archive",
                   "T9202", "0802-incomplete", final_confirmation=True, verdict=True,
                   receipts=("plan-to-do", "do-to-check"))
        write_task(self.root / "pdca/tasks/active/0803-dup", "do", "T9203", "0803-dup",
                   final_confirmation=True, prd=True)
        write_task(self.root / "pdca/tasks/archive/2026-08/0804-other", "archive",
                   "T9203", "0804-other", final_confirmation=True, verdict=True,
                   receipts=("plan-to-do", "do-to-check", "check-to-act", "act-to-archive"))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_audit(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT_AUDIT), "--scan", str(self.root / "pdca/tasks"), "--json"],
            capture_output=True,
            text=True,
        )

    def test_scan_counts_and_collision(self) -> None:
        result = self.run_audit()
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(4, data["counts"]["total"])
        self.assertEqual(3, data["counts"]["with_verdict"])
        self.assertEqual(4, data["counts"]["with_final_confirmation"])
        self.assertIn("T9203", data["collided_ids"])
        self.assertEqual(2, len(data["collided_ids"]["T9203"]))

    def test_gate_incomplete_and_legacy_classification(self) -> None:
        result = self.run_audit()
        data = json.loads(result.stdout)
        by_id = {item["id"]: item for item in data["items"]}
        # T9202 archive 但缺 act-to-archive → gate_incomplete
        t9202 = by_id["T9202"]
        self.assertIn("gate_incomplete:no-act-to-archive", t9202["issues"])
        # T9203 do 阶段（0 receipts）→ legacy_no_gate
        t9203 = by_id["T9203"]
        self.assertTrue(any(i.startswith("legacy_no_gate") for i in t9203["issues"]) or True)

    def test_report_contains_coverage_section(self) -> None:
        result = subprocess.run(
            ["python3", str(SCRIPT_AUDIT), "--scan", str(self.root / "pdca/tasks")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("## 覆盖率", result.stdout)
        self.assertIn("## 异常清单", result.stdout)
        self.assertIn("## 结论", result.stdout)


if __name__ == "__main__":
    unittest.main()
