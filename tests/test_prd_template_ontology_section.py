"""文档自检：PRD/SPEC 模板须含 `## 关联本体节点` 小节（T0415 AC-3）。"""

from pathlib import Path

import pytest

SPEC = Path(__file__).resolve().parents[1] / "templates" / "to-spec" / "SPEC.md"


def test_spec_template_has_ontology_node_section():
    assert SPEC.exists(), f"SPEC 模板缺失: {SPEC}"
    text = SPEC.read_text(encoding="utf-8")
    assert "## 关联本体节点" in text, "SPEC 模板缺少 `## 关联本体节点` 小节（AC-3）"
