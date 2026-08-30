"""PRD seam 契约测试。

证明目标（AC-1..AC-6）：flow-plan 的 P3.5 seam 确认步骤 + SPEC.md
`### 声明的测试接缝` 清单 + 契约测试（声明的测试文件存在、被测模块一致），
把"PRD 声明的测试接缝 vs 实际测试"做成可回归验证的一致性契约。

同构先例：T0231 source 术语契约、T0232 词汇契约（机器可读 + 契约测试守护）。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.seam_contract import parse_seams  # noqa: E402


class SeamParseTest(unittest.TestCase):
    def test_parse_seam_line(self) -> None:
        text = "### 声明的测试接缝\n- seam: tests/test_foo.py -> src/foo.py\n"
        self.assertEqual(parse_seams(text), [("tests/test_foo.py", "src/foo.py")])

    def test_parse_multiple_seams(self) -> None:
        text = (
            "### 声明的测试接缝\n"
            "- seam: tests/test_foo.py -> src/foo.py\n"
            "- seam: tests/test_bar.py -> src/bar.py\n"
        )
        self.assertEqual(
            parse_seams(text),
            [("tests/test_foo.py", "src/foo.py"), ("tests/test_bar.py", "src/bar.py")],
        )

    def test_no_seam_lines_returns_empty(self) -> None:
        # 无 seam 行的 spec（历史 spec 追溯策略）→ 跳过
        self.assertEqual(parse_seams("## Seam 分析\n### 测试接缝\n自由文本描述\n"), [])

    def test_seam_line_with_extra_whitespace(self) -> None:
        text = "-    seam:   tests/a.py   ->   src/b.py   \n"
        self.assertEqual(parse_seams(text), [("tests/a.py", "src/b.py")])

    def test_non_seam_lines_ignored(self) -> None:
        text = "- 普通列表项\n- seam: tests/ok.py -> src/ok.py\n- seam 无箭头\n"
        self.assertEqual(parse_seams(text), [("tests/ok.py", "src/ok.py")])


class SeamFileExistenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = Path(__file__).resolve().parent / "_seam_tmp"

    def tearDown(self) -> None:
        import shutil

        if self.temporary.exists():
            shutil.rmtree(self.temporary)

    def _write_spec(self, seams: list[tuple[str, str]]) -> Path:
        spec = self.temporary / "prd.md"
        spec.parent.mkdir(parents=True, exist_ok=True)
        body = "### 声明的测试接缝\n" + "\n".join(f"- seam: {t} -> {m}" for t, m in seams) + "\n"
        spec.write_text(body, encoding="utf-8")
        return spec

    def test_declared_test_file_exists(self) -> None:
        # seam 指向存在的测试文件且引用被测模块 → 通过
        (self.temporary / "tests").mkdir(parents=True)
        (self.temporary / "tests/test_foo.py").write_text(
            "from src.foo import f\n", encoding="utf-8"
        )
        spec = self._write_spec([("tests/test_foo.py", "src/foo.py")])
        from scripts.seam_contract import validate_seams

        issues = validate_seams(spec, self.temporary)
        self.assertEqual(issues, [])

    def test_missing_test_file_fails(self) -> None:
        # seam 指向不存在的测试文件 → 失败
        spec = self._write_spec([("tests/ghost.py", "src/foo.py")])
        from scripts.seam_contract import validate_seams

        issues = validate_seams(spec, self.temporary)
        self.assertEqual(len(issues), 1)
        self.assertIn("tests/ghost.py", issues[0])

    def test_target_module_consistency(self) -> None:
        # 测试文件存在但被测模块未声明的一致 → 通过（文件级契约）
        (self.temporary / "tests").mkdir(parents=True)
        (self.temporary / "tests/test_foo.py").write_text("from src.foo import f", encoding="utf-8")
        spec = self._write_spec([("tests/test_foo.py", "src/foo.py")])
        from scripts.seam_contract import validate_seams

        issues = validate_seams(spec, self.temporary)
        self.assertEqual(issues, [])

    def test_missing_target_reference_fails(self) -> None:
        # 测试文件存在但未引用声明的被测模块 → 失败（AC-4 失败路径）
        (self.temporary / "tests").mkdir(parents=True)
        (self.temporary / "tests/test_foo.py").write_text(
            "from src.other import f\n", encoding="utf-8"
        )
        spec = self._write_spec([("tests/test_foo.py", "src/foo.py")])
        from scripts.seam_contract import validate_seams

        issues = validate_seams(spec, self.temporary)
        self.assertEqual(len(issues), 1)
        self.assertIn("src/foo.py", issues[0])


class FlowPlanSeamGateTest(unittest.TestCase):
    def test_flow_plan_has_p3_5(self) -> None:
        text = (ROOT / "ontology/process/flow-plan.md").read_text(encoding="utf-8")
        self.assertIn("P3.5", text)
        self.assertIn("声明的测试接缝", text)

    def test_flow_plan_p6_gate_checks_seams(self) -> None:
        text = (ROOT / "ontology/process/flow-plan.md").read_text(encoding="utf-8")
        self.assertIn("声明的测试接缝", text)


class SpecTemplateSeamSectionTest(unittest.TestCase):
    def test_spec_template_has_declared_seams_subsection(self) -> None:
        text = (ROOT / "templates/to-spec/SPEC.md").read_text(encoding="utf-8")
        self.assertIn("### 声明的测试接缝", text)
        self.assertIn("- seam: <测试文件路径> -> <被测模块路径>", text)


if __name__ == "__main__":
    unittest.main()
