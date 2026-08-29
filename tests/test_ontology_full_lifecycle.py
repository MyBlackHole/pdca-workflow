"""T0414 AC-2/AC-3/AC-4: 结论锚定、archive 本体自检、CI 硬门禁。"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO
GATE = REPO / "scripts" / "ci-ontology-gate.py"


def _copy_repo(tmp_path: Path) -> Path:
    d = tmp_path / "repo"
    shutil.copytree(REPO, d, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return d


def _break_ontology(ont_dir: Path):
    """在 meta-ontology.md 注入一个指向不存在节点的关系，触发 DANGLING_REF。"""
    p = ont_dir / "concept" / "meta-ontology.md"
    parts = p.read_text(encoding="utf-8").split("---", 2)
    fm = yaml.safe_load(parts[1])
    fm["relations"] = {"relates_to": ["ontology:concept/this-node-does-not-exist"]}
    new_fm = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
    p.write_text("---\n" + new_fm + "---\n" + parts[2], encoding="utf-8")


# ---------- AC-2 结论锚定 ----------
def test_verdict_confirmed_anchors_ok():
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from scripts.ontology_gate import verdict_anchor_issues

    task = {"meta": {"phase": "check", "verdict": {"outcome": "confirmed"}}}
    assert verdict_anchor_issues(task, REPO) == []


def test_verdict_missing_node_blocked(tmp_path):
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from scripts.ontology_gate import verdict_anchor_issues

    root = _copy_repo(tmp_path)
    (root / "ontology" / "entity" / "verdict-rejected.md").unlink()
    task = {"meta": {"phase": "check", "verdict": {"outcome": "rejected"}}}
    issues = verdict_anchor_issues(task, root)
    assert any(i.code == "VERDICT_ANCHOR_MISSING" for i in issues)


def test_no_verdict_not_blocked():
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from scripts.ontology_gate import verdict_anchor_issues

    assert verdict_anchor_issues({"meta": {"phase": "plan"}}, REPO) == []


# ---------- AC-3 archive 本体自检 ----------
def test_archive_selfcheck_ok():
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from scripts.ontology_gate import archive_ontology_ready_issues

    assert archive_ontology_ready_issues(REPO) == []


def test_archive_selfcheck_rejects_broken_ontology(tmp_path):
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from scripts.ontology_gate import archive_ontology_ready_issues

    root = _copy_repo(tmp_path)
    _break_ontology(root / "ontology")
    issues = archive_ontology_ready_issues(root)
    assert any(i.code in ("ARCHIVE_ONTOLOGY_INVALID", "ARCHIVE_ONTOLOGY_ISLANDS") for i in issues)


# ---------- AC-4 CI 硬门禁 ----------
def test_ci_gate_ok_on_clean_repo():
    r = subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ci_gate_fails_on_broken_ontology(tmp_path):
    root = _copy_repo(tmp_path)
    _break_ontology(root / "ontology")
    r = subprocess.run([sys.executable, str(GATE), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode != 0


def test_install_hook_script_syntax():
    # 安装脚本语法正确（不实际安装到用户 .git）
    r = subprocess.run(["bash", "-n", str(REPO / "scripts" / "install-git-hook.sh")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
