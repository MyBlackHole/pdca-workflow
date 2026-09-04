from __future__ import annotations

import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DESIGN_SKILL = ROOT / "ontology" / "domain" / "pdca" / "skill-design-it-twice.md"

# 依赖分类 → 测试策略的确定性决策表（与 skill 文档契约一致）
DEPENDENCY_POLICY = {
    "in-process": "merge modules, test through the new interface directly, no adapter",
    "local-substitutable": "test with local stand-in, internal seam, no port at external interface",
    "remote-owned": "define a port at the seam, inject transport as adapter, test with in-memory adapter",
    "true-external": "inject external dependency as a port, tests provide a mock adapter",
}


class DeepeningDecisionTableTest(unittest.TestCase):
    """DEEPENING 依赖分类 → 测试策略的确定性决策表（T0266 增量 3）。"""

    def test_all_dependency_categories_have_strategy(self) -> None:
        self.assertEqual(
            {"in-process", "local-substitutable", "remote-owned", "true-external"},
            set(DEPENDENCY_POLICY.keys()),
        )
        for category, policy in DEPENDENCY_POLICY.items():
            self.assertTrue(policy, f"{category} must map to a non-empty strategy")

    def test_policy_maps_are_distinct(self) -> None:
        strategies = list(DEPENDENCY_POLICY.values())
        self.assertEqual(len(strategies), len(set(strategies)), "each category maps to a distinct strategy")


class DesignItTwiceDeepeningContractTest(unittest.TestCase):
    """design-it-twice 文档必须含 DEEPENING 深化测试策略（结构契约）。"""

    def test_document_contains_deletion_test(self) -> None:
        text = DESIGN_SKILL.read_text(encoding="utf-8")
        for marker in ("deletion test", "pass-through", "two adapters", "replace, don't layer", "interface is the test surface"):
            self.assertIn(marker, text, f"design-it-twice missing deepening marker: {marker}")

    def test_document_contains_seam_discipline(self) -> None:
        text = DESIGN_SKILL.read_text(encoding="utf-8")
        self.assertIn("one adapter", text)
        self.assertIn("two adapters", text)


if __name__ == "__main__":
    unittest.main()
