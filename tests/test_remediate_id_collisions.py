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


def test_decisions_absorb_all_disposable_doctor_groups():
    """裁决表吸收当前 doctor 报告中的全部可处置撞车组。

    仓库可能处于 apply 前（23 组，含 12 组可处置）或 apply 后（11 组，全待办）。
    不变式：doctor 报出的可处置组必须全部被裁决表覆盖（uncovered 为空）。
    """
    r = run("--check-cover")
    d = json.loads(r.stdout)
    assert d["covered"] + d["deferred"] == d["doctor_groups"], d
    assert d["uncovered"] == [], f"存在未覆盖组: {d}"
    assert d["covered"] in (0, 12), f"covered 应 0(已应用)或 12(未应用): {d}"


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


def test_dir_rename_consistent_with_current_naming():
    """dry-run 的 dir_rename 标注与当前目录命名一致（幂等视角）。

    目录名仍以 `old_id-` 前缀开头 → 需重命名；否则已就位。
    apply 前 5 组标 True，apply 后 0 组标 True。
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rm", ROOT / "scripts/remediate-id-collisions.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    r = run("--dry-run", "--json")
    d = json.loads(r.stdout)
    for i in d["reassignments"]:
        dirname = (ROOT / i["task_dir"]).name
        expected = dirname.startswith(f"{i['old_id']}-")
        assert i["dir_rename"] == expected, (
            f"{i['old_id']}: 目录名 {dirname!r} dir_rename={i['dir_rename']} 期望 {expected}")
    # 目录仍含旧 ID 前缀的组须重命名；apply 后应全部就位
    pending = [i["old_id"] for i in d["reassignments"] if i["dir_rename"]]
    for old_id in pending:
        assert old_id in ("T0215", "T0217", "T0246", "T0247", "T0249"), pending


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


def test_sync_record_flow_events(tmp_path):
    """flow-events 的 record_id/task_id 随 records 重命名同步（doctor event_path_mismatches 不回归）。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rm", ROOT / "scripts/remediate-id-collisions.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    rec = tmp_path / "records" / "T0276-0731-nbu-dte-enforced-mechanism"
    fe = rec / "flow-events"
    fe.mkdir(parents=True)
    (fe / "FE-1.json").write_text(
        '{"record_id": "T0163-0731-nbu-dte-enforced-mechanism", "task_id": "T0163"}',
        encoding="utf-8")
    (fe / "FE-2.json").write_text(
        '{"record_id": "already-new", "task_id": "T0276"}', encoding="utf-8")

    n = mod._sync_record_flow_events(
        rec, "T0163-0731-nbu-dte-enforced-mechanism", "T0276-0731-nbu-dte-enforced-mechanism", "T0163", "T0276")
    assert n == 1, "仅旧值文件应被改写"
    import json
    ev1 = json.loads((fe / "FE-1.json").read_text(encoding="utf-8"))
    assert ev1["record_id"] == "T0276-0731-nbu-dte-enforced-mechanism"
    assert ev1["task_id"] == "T0276"
    ev2 = json.loads((fe / "FE-2.json").read_text(encoding="utf-8"))
    assert ev2["record_id"] == "already-new"
