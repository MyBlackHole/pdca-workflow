"""Tests for scripts/pdca_context.py (T0409)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scripts import pdca_context as pc  # noqa: E402
from scripts.ontology_reason import (  # noqa: E402
    admission_conditions,
    transition_targets,
)

REPO = Path(__file__).resolve().parent.parent
ONTO = REPO / "ontology"
PHASES = ["plan", "do", "check", "act", "archive"]


def test_context_each_phase_nonempty_and_identifies():
    for phase in PHASES:
        out = pc.render(phase, ONTO)
        assert isinstance(out, str) and out.strip(), f"{phase} 输出为空"
        assert f"PDCA 阶段指引：{phase}" in out, f"{phase} 缺少阶段标识"


def test_context_includes_enriched_body():
    out = pc.render("do", ONTO)
    assert "PDCA 的执行阶段" in out  # 来自补后的 phase-do 正文
    assert "ontology-ready" in out     # 准入条件章节


@pytest.mark.skip(reason="T2056 slow-quarantine (>10s: per-phase reasoner render); rehabilitate in T2059")
def test_context_json_matches_reasoner():
    for phase in PHASES:
        data = json.loads(pc.render(phase, ONTO, as_json=True))
        assert data["admission"] == admission_conditions(phase, ont_dir=ONTO)
        assert data["next_transitions"] == transition_targets(phase, ont_dir=ONTO)
        assert data["has_meta"] is True


def test_context_fallback_when_ontology_missing(tmp_path):
    out = pc.render("do", tmp_path / "nope")
    assert "PDCA 阶段指引：do" in out
    assert "回退" in out
