"""writing-great-skills 增强（T0245）契约测试。

证明目标（AC-1..AC-5）：SKILL.md 的 L1-L4 杠杆以机器可读断言守护，
与 seam 契约（测试 -> ontology/domain/pdca/skill-writing-great-skills.md）一致。
同构先例：T0231 source 术语契约、T0233 seam 契约、T0243 diagnosing-bugs 契约。
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "ontology/domain/pdca/skill-writing-great-skills.md"


class LeadingWordsContractTest(unittest.TestCase):
    """L1 锚定词章节（AC-1）。"""

    def test_has_leading_words_section(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("锚定词", text)
        self.assertIn("leading words", text)

    def test_has_pretrained_word_examples(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("_tight_", text)
        self.assertIn("_red_", text)

    def test_has_madeup_word_caveat(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("不招募先验", text)


class PointerWordingContractTest(unittest.TestCase):
    """L2 指针措辞章节（AC-2）。"""

    def test_has_pointer_wording_section(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("指针措辞", text)

    def test_wording_over_target(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("措辞", text)
        self.assertIn("方差 bug", text)

    def test_has_leading_word_front_load(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("前置首词", text)


class TwoLoadsContractTest(unittest.TestCase):
    """L3 双负载章节（AC-3）。"""

    def test_has_two_loads_section(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("双负载", text)
        self.assertIn("context load", text)

    def test_has_cognitive_load(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("cognitive load", text)

    def test_progressive_disclosure_is_guard(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("保护信息层级", text)


class ModelRelativeNoopContractTest(unittest.TestCase):
    """L4 no-op 模型相对判定（AC-4）。"""

    def test_has_model_relative_test(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("模型相对", text)

    def test_has_stronger_word_replacement(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("_relentless_", text)

    def test_delete_whole_sentence(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("删整句", text)


class ExistingSectionsPreservedTest(unittest.TestCase):
    """CC-3 现有章节不破坏。"""

    def test_core_sections_still_present(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        for section in ("信息层级", "极简原则", "何时拆分", "完成标准", "失败模式"):
            self.assertIn(section, text)


if __name__ == "__main__":
    unittest.main()
