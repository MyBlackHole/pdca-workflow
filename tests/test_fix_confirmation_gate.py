"""fix_confirmation 门禁（T0542）契约测试。

证明 AC-1/AC-2：schema + CLI + skill 文本 + flow-do marker + execution-contract + audit 的完整链路
与 seam：tests/test_fix_confirmation_gate.py -> schemas/clarification.schema.json / scripts/append-confirmation.py / scripts/flow_audit.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIAG = ROOT / "ontology/domain/pdca/skill-diagnosing-bugs.md"
SKILL_ANALYSIS = ROOT / "ontology/domain/pdca/skill-bug-analysis.md"
SKILL_COMMIT = ROOT / "ontology/domain/pdca/skill-bug-commit-format.md"
FLOW_DO = ROOT / "ontology/process/flow-do.md"
SCHEMA = ROOT / "schemas/clarification.schema.json"
CLI = ROOT / "scripts/append-confirmation.py"
AUDIT = ROOT / "scripts/flow_audit.py"
EXEC_CONTRACT = ROOT / "pdca/ai-execution-contract.json"


class FixConfirmationSchemaContractTest(unittest.TestCase):
    def test_schema_has_fix_confirmation(self) -> None:
        data = json.loads(SCHEMA.read_text(encoding="utf-8"))
        text = SCHEMA.read_text(encoding="utf-8")
        self.assertIn("fix_confirmation", text)
        # 校验分支存在且 response 含 confirmed/rejected
        self.assertIn("confirmed", text)
        self.assertIn("rejected", text)

    def test_schema_validates_fix_confirmation_entry(self) -> None:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from pdca_core import schema_issues
        entry = {
            "source": "fix_confirmation",
            "summary": "根因X+方案Y+影响Z",
            "response": "confirmed",
            "at": "2026-09-04T10:00:00+08:00",
        }
        issues = schema_issues(ROOT, entry, "clarification.schema.json")
        self.assertEqual([], issues, f"schema should accept fix_confirmation: {issues}")
        bad = dict(entry, response="partial")
        issues2 = schema_issues(ROOT, bad, "clarification.schema.json")
        self.assertTrue(issues2, "fix_confirmation partial should be rejected")

    def test_cli_supports_fix_confirmation(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        self.assertIn("fix_confirmation", text)

    def test_cli_append_fix_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ontology/process").mkdir(parents=True)
            (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
            import shutil
            shutil.copytree(ROOT / "schemas", root / "schemas")
            task_dir = root / "pdca/tasks/0904-fix-confirmation-test"
            task_dir.mkdir(parents=True)
            (task_dir / "clarifications.jsonl").write_text("", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "--task-dir", str(task_dir), "--source", "fix_confirmation", "--response", "confirmed", "--summary", "根因A+方案B+影响C", "--root", str(root)],
                capture_output=True, text=True, cwd=ROOT,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            content = (task_dir / "clarifications.jsonl").read_text(encoding="utf-8")
            self.assertIn("fix_confirmation", content)
            self.assertIn("confirmed", content)


class FixConfirmationSkillContractTest(unittest.TestCase):
    def test_diagnosing_bugs_has_phase_45(self) -> None:
        text = SKILL_DIAG.read_text(encoding="utf-8")
        self.assertIn("Phase 4.5", text)
        self.assertIn("Fix Approval", text)
        self.assertIn("fix_confirmation", text)
        self.assertIn("append-confirmation.py", text)
        self.assertIn("captured:true", text)

    def test_diagnosing_bugs_requires_fix_before_code_change(self) -> None:
        text = SKILL_DIAG.read_text(encoding="utf-8")
        self.assertIn("fix_confirmation:confirmed", text)
        self.assertIn("禁止任何代码修改", text)

    def test_bug_analysis_has_fix_gate_and_science(self) -> None:
        text = SKILL_ANALYSIS.read_text(encoding="utf-8")
        self.assertIn("fix_confirmation", text)
        self.assertIn("根因≠现象", text)
        self.assertIn("假设/设计错误", text)
        self.assertIn("实现/环境错误", text)
        self.assertIn("流程/证据遗漏", text)
        self.assertIn("双向预测", text)

    def test_bug_commit_format_has_three_categories(self) -> None:
        text = SKILL_COMMIT.read_text(encoding="utf-8")
        self.assertIn("根因 ≠ 现象", text)
        self.assertIn("假设/设计错误", text)
        self.assertIn("实现/环境错误", text)
        self.assertIn("流程/证据遗漏", text)
        self.assertIn("fix_confirmation", text)


class FixConfirmationFlowContractTest(unittest.TestCase):
    def test_flow_do_has_fix_approval_marker(self) -> None:
        text = FLOW_DO.read_text(encoding="utf-8")
        self.assertIn("确认修复方案", text)
        # 顺序校验：确认修复方案 在 再做最小修复 之前
        self.assertLess(text.index("确认修复方案"), text.index("再做最小修复"))

    def test_execution_contract_has_fix_approval(self) -> None:
        data = json.loads(EXEC_CONTRACT.read_text(encoding="utf-8"))
        bugfix = next(r for r in data["routes"] if r["scenario"] == "bugfix")
        markers = [p["marker"] for p in bugfix["phases"]]
        self.assertIn("确认修复方案", markers)
        self.assertLess(markers.index("确认修复方案"), markers.index("再做最小修复"))
        ids = [p["id"] for p in bugfix["phases"]]
        self.assertIn("fix-approval", ids)

    def test_flow_audit_has_fix_confirmation_check(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        self.assertIn("fix-confirmation", text)
        self.assertIn("FIX_CONFIRMATION_MISSING", text)
        self.assertIn("fix_confirmation", text)

    def test_execution_contract_verify_document_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/resolve-ai-execution-contract.py"), "--verify-document", "--root", str(ROOT)],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
