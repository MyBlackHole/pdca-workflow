"""Tests for scripts/ontology_reason.py and scripts/ontology_gate.py (T0405)."""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scripts.ontology_gate import ontology_ready_issues  # noqa: E402
from scripts.ontology_reason import (  # noqa: E402
    admission_conditions,
    legal_transition,
    recognized_evidence,
)

REPO = Path(__file__).resolve().parent.parent
ONTO = REPO / "ontology"


def _fm_node(path: Path, slug: str, type_dir: str):
    path.mkdir(parents=True, exist_ok=True)
    fm = {
        "schema": "pdca.asset/v1",
        "id": f"ontology:{type_dir}/{slug}",
        "type": type_dir,
        "layer": "Knowledge",
        "summary": slug,
        "status": "active",
    }
    (path / f"{slug}.md").write_text(
        "---\n" + yaml.safe_dump(fm, allow_unicode=True).strip() + "\n---\n", encoding="utf-8"
    )


def test_reason_legal_meta_present():
    assert legal_transition("plan", "do", ont_dir=ONTO) is True
    assert legal_transition("do", "plan", ont_dir=ONTO) is False
    assert legal_transition("plan", "check", ont_dir=ONTO) is False
    assert legal_transition("act", "archive", ont_dir=ONTO) is True


def test_reason_fallback_when_meta_missing(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert legal_transition("plan", "do", ont_dir=empty) is True
    assert legal_transition("plan", "check", ont_dir=empty) is False
    assert admission_conditions("do", ont_dir=empty) == ["ontology-ready"]


def test_reason_admission_meta_present():
    assert admission_conditions("do", ont_dir=ONTO) == ["ontology-ready"]
    assert admission_conditions("plan", ont_dir=ONTO) == []


def test_reason_evidence():
    assert recognized_evidence("test-result", ont_dir=ONTO) is True
    assert recognized_evidence("bogus", ont_dir=ONTO) is False


def test_gate_missing_fragment():
    task = {"meta": {"phase": "do"}}
    issues = ontology_ready_issues(task, REPO)
    assert any(i.code == "ONTOLOGY_FRAGMENT_MISSING" for i in issues)


def test_gate_exempt():
    task = {"meta": {"phase": "do", "ontology_exempt": True}}
    assert ontology_ready_issues(task, REPO) == []


def test_gate_valid_fragment(tmp_path: Path):
    frag = tmp_path / "frag"
    _fm_node(frag / "concept", "my-entity", "concept")
    task = {"meta": {"phase": "do", "ontology_fragment": str(frag)}}
    assert ontology_ready_issues(task, REPO) == []


def test_gate_dangling_fragment():
    task = {"meta": {"phase": "do", "ontology_fragment": "/no/such/path/here"}}
    issues = ontology_ready_issues(task, REPO)
    assert any(i.code == "ONTOLOGY_FRAGMENT_DANGLING" for i in issues)


def test_gate_invalid_fragment(tmp_path: Path):
    frag = tmp_path / "bad"
    frag.mkdir()
    (frag / "concept").mkdir()
    (frag / "concept" / "x.md").write_text("# no frontmatter\n", encoding="utf-8")
    task = {"meta": {"phase": "do", "ontology_fragment": str(frag)}}
    issues = ontology_ready_issues(task, REPO)
    assert any(i.code == "ONTOLOGY_FRAGMENT_INVALID" for i in issues)
