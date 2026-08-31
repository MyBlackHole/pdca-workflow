"""T0456 AC: evidence→ontology 自动反哺机制结构契约测试。"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from scripts.ontology_induction import EvidenceAdapter, induce, load_ontology  # noqa: E402
from scripts.ontology_gate import auto_induce_evidence, auto_induce_flow_issues  # noqa: E402


# ---------- EvidenceAdapter ----------
def test_evidence_adapter_exists_and_is_adapter(tmp_path: Path):
    from scripts.ontology_induction import Adapter
    assert isinstance(EvidenceAdapter(), Adapter)


def test_evidence_adapter_parses_manifest(tmp_path: Path):
    # 用真实 record 的 manifest 作为输入
    src = REPO / "records" / "T0454-0831-research-last-two-commits" / "evidence" / "manifest.jsonl"
    if not src.is_file():
        return
    drafts = EvidenceAdapter().parse(src)
    assert drafts, "EvidenceAdapter 未产出 drafts"
    # 应产生 ev-pitfall 的 draft
    titles = [d.title for d in drafts]
    assert any("pitfall" in t for t in titles)


def test_evidence_adapter_dedup(tmp_path: Path):
    src = REPO / "records" / "T0454-0831-research-last-two-commits" / "evidence" / "manifest.jsonl"
    if not src.is_file():
        return
    a = EvidenceAdapter().parse(src)
    b = EvidenceAdapter().parse(src)
    assert len(a) == len(b)
    assert sorted(d.title for d in a) == sorted(d.title for d in b)


def test_induce_evidence_adapter_produces_candidates(tmp_path: Path):
    src = REPO / "records" / "T0454-0831-research-last-two-commits" / "evidence"
    if not src.is_dir():
        return
    cands = induce(src, REPO / "ontology", adapter="evidence")
    assert cands, "evidence induce 未产出 candidates"
    for c in cands:
        assert c.type in {"domain", "entity", "concept", "process", "role",
                          "pattern", "principle", "pitfall", "fact", "decision"}
        assert c.id.startswith("ontology:")


def test_induce_evidence_guides_hit_domain(tmp_path: Path):
    src = REPO / "records" / "T0454-0831-research-last-two-commits" / "evidence" / "manifest.jsonl"
    if not src.is_file():
        return
    cands = induce(src, REPO / "ontology", adapter="evidence")
    # 至少有一个 candidate 命中 evidence-convergence-map（该 manifest 含该 ref）
    has_guide = any("evidence-convergence-map" in g for c in cands for g in c.guides)
    assert has_guide, "evidence induce 未命中 domain guides"


def test_induce_evidence_cli(tmp_path: Path):
    src = REPO / "records" / "T0454-0831-research-last-two-commits" / "evidence" / "manifest.jsonl"
    if not src.is_file():
        return
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/ontology_induction.py"),
         "--adapter", "evidence", "--source", str(src), "--out", "print"],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    assert "schema: pdca.asset/v1" in out.stdout


def test_induce_evidence_deterministic(tmp_path: Path):
    src = REPO / "records" / "T0454-0831-research-last-two-commits" / "evidence"
    if not src.is_dir():
        return
    a = induce(src, REPO / "ontology", adapter="evidence")
    b = induce(src, REPO / "ontology", adapter="evidence")
    assert [(c.id, c.type) for c in a] == [(c.id, c.type) for c in b]


# ---------- auto_induce_evidence ----------
def test_auto_induce_evidence_act_prompts(tmp_path: Path):
    root = REPO
    task = {"meta": {"phase": "act", "record": "T0454-0831-research-last-two-commits"}}
    issues = auto_induce_evidence(task, root)
    # T0454 含未锚定 pitfall evidence，应提示
    assert any(i.code == "AUTO_INDUCE_CANDIDATE" for i in issues)
    # guidance 应含可执行命令
    for i in issues:
        if i.code == "AUTO_INDUCE_CANDIDATE":
            assert "ontology_induction.py" in (i.guidance or "") or "ontology_induction.py" in i.message


def test_auto_induce_evidence_non_act_empty():
    root = REPO
    for phase in ("plan", "do", "check"):
        task = {"meta": {"phase": phase, "record": "T0454-0831-research-last-two-commits"}}
        assert auto_induce_evidence(task, root) == []


def test_auto_induce_evidence_no_manifest(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "ontology").mkdir()
    (root / "records" / "T9999-test" / "evidence").mkdir(parents=True)
    task = {"meta": {"phase": "act", "record": "T9999-test"}}
    assert auto_induce_evidence(task, root) == []


# ---------- auto_induce_flow_issues ----------
def test_auto_induce_flow_no_backlog_empty(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    assert auto_induce_flow_issues(root, threshold=3) == []


def test_auto_induce_flow_threshold(tmp_path: Path):
    root = tmp_path / "repo"
    backlog = root / "pdca" / "improvements"
    backlog.mkdir(parents=True)
    data = {
        "issues": [
            {"id": "FI-aaaa", "occurrence_count": 5, "candidate_id": None},
            {"id": "FI-bbbb", "occurrence_count": 1, "candidate_id": None},
            {"id": "FI-cccc", "occurrence_count": 10, "candidate_id": "FC-xxx"},
        ]
    }
    (backlog / "flow-issue-backlog.json").write_text(json.dumps(data), encoding="utf-8")
    low = auto_induce_flow_issues(root, threshold=3)
    high = auto_induce_flow_issues(root, threshold=6)
    # threshold 3 应命中 aaaa（5），阈值 6 不命中 aaaa
    assert any("FI-aaaa" in i.message for i in low)
    assert not any("FI-aaaa" in i.message for i in high)
    # 已有 candidate 的 cccc 不应命中
    assert not any("FI-cccc" in i.message for i in low)


def test_auto_induce_flow_codes():
    # 冒烟：函数返回 Issue 且 code 正确
    from pathlib import Path as P
    root = REPO
    # 用真实 backlog（若存在）
    issues = auto_induce_flow_issues(root, threshold=1)
    for i in issues:
        assert i.code == "AUTO_FLOW_INDUCE_CANDIDATE"
        assert i.guidance is not None


# ---------- ontology nodes ----------
def test_auto_induce_nodes_exist():
    onto = REPO / "ontology"
    assert (onto / "concept" / "auto-induce-evidence.md").is_file()
    assert (onto / "concept" / "auto-induce-flow-trigger.md").is_file()
    for p in [onto / "concept" / "auto-induce-evidence.md",
              onto / "concept" / "auto-induce-flow-trigger.md"]:
        text = p.read_text(encoding="utf-8")
        fm = yaml.safe_load(text.split("---", 2)[1])
        assert fm["type"] == "concept"
        assert "ontology:concept/pdca-continuous-improvement" in fm["relations"]["specializes"]
        assert fm["relations"].get("relates_to")


def test_ontology_validate_still_passes():
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/ontology-validate.py"), "--ontology-dir", str(REPO / "ontology")],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr


def test_ontology_graph_no_islands():
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts/ontology_graph.py"), "--root", str(REPO / "ontology"), "--format", "summary"],
        capture_output=True, text=True,
    )
    assert "islands: 0" in out.stdout
