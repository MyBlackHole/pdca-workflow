import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ontology_tree_split as ots


def _write_ont(tmp_path):
    ont = tmp_path / "ont"
    (ont / "entity").mkdir(parents=True)
    (ont / "entity" / "parent.md").write_text(
        "---\nid: ontology:entity/parent\ntype: entity\nsummary: 父实体\n"
        "relations:\n  composed_of:\n    - ontology:entity/child\n---\n",
        encoding="utf-8",
    )
    (ont / "entity" / "child.md").write_text(
        "---\nid: ontology:entity/child\ntype: entity\nsummary: 子实体\n---\n",
        encoding="utf-8",
    )
    return ont


def _prd(tmp_path, body):
    p = tmp_path / "prd.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_generate_builds_wbs_with_node_type_and_deps(tmp_path):
    ont = _write_ont(tmp_path)
    prd = _prd(tmp_path, "# PRD\n## 拆分映射\n- 第一章 -> ontology:entity/parent\n")
    res = ots.generate(prd, ont)
    cands = res["candidates"]
    assert res["schema"] == "pdca.tree-split/v1"
    assert [c["slug_base"] for c in cands] == ["child", "parent"]
    child = cands[0]
    assert child["ontology_node_type"] == "entity"
    assert child["dependencies"] == []
    assert cands[1]["dependencies"] == ["child"]


def test_missing_node_raises(tmp_path):
    ont = _write_ont(tmp_path)
    prd = _prd(tmp_path, "# PRD\n## 拆分映射\n- X -> ontology:entity/nope\n")
    with pytest.raises(ValueError):
        ots.generate(prd, ont)


def test_cycle_raises(tmp_path):
    ont = tmp_path / "ont"
    (ont / "entity").mkdir(parents=True)
    (ont / "entity" / "a.md").write_text(
        "---\nid: ontology:entity/a\ntype: entity\nrelations:\n  composed_of:\n    - ontology:entity/b\n---\n",
        encoding="utf-8",
    )
    (ont / "entity" / "b.md").write_text(
        "---\nid: ontology:entity/b\ntype: entity\nrelations:\n  composed_of:\n    - ontology:entity/a\n---\n",
        encoding="utf-8",
    )
    prd = _prd(tmp_path, "# PRD\n## 拆分映射\n- X -> ontology:entity/a\n")
    with pytest.raises(ValueError):
        ots.generate(prd, ont)


def test_leaf_node_single_candidate(tmp_path):
    ont = _write_ont(tmp_path)
    prd = _prd(tmp_path, "# PRD\n## 拆分映射\n- Y -> ontology:entity/child\n")
    res = ots.generate(prd, ont)
    assert [c["slug_base"] for c in res["candidates"]] == ["child"]
    assert res["candidates"][0]["dependencies"] == []


def test_empty_map_raises(tmp_path):
    ont = _write_ont(tmp_path)
    prd = _prd(tmp_path, "# PRD\n## 拆分映射\n")
    with pytest.raises(ValueError):
        ots.generate(prd, ont)
