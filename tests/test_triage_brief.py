"""triager-brief 采用度检查器测试（T0268）。

覆盖：
- 契约解析：含/缺字段 fixture 的逐项报告与退出码
- 历史全量回溯：扫描 pdca/tasks（含归档）的采用率基线固化（防回归）
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check-triage-brief.py"
PYTHON = sys.executable

FULL_BRIEF = """# T9999 Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- priority: P1

## 查重与关系

- T9998 已覆盖，不重复。

## 已验证问题

- 代码证据：某函数复杂度 O(n^2)。
"""


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT), *args], capture_output=True, text=True
    )


def test_full_brief_all_fields(tmp_path):
    f = tmp_path / "triager-brief.md"
    f.write_text(FULL_BRIEF, encoding="utf-8")
    r = run("--file", str(f), "--exit-code")
    assert r.returncode == 0
    assert "category: OK" in r.stdout
    assert "evidence: OK" in r.stdout
    assert "dedup: OK" in r.stdout


def test_missing_fields_reported(tmp_path):
    f = tmp_path / "triager-brief.md"
    f.write_text("# T9999 Triage Brief\n\n只有标题。\n", encoding="utf-8")
    r = run("--file", str(f), "--json")
    d = json.loads(r.stdout)
    assert d["fields"]["category"] is False
    assert d["fields"]["evidence"] is False
    assert d["core_fields"] == 0


def test_exit_code_on_missing_core(tmp_path):
    f = tmp_path / "triager-brief.md"
    f.write_text("# T9999\n\n无字段。\n", encoding="utf-8")
    r = run("--file", str(f), "--exit-code")
    assert r.returncode == 1


def test_json_scan_baseline_structure(tmp_path):
    (tmp_path / "t1" / "triager-brief.md").parent.mkdir(parents=True)
    (tmp_path / "t1" / "triager-brief.md").write_text(FULL_BRIEF, encoding="utf-8")
    r = run("--scan", str(tmp_path), "--json")
    d = json.loads(r.stdout)
    assert d["total"] == 1
    assert d["core_fields_full"] == 1
    assert d["core_coverage"] == 100.0


def test_historical_baseline_no_regression():
    """历史全量回溯基线固化：93 个 brief（T0272 新增 self-audit 后），核心三字段全含率不低于当前值。"""
    r = run("--scan", str(ROOT / "pdca" / "tasks"), "--json")
    d = json.loads(r.stdout)
    assert d["total"] >= 93, f"期望 >=93 个 brief，实得 {d['total']}"
    assert d["core_fields_full"] >= 53, f"核心三字段全含数回退: {d['core_fields_full']}"
    assert d["core_coverage"] >= 57.0, f"核心覆盖率回退: {d['core_coverage']}%"


def test_field_coverage_bounds():
    """各字段覆盖率不显著回退（基线固化）。"""
    r = run("--scan", str(ROOT / "pdca" / "tasks"), "--json")
    d = json.loads(r.stdout)
    cov = d["field_coverage"]
    assert cov["category"] >= 76.3, cov
    assert cov["evidence"] >= 79.6, cov
    assert cov["dedup"] >= 76.3, cov
