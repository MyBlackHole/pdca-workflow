"""recall-brief-decisions.py 契约与回读矩阵测试（T0269）。

覆盖：
- 决策提取（推荐方向/已验证问题/信息缺口/风险 → 决策列表）
- 关键词抽取与停用词过滤
- CLI 生成矩阵骨架（subprocess 调用，脚本连字符无法 import）
- 命中检测：决策关键词在产出文件中的计数
- 矩阵兑现率解析（fulfilled/partial/not-fulfilled/unknown/未标注）
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "recall-brief-decisions.py"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "brief-recall"

BRIEF_CN = """# fixture Brief

## 分类

- 类型：enhancement
- 场景：development

## 推荐方向

- 推荐 A 方案并保留 B 回退。
- 逐批确认 + 指纹校验，不做游标盲跳。

## 信息缺口

- 需要测量 tmpfs 与旋转盘。
"""

DESIGN_CN = """# Design

采用 A 方案，保留 B 回退。

指纹校验覆盖逐批确认。

旋转盘基准：见 benchmark.log。
"""


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="module")
def fixtures() -> Path:
    (FIXTURE_DIR / "triager-brief.md").write_text(BRIEF_CN, encoding="utf-8")
    (FIXTURE_DIR / "design.md").write_text(DESIGN_CN, encoding="utf-8")
    return FIXTURE_DIR


@pytest.fixture(scope="module")
def matrix_path(fixtures: Path) -> Path:
    out = fixtures / "recall-matrix.md"
    res = run_script("--task-dir", str(fixtures), "--out", str(out))
    assert res.returncode == 0, res.stderr
    return out


def test_extract_decisions_types_and_counts(fixtures: Path):
    """决策提取：推荐方向/信息缺口各自成决策，按列表项计数。"""
    res = run_script("--task-dir", str(fixtures))
    assert res.returncode == 0, res.stderr
    text = res.stdout
    assert "| 1 | recommendation | 推荐 A 方案并保留 B 回退。" in text
    assert "| 2 | recommendation | 逐批确认 + 指纹校验，不做游标盲跳。" in text
    assert "| 3 | information_gap | 需要测量 tmpfs 与旋转盘。" in text


def test_hit_detection_in_matrix(fixtures: Path):
    """命中检测：决策关键词在产出中计数。"""
    res = run_script("--task-dir", str(fixtures))
    assert res.returncode == 0, res.stderr
    text = res.stdout
    assert "design.md" in text
    assert "design.md(" in text


def test_matrix_has_status_and_basis_columns(fixtures: Path):
    """矩阵行含兑现状态与依据列（状态默认 -，由审计填写）。"""
    res = run_script("--task-dir", str(fixtures))
    header_line = [l for l in res.stdout.splitlines() if l.startswith("| # |")][0]
    assert "兑现状态" in header_line
    assert "依据" in header_line
    row = [l for l in res.stdout.splitlines() if l.startswith("| 1 |")][0]
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    assert cells[4] == "-"  # 状态待审计
    assert cells[5] == ""  # 依据待填写


def test_matrix_generation_writes_file(matrix_path: Path):
    assert matrix_path.exists()
    assert "兑现状态" in matrix_path.read_text(encoding="utf-8")


def test_parse_matrix_fulfillment_rate(tmp_path: Path):
    """矩阵兑现率解析：fulfilled+partial 计入率，unknown/未标注不计入可判定。"""
    md = """| # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |
|---|------|------|---------|---------|------|
| 1 | recommendation | A | design.md(1) | fulfilled | design.md:1 |
| 2 | recommendation | B | design.md(2) | partial | design.md:2 |
| 3 | recommendation | C | - | not-fulfilled | - |
| 4 | recommendation | D | - | unknown | - |
| 5 | recommendation | E | - | - | - |
"""
    p = tmp_path / "matrix.md"
    p.write_text(md, encoding="utf-8")
    res = run_script("--matrix", str(p), "--json")
    assert res.returncode == 0, res.stderr
    stats = json.loads(res.stdout)
    assert stats["total_decisions"] == 5
    assert stats["judged"] == 3
    assert stats["fulfilled"] == 1
    assert stats["partial"] == 1
    assert stats["not_fulfilled"] == 1
    assert stats["unknown"] == 1
    assert stats["unjudged"] == 1
    assert stats["fulfillment_rate"] == pytest.approx(66.7)


def test_parse_matrix_requires_judged_for_rate(tmp_path: Path):
    """无已判定决策时兑现率为 0，不除零。"""
    md = "| # | 类型 | 决策 | 命中提示 | 兑现状态 | 依据 |\n|---|------|------|---------|---------|------|\n| 1 | risk | X | - | unknown | - |\n"
    p = tmp_path / "matrix2.md"
    p.write_text(md, encoding="utf-8")
    res = run_script("--matrix", str(p), "--json")
    stats = json.loads(res.stdout)
    assert stats["judged"] == 0
    assert stats["fulfillment_rate"] == 0.0


def test_missing_brief_returns_nonzero(tmp_path: Path):
    res = run_script("--task-dir", str(tmp_path))
    assert res.returncode == 1
    assert "未找到 triager-brief.md" in res.stderr
