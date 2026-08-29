"""T0413: prove ontology-validate.py reads rule parameters from ontology-rule-* nodes.

These tests demonstrate that the validator's behavior is driven by the meta-ontology
rule nodes (the ontology is the authority), not by hardcoded constants. The script
is invoked via its CLI (`scripts/ontology-validate.py --ontology-dir`) to exercise the
real entry point (which calls sys.exit on missing rule nodes).
"""
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ONT = REPO / "ontology"
SCRIPT = REPO / "scripts" / "ontology-validate.py"


def _copy_ontology(tmp_path: Path) -> Path:
    dst = tmp_path / "ontology"
    shutil.copytree(ONT, dst)
    return dst


def _edit_rule_spec(ont_dir: Path, rule_id: str, mutate):
    fname = rule_id.split("/")[-1] + ".md"
    p = ont_dir / "concept" / fname
    parts = p.read_text(encoding="utf-8").split("---", 2)
    fm = yaml.safe_load(parts[1])
    mutate(fm["rule_spec"])
    new_fm = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
    p.write_text("---\n" + new_fm + "---\n" + parts[2], encoding="utf-8")


def _run(ont_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--ontology-dir", str(ont_dir)],
        capture_output=True, text=True,
    )


def test_real_ontology_still_passes():
    r = _run(ONT)
    assert r.returncode == 0, r.stdout + r.stderr


def test_remove_concept_from_allowed_types_rejects_existing_concept_nodes():
    # 删除 rule 节点 allowed_types 中的 'concept' → 现有 concept 节点应被 TYPE_VOCAB 拒绝，
    # 证明 validator 读取节点参数而非硬编码。
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        _edit_rule_spec(ont, "ontology:concept/ontology-rule-type-controlled",
                        lambda rs: rs["allowed_types"].remove("concept"))
        r = _run(ont)
    assert r.returncode != 0
    assert "TYPE_VOCAB" in (r.stdout + r.stderr)
    assert "concept" in (r.stdout + r.stderr)


def test_add_custom_type_to_allowed_types_accepts_new_node():
    # 在 rule 节点 allowed_types 增加 'widget' 并新建 widget 节点 → 该类型被接受，
    # 证明“改节点即改校验行为”。
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        _edit_rule_spec(ont, "ontology:concept/ontology-rule-type-controlled",
                        lambda rs: rs["allowed_types"].append("widget"))
        widget_dir = ont / "widget"
        widget_dir.mkdir()
        (widget_dir / "w1.md").write_text(
            "---\n"
            "schema: pdca.asset/v1\n"
            "id: ontology:widget/w1\n"
            "type: widget\n"
            "layer: Knowledge\n"
            "summary: t\n"
            "status: active\n"
            "relations:\n"
            "  specializes:\n"
            "  - ontology:concept/meta-ontology\n"
            "---\n# w1\n",
            encoding="utf-8",
        )
        r = _run(ont)
    assert "TYPE_VOCAB" not in (r.stdout + r.stderr), r.stdout + r.stderr


def test_missing_rule_node_exits_with_error():
    # 删除任一 rule 节点 → validator 以非零退出（本体为权威，不允许静默回退）。
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        (ont / "concept" / "ontology-rule-type-controlled.md").unlink()
        r = _run(ont)
    assert r.returncode != 0
    assert "ERROR" in (r.stdout + r.stderr)


def test_change_knowledge_types_toggles_richness_check():
    # 把 richness 节点的 knowledge_types 改为仅 ['decision'] → 非 decision 知识资产不再被
    # 富度检查约束；新建一个无 guides/relates_to 的 pattern 节点不应触发 NO_GUIDES。
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        _edit_rule_spec(ont, "ontology:concept/ontology-rule-richness",
                        lambda rs: rs.__setitem__("knowledge_types", ["decision"]))
        pat_dir = ont / "pattern"
        pat_dir.mkdir(exist_ok=True)
        (pat_dir / "orphan.md").write_text(
            "---\n"
            "schema: pdca.asset/v1\n"
            "id: ontology:pattern/orphan\n"
            "type: pattern\n"
            "layer: Knowledge\n"
            "summary: t\n"
            "status: active\n"
            "relations:\n"
            "  specializes:\n"
            "  - ontology:concept/meta-ontology\n"
            "---\n# orphan\n",
            encoding="utf-8",
        )
        r = _run(ont)
    assert "NO_GUIDES" not in (r.stdout + r.stderr), r.stdout + r.stderr
