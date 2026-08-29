"""T0414 AC-1: register-evidence 将 --kind 锚定到 pdca-evidence 子类型节点。"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "register-evidence.py"


def _root(tmp_path: Path) -> Path:
    d = tmp_path / "repo"
    shutil.copytree(REPO, d, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return d


def _run(root, record, src, kind, crit="AC-1", rid="ev1"):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--record", record,
         "--source", str(src), "--id", rid, "--kind", kind, "--criterion", crit],
        capture_output=True, text=True,
    )


def _manifest_entry(root, record):
    lines = (root / "records" / record / "evidence" / "manifest.jsonl").read_text().splitlines()
    return json.loads(lines[-1])


def test_convergence_map_anchors_to_node(tmp_path):
    root = _root(tmp_path)
    src = tmp_path / "src.txt"
    src.write_text("x")
    r = _run(root, "rec1", src, "convergence-map")
    assert r.returncode == 0, r.stderr
    entry = _manifest_entry(root, "rec1")
    assert entry["evidence_type_ref"] == "ontology:entity/evidence-convergence-map"


def test_legacy_support_kind_accepted_without_anchor(tmp_path):
    root = _root(tmp_path)
    src = tmp_path / "src.txt"
    src.write_text("x")
    r = _run(root, "rec3", src, "document")
    assert r.returncode == 0, r.stderr
    entry = _manifest_entry(root, "rec3")
    assert "evidence_type_ref" not in entry


def test_unknown_kind_rejected(tmp_path):
    root = _root(tmp_path)
    src = tmp_path / "src.txt"
    src.write_text("x")
    r = _run(root, "rec2", src, "bogus-kind")
    assert r.returncode != 0
    assert "不在允许集合" in (r.stdout + r.stderr)
