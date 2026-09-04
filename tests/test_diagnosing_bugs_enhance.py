"""diagnosing-bugs 增强（T0243）契约测试。

证明目标（AC-1..AC-7）：SKILL.md 的 D1-D6 落地点以机器可读断言守护，
与 seam 契约（测试 -> ontology/domain/pdca/skill-diagnosing-bugs.md）一致。
同构先例：T0231 source 术语契约、T0232 词汇契约、T0233 seam 契约。
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "ontology/domain/pdca/skill-diagnosing-bugs.md"
TEMPLATE = ROOT / "ontology/domain/diagnosing-bugs/hitl-loop.template.sh"


class DiagnosingBugsRedactContractTest(unittest.TestCase):
    """D1 Redact 安全前置（AC-1）。"""

    def test_has_redact_section(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Redact", text)
        self.assertIn("<REDACTED>", text)

    def test_credentials_stay_in_env(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("environment variables", text)
        self.assertIn("environment variables", text)

    def test_paste_only_load_bearing_lines(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("load-bearing lines", text)


class DiagnosingBugsStopGateContractTest(unittest.TestCase):
    """D3 无环显式停止门禁（AC-2）。"""

    def test_has_explicit_stop_when_no_loop(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Explicit stop", text)
        self.assertIn("Do NOT enter Phase 3", text)


class DiagnosingBugsNondeterminismContractTest(unittest.TestCase):
    """D2 非确定性 bug 指引（AC-3）。"""

    def test_has_nondeterministic_guidance(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Non-deterministic", text)
        self.assertIn("100×", text)


class DiagnosingBugsHitlContractTest(unittest.TestCase):
    """D4 HITL 模板（AC-4）。"""

    def test_skill_references_hitl_template(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("hitl-loop.template.sh", text)

    def test_hitl_template_file_exists(self) -> None:
        self.assertTrue(TEMPLATE.is_file())
        self.assertTrue(TEMPLATE.stat().st_mode & 0o111, "模板应可执行")


class DiagnosingBugsPostMortemContractTest(unittest.TestCase):
    """D5 post-mortem 架构移交（AC-5）。"""

    def test_has_architecture_handoff(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("improve-codebase-architecture", text)
        self.assertIn("would have prevented", text)


class DiagnosingBugsContextHypothesisContractTest(unittest.TestCase):
    """D6 CONTEXT 前置 + 双向预测（AC-6）。"""

    def test_has_context_read_prerequisite(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("CONTEXT.md", text)
        self.assertIn("ADR", text)

    def test_hypothesis_format_is_two_sided(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("make it worse", text)
        self.assertIn("disappear", text)


if __name__ == "__main__":
    unittest.main()
