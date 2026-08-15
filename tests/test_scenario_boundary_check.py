"""scenario-boundary-check.py 场景归属判定测试（T0273）。

覆盖：
- 判定规则：含可测试代码产出信号（脚本/测试/可回归验证）→ development；纯结论性调研 → research
- 历史错配任务回归夹具：T0268-T0272 期望 development，T0249 等纯 research 期望 research
- 边界用例：含报告但无代码产出、含工具代码无报告、两者皆无
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/scenario-boundary-check.py"
PYTHON = sys.executable


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT), *args], capture_output=True, text=True
    )


def test_single_judgement_code_production():
    """含脚本+测试产出 → development。"""
    r = run("--judge", "--code-scripts", "scripts/x.py", "--code-tests", "tests/test_x.py", "--desc", "audit tool")
    assert r.returncode == 0
    d = json.loads(r.stdout)
    assert d["scenario"] == "development"
    assert "可测试代码产出" in d["reason"]


def test_single_judgement_pure_research():
    """纯结论性调研（无代码产出）→ research。"""
    r = run("--judge", "--desc", "research nfs gm 可行性，仅输出报告")
    assert r.returncode == 0
    d = json.loads(r.stdout)
    assert d["scenario"] == "research"


def test_historical_mislabeled_fixtures():
    """历史错配任务（T0268-T0272）→ 期望 development。"""
    fixtures = {
        "T0268": {"code": True},
        "T0269": {"code": True},
        "T0270": {"code": True},
        "T0271": {"code": True},
        "T0272": {"code": True},
        "T0249": {"code": False, "desc": "kernel nfs gm 技术调研，仅报告"},
        "T0225": {"code": False, "desc": "xtrabackup 增量技术调研，仅报告"},
        "T0260": {"code": False, "desc": "自我改进 effectiveness 审计，输出结论报告"},
    }
    for tid, cfg in fixtures.items():
        args = ["--judge", "--task-id", tid, "--desc", cfg.get("desc", f"task {tid}")]
        if cfg["code"]:
            args += ["--code-scripts", "scripts/check.py", "--code-tests", "tests/test_check.py"]
        r = run(*args)
        assert r.returncode == 0, f"{tid} 判定失败"
        d = json.loads(r.stdout)
        expect = "development" if cfg["code"] else "research"
        assert d["scenario"] == expect, f"{tid}: 期望 {expect}, 实得 {d['scenario']}"


def test_boundary_report_without_code():
    """含报告但无代码产出 → research。"""
    r = run("--judge", "--desc", "调研并输出报告 md，无脚本无测试")
    d = json.loads(r.stdout)
    assert d["scenario"] == "research"


def test_boundary_toolcode_without_report():
    """含工具代码无报告 → development。"""
    r = run("--judge", "--code-scripts", "scripts/tool.py", "--desc", "开发审计工具")
    d = json.loads(r.stdout)
    assert d["scenario"] == "development"


def test_boundary_neither():
    """两者皆无 → 无法判定，返回 unknown 且退出码 1。"""
    r = run("--judge", "--desc", "模糊描述")
    assert r.returncode == 1
    d = json.loads(r.stdout)
    assert d["scenario"] == "unknown"


def test_json_schema():
    """输出含 scenario/reason/evidence 三字段。"""
    r = run("--judge", "--code-scripts", "scripts/x.py", "--desc", "tool")
    d = json.loads(r.stdout)
    assert set(("scenario", "reason", "evidence")) <= set(d.keys())
