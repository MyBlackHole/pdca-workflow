"""P0 负向测试：验证 gate 非装饰（L8/L10）。

- G6 ATTR_GENERIC：含泛化短语但无动词必失败；含动词则通过
- G13 check-design-vocab：design 文档含禁用词必失败；other 类型跳过
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ONT = REPO / "ontology"
VALIDATOR = REPO / "scripts/ontology-validate.py"
CHECK_DESIGN = REPO / "scripts/check-design-vocab.py"


def _copy_ontology(tmp_path: Path) -> Path:
    dst = tmp_path / "ontology"
    shutil.copytree(ONT, dst)
    return dst


def _run_validator(ont_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--ontology-dir", str(ont_dir)],
        capture_output=True, text=True,
    )


def _write_fidelity_node(ont_dir: Path, node_id: str, signal: str):
    """在 domain 下写入一个待测节点，触发 G6 检查。"""
    d = ont_dir / "domain"
    d.mkdir(exist_ok=True)
    fname = node_id.split("/")[-1] + ".md"
    (d / fname).write_text(
        "---\n"
        "schema: pdca.asset/v1\n"
        f"id: {node_id}\n"
        "type: domain\n"
        "layer: Knowledge\n"
        "summary: test node for G6 negative test\n"
        "status: active\n"
        "attributes:\n"
        f"  - name: check\n"
        f"    testable_signal: \"{signal}\"\n"
        "relations:\n"
        "  specializes:\n"
        "  - ontology:concept/meta-ontology\n"
        "  guides:\n"
        "  - ontology:domain/test-target\n"
        "---\n# test\n",
        encoding="utf-8",
    )


# ── G6 ATTR_GENERIC ──

def test_g6_pure_generic_must_fail():
    """纯泛化（phrase 无 verb）必报 ATTR_GENERIC，证明 gate 非装饰。"""
    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        _write_fidelity_node(ont, "ontology:domain/neg-pure-generic", "检查本文件")
        r = _run_validator(ont)
    assert r.returncode != 0, "纯泛化应被阻断: " + r.stdout + r.stderr
    assert "ATTR_GENERIC" in (r.stdout + r.stderr), r.stdout + r.stderr


def test_g6_generic_with_verb_must_pass():
    """含 phrase 但含 verb（双条件）不阻断，验证误报消除。"""
    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        _write_fidelity_node(ont, "ontology:domain/neg-with-verb", "检查本文件 python3 scripts/ontology-validate.py --check")
        r = _run_validator(ont)
    assert "ATTR_GENERIC" not in (r.stdout + r.stderr), "含 verb 不应报 ATTR_GENERIC: " + r.stdout + r.stderr


def test_g6_no_generic_must_pass():
    """无 phrase 的具体 signal 不应触发 G6。"""
    with tempfile.TemporaryDirectory() as td:
        ont = _copy_ontology(Path(td))
        _write_fidelity_node(ont, "ontology:domain/neg-clean", "grep -q pattern file && python3 scripts/check.py")
        r = _run_validator(ont)
    assert "ATTR_GENERIC" not in (r.stdout + r.stderr), r.stdout + r.stderr


def test_existing_ontology_still_passes():
    """现有 413 节点仍 0 issues（正向锚点）。"""
    r = _run_validator(ONT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ATTR_GENERIC" not in (r.stdout + r.stderr)


# ── G13 check-design-vocab ──

def _run_design_check(text: str, doc_type: str = "design") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_DESIGN), "--doc-type", doc_type],
        input=text,
        capture_output=True, text=True,
    )


def test_design_vocab_forbidden_must_flag():
    out = _run_design_check("本模块使用 component 架构")
    import json
    data = json.loads(out.stdout)
    assert not data["vocab_ok"]
    assert "component" in data["violations"]


def test_design_vocab_other_type_skipped():
    out = _run_design_check("本服务使用 component", doc_type="other")
    import json
    data = json.loads(out.stdout)
    assert data["vocab_ok"]
    assert data.get("skipped") is True


def test_design_vocab_clean_must_pass():
    out = _run_design_check("本 module 通过 seam 暴露 interface，使用 adapter 保证 locality")
    import json
    data = json.loads(out.stdout)
    assert data["vocab_ok"]
