"""remediate-id-collisions.py 测试（T0274）。

覆盖：
- dry-run 模式：不改动文件，输出将改动的清单
- 裁决表完整性：覆盖 doctor 报告的 23 组，且 12 组可处置映射与实况一致
- 幂等性：dry-run 不改变任何文件（digest 前后一致）
- 引用链完整性：重分配后旧 ID 无残留
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/remediate-id-collisions.py"
PYTHON = sys.executable


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT), *args], capture_output=True, text=True
    )


def load_doctor() -> dict:
    r = subprocess.run(
        [PYTHON, str(ROOT / "scripts/pdca-doctor.py"), "--json"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    return json.loads(r.stdout)


def test_dry_run_no_changes(tmp_path):
    """dry-run 不改变任何文件。"""
    before = {}
    for p in ROOT.rglob("task.json"):
        before[str(p)] = p.read_bytes()

    r = run("--dry-run")
    assert r.returncode == 0, r.stderr

    after = {}
    for p in ROOT.rglob("task.json"):
        after[str(p)] = p.read_bytes()
    assert before == after, "dry-run 不得改动任何 task.json"


def test_decisions_cover_doctor_report():
    """裁决表覆盖 doctor 报告的全部 23 组：12 组重分配 + 11 组待办（活跃）。"""
    r = run("--check-cover")
    d = json.loads(r.stdout)
    assert d["doctor_groups"] == 23, d
    assert d["covered"] == 12, f"重分配组数应 12: {d}"
    assert d["reassigning"] == 12, d
    assert d["uncovered"] == [], f"存在未覆盖组: {d}"


def test_disposable_groups_all_archived():
    """12 组可处置组必须全部处于 archive 状态（活跃组须跳过）。"""
    r = run("--check-disposable")
    d = json.loads(r.stdout)
    assert d["all_archived"], d


def test_deferred_groups_have_active_tasks():
    """11 组待办组必须至少含一个活跃任务。"""
    r = run("--check-deferred")
    d = json.loads(r.stdout)
    assert d["all_have_active"], d


def test_dry_run_lists_all_reassignments():
    """dry-run 输出列明 12 组重分配的完整映射。"""
    r = run("--dry-run", "--json")
    d = json.loads(r.stdout)
    assert len(d["reassignments"]) == 12, f"期望 12 组重分配，实得 {len(d['reassignments'])}"
    for item in d["reassignments"]:
        assert item["old_id"] and item["new_id"]
        assert item["old_record"] and item["new_record"]


def test_dry_run_flags_dir_renames():
    """dry-run 标注 5 个含旧 ID 前缀的目录需重命名。"""
    r = run("--dry-run", "--json")
    d = json.loads(r.stdout)
    renames = [i["old_id"] for i in d["reassignments"] if i["dir_rename"]]
    assert renames == ["T0215", "T0217", "T0246", "T0247", "T0249"], renames


def test_reference_belongs_to_reassigned_context():
    """上下文感知引用归属：CDM/报表链指向重分配方，RPC 链指向保留方。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rm", ROOT / "scripts/remediate-id-collisions.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fn = mod._reference_belongs_to_reassigned
    # CDM/报表链 → True（引用指向重分配方，须改新 ID）
    assert fn("0804-report-subscheme-docs", "T0214") is True
    assert fn("0804-cdm-data-cli", "T0214") is True
    assert fn("0804-collection-service", "T0214") is True
    # RPC 链 → False（引用指向保留方，保持旧 ID）
    assert fn("0804-rpc-epoll-multireactor", "T0214") is False
    assert fn("0805-worker-adaptation", "T0214") is False
    assert fn("0805-rpc-epoll-worker-supply-followup", "T0215") is False
    # cdm 父任务 children 中 T0215/T0217 → 指向重分配子任务
    assert fn("0804-cdm-report-center-analyse", "T0215") is True
    assert fn("0804-cdm-report-center-analyse", "T0217") is True
    # 非纠缠组 → 不改
    assert fn("0729-vmcore-analysis", "T0142") is False
