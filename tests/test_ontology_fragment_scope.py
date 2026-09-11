"""T0457 AC: ontology_fragment 强制范围扩展至 research/design/review。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from scripts.ontology_gate import ontology_ready_issues  # noqa: E402


def _root() -> Path:
    return REPO


def test_research_missing_blocked():
    root = _root()
    for scen in ("ontology_modeling", "ontology_conformance_verification", "ontology_conformance_verification", "ontology_modeling"):
        task = {"meta": {"phase": "do", "ontology_role": scen}}
        issues = ontology_ready_issues(task, root)
        assert any(i.code == "ONTOLOGY_FRAGMENT_MISSING" for i in issues), scen


def test_development_missing_blocked():
    root = _root()
    for scen in ("ontology_projection", "ontology_projection"):
        task = {"meta": {"phase": "do", "ontology_role": scen}}
        issues = ontology_ready_issues(task, root)
        assert any(i.code == "ONTOLOGY_FRAGMENT_MISSING" for i in issues)


def test_exempt_not_blocked():
    root = _root()
    for scen in ("ontology_modeling", "ontology_conformance_verification", "ontology_conformance_verification", "ontology_modeling", "ontology_projection"):
        task = {"meta": {"phase": "do", "ontology_role": scen, "ontology_exempt": True}}
        assert ontology_ready_issues(task, root) == []


def test_fragment_ok():
    root = _root()
    for scen in ("ontology_modeling", "ontology_conformance_verification", "ontology_conformance_verification"):
        task = {"meta": {"phase": "do", "ontology_role": scen, "ontology_fragment": "ontology"}}
        assert ontology_ready_issues(task, root) == []


def test_guidance_contains_scenario_and_hint():
    root = _root()
    task = {"meta": {"phase": "do", "ontology_role": "ontology_modeling"}}
    issues = ontology_ready_issues(task, root)
    msg = issues[0].message
    assert "ontology_modeling" in msg
    assert "ontology_exempt" in msg
    assert issues[0].guidance is not None


def test_non_do_not_blocked():
    root = _root()
    for phase in ("plan", "check", "act", "archive"):
        task = {"meta": {"phase": phase, "ontology_role": "ontology_modeling"}}
        assert ontology_ready_issues(task, root) == []
