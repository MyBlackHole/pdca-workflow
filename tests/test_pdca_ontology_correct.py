"""Tests for T0410: PDCA meta-ontology correctness vs canonical methodology."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scripts.ontology_reason import load_ontology  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
ONTO = REPO / "ontology"


def _read(rel: str) -> str:
    return (ONTO / rel).read_text(encoding="utf-8")


def test_continuous_improvement_node_exists():
    nodes = load_ontology(ONTO)
    node = nodes.get("ontology:concept/pdca-continuous-improvement")
    assert node is not None, "pdca-continuous-improvement 概念节点缺失"
    assert node.get("type") == "concept"
    assert "ontology:concept/pdca" in (node.get("relations", {}).get("specializes") or [])


def test_continuous_improvement_relates_act_plan():
    nodes = load_ontology(ONTO)
    rel = nodes["ontology:concept/pdca-continuous-improvement"].get("relations", {})
    relates = rel.get("relates_to") or []
    assert "ontology:entity/phase-act" in relates
    assert "ontology:entity/phase-plan" in relates


def test_pdca_phase_declares_four_canonical_phases():
    body = _read("concept/pdca-phase.md")
    assert "经典四阶段" in body
    assert "plan/do/check/act" in body.replace(" ", "")
    assert "archive 不是 PDCA 方法论阶段" in body


def test_pdca_phase_has_pdsa_note():
    body = _read("concept/pdca-phase.md")
    assert "PDSA" in body and "Study" in body


def test_archive_marked_as_operational_extension():
    body = _read("entity/phase-archive.md")
    assert "非 PDCA 方法论阶段" in body


def test_act_references_continuous_improvement():
    body = _read("entity/phase-act.md")
    assert "pdca-continuous-improvement" in body


def test_ontology_still_acyclic_after_correction():
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/ontology-validate.py"),
         "--ontology-dir", str(ONTO)],
        capture_output=True, text=True,
    )
    assert "CYCLE" not in (out.stdout + out.stderr)
    assert "DANGLING_REF" not in (out.stdout + out.stderr)
