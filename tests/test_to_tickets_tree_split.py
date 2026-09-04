import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ontology_tree_split as ots

SKILL = ROOT / "ontology" / "domain" / "pdca" / "skill-to-tickets.md"
SPEC = ROOT / "templates" / "to-spec" / "SPEC.md"


def test_to_tickets_skill_mentions_tree_split():
    text = SKILL.read_text(encoding="utf-8")
    assert "ontology_tree_split" in text
    assert "拆分映射" in text


def test_spec_template_has_split_map_section():
    text = SPEC.read_text(encoding="utf-8")
    assert "## 拆分映射" in text


def test_generate_triggered_on_map_declaration(tmp_path):
    ont = tmp_path / "ont"
    (ont / "entity").mkdir(parents=True)
    (ont / "entity" / "parent.md").write_text(
        "---\nid: ontology:entity/parent\ntype: entity\nrelations:\n  composed_of:\n    - ontology:entity/child\n---\n",
        encoding="utf-8",
    )
    (ont / "entity" / "child.md").write_text(
        "---\nid: ontology:entity/child\ntype: entity\n---\n",
        encoding="utf-8",
    )
    prd = tmp_path / "prd.md"
    prd.write_text(
        "# PRD\n## 拆分映射\n- 第一章 -> ontology:entity/parent\n",
        encoding="utf-8",
    )
    res = ots.generate(prd, ont)
    assert res["candidates"]
