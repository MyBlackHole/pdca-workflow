"""Tests for T0412: meta-ontology as authoritative basis for the ontology-creation gate."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scripts.ontology_reason import load_ontology  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
ONTO = REPO / "ontology"

META_ROOT = "ontology:concept/meta-ontology"
GATE = "ontology:concept/ontology-creation-gate"
VALIDATOR = "ontology:concept/ontology-validate"
ASSET = "ontology:concept/ontology-asset"
RULE_CLASS = "ontology:concept/ontology-rule"
RULES = [
    "ontology:concept/ontology-rule-type-controlled",
    "ontology:concept/ontology-rule-non-dangling",
    "ontology:concept/ontology-rule-acyclic",
    "ontology:concept/ontology-rule-attr-testable",
    "ontology:concept/ontology-rule-richness",
    "ontology:concept/ontology-rule-guides-range",
]


def _nodes():
    return load_ontology(ONTO)


def test_meta_ontology_nodes_exist():
    n = _nodes()
    for node in [META_ROOT, GATE, VALIDATOR, ASSET, RULE_CLASS, *RULES]:
        assert node in n, f"缺失 meta-ontology 节点: {node}"
        assert n[node].get("type") == "concept"


def test_gate_has_authority_chain():
    n = _nodes()
    rel = n[GATE].get("relations", {})
    targets = set(rel.get("relates_to", []))
    assert VALIDATOR in targets, "gate 必须 relates_to validator"
    for r in RULES:
        assert r in targets, f"gate 必须 relates_to 规则节点 {r}"


def test_rules_specialize_rule_class():
    n = _nodes()
    for r in RULES:
        spec = n[r].get("relations", {}).get("specializes", [])
        assert RULE_CLASS in spec, f"{r} 应 specializes {RULE_CLASS}"


def test_meta_root_is_terminal_no_outgoing():
    n = _nodes()
    rel = n[META_ROOT].get("relations")
    assert rel is None or rel == {}, "meta-ontology 作为根不应向外指，以保证无环"


def test_ontology_still_valid_after_meta_ontology():
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/ontology-validate.py"),
         "--ontology-dir", str(ONTO)],
        capture_output=True, text=True,
    )
    assert "CYCLE" not in (out.stdout + out.stderr)
    assert "DANGLING_REF" not in (out.stdout + out.stderr)
