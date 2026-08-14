from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# seam 契约锚点：三个 skill 文档均为被测文档（skills/ 目录）
SEAM_TARGET = "skills/"


class SkillsIncrementsTest(unittest.TestCase):
    """T0265 落地 mattpocock/skills 三个可证明增量——结构契约测试。"""

    def read_skill(self, name: str) -> str:
        path = ROOT / "skills" / name / "SKILL.md"
        self.assertTrue(path.is_file(), f"missing skill file: {path}")
        return path.read_text(encoding="utf-8")

    # ---- 增量 1：triage-work AGENT-BRIEF 模板 ----

    def test_triage_work_contains_agent_brief_template(self) -> None:
        text = self.read_skill("triage-work")
        for field in (
            "category",
            "scenario_type",
            "summary",
            "current behavior",
            "desired behavior",
            "key interfaces",
            "acceptance criteria",
            "out of scope",
            "information gaps",
            "dedup results",
            "recommended next steps",
        ):
            self.assertIn(field, text, f"triage-work template missing field: {field}")

    def test_triage_work_contains_checkable_quality_constraints(self) -> None:
        text = self.read_skill("triage-work")
        for constraint in (
            "运行 X 得到 Y",
            "durability over precision",
            "不写文件路径",
            "ready-to-plan",
        ):
            self.assertIn(constraint, text, f"triage-work missing quality constraint: {constraint}")

    # ---- 增量 2：to-tickets wide-refactor ----

    def test_to_tickets_contains_wide_refactor_branch(self) -> None:
        text = self.read_skill("to-tickets")
        for marker in ("expand", "分批迁移", "contract", "逐批", "CI 绿", "blast radius"):
            self.assertIn(marker, text, f"to-tickets missing wide-refactor marker: {marker}")

    def test_to_tickets_wide_refactor_specifies_dependency_edges(self) -> None:
        text = self.read_skill("to-tickets")
        self.assertIn("blocked by", text, "to-tickets wide-refactor must declare blocking edges")
        self.assertIn("expand", text)

    # ---- 增量 3：wayfinding-work claim 机制 ----

    def test_wayfinding_work_contains_claim_mechanism(self) -> None:
        text = self.read_skill("wayfinding-work")
        for marker in ("claimed-by", "in-progress", "unclaimed", "resolved"):
            self.assertIn(marker, text, f"wayfinding-work missing claim marker: {marker}")

    def test_wayfinding_work_claim_requires_claim_before_work(self) -> None:
        text = self.read_skill("wayfinding-work")
        claim_pos = text.find("claimed-by")
        execute_pos = text.find("### 3.")
        self.assertGreater(claim_pos, -1, "wayfinding-work must define claim")
        self.assertGreater(
            execute_pos,
            claim_pos,
            "claim must appear before execution step (并发 session 先认领再执行)",
        )


class TicketClaimStateMachineTest(unittest.TestCase):
    """wayfinding claim 状态机的冲突检测行为测试。"""

    def run_claims(self, *args: str, cwd: Path) -> subprocess.CompletedProcess:
        tickets_file = str(cwd / "tickets" / "claims.jsonl")
        return subprocess.run(
            ["python3", "scripts/check-ticket-claims.py", "--tickets", tickets_file, *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_claim_and_resolve_cycle(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "tickets").mkdir(parents=True)
        result = self.run_claims("claim", "--ticket", "TK-1", "--by", "sess-a", cwd=root)
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("claimed", payload["status"])
        self.assertEqual("TK-1", payload["ticket"])
        self.assertEqual("sess-a", payload["claimed_by"])
        self.assertEqual("in-progress", payload["state"])

    def test_conflicting_claim_is_rejected(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "tickets").mkdir(parents=True)
        first = self.run_claims("claim", "--ticket", "TK-1", "--by", "sess-a", cwd=root)
        self.assertEqual(0, first.returncode, first.stderr)
        second = self.run_claims("claim", "--ticket", "TK-1", "--by", "sess-b", cwd=root)
        self.assertEqual(1, second.returncode)
        self.assertIn("ALREADY_CLAIMED", second.stderr)

    def test_resolve_clears_claim_and_allows_reclaim(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "tickets").mkdir(parents=True)
        self.run_claims("claim", "--ticket", "TK-1", "--by", "sess-a", cwd=root)
        resolve = self.run_claims("resolve", "--ticket", "TK-1", "--by", "sess-a", cwd=root)
        self.assertEqual(0, resolve.returncode, resolve.stderr)
        reclaim = self.run_claims("claim", "--ticket", "TK-1", "--by", "sess-c", cwd=root)
        self.assertEqual(0, reclaim.returncode, reclaim.stderr)

    def test_resolve_by_non_claimant_is_rejected(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "tickets").mkdir(parents=True)
        self.run_claims("claim", "--ticket", "TK-1", "--by", "sess-a", cwd=root)
        resolve = self.run_claims("resolve", "--ticket", "TK-1", "--by", "sess-b", cwd=root)
        self.assertEqual(1, resolve.returncode)
        self.assertIn("NOT_CLAIMANT", resolve.stderr)


if __name__ == "__main__":
    unittest.main()
