"""
T0334 AC-1: pg_control + backup_label 解析器单元测试。

验证 pg_recover_read_control / pg_recover_read_backup_label 的二进制行为：
- 对真实备份产物运行 pgwrecover，校验输出 JSON 的 pg_control_version 与起点 LSN
- 构造带 backup_label 的备份目录，校验 START WAL LOCATION 覆盖默认起点
"""
import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PG_RECOVER = REPO / "build" / "pgwrecover"
BACKUP_DIR = Path("/tmp/opencode/pgwrecover-e2e/fpi_backup")

# 从真实备份解析的预期值（pg_control 布局：version@8, redo@32）
EXPECTED_VERSION = 1800
EXPECTED_REDO = 0xC820805B8
EXPECTED_REDO_STR = "C/820805B8"


def _run_pgwrecover(backup_dir, out_heap, out_clog, rel_oid=None):
    cmd = [str(PG_RECOVER), str(backup_dir), str(out_heap), str(out_clog)]
    if rel_oid is not None:
        cmd.append(f"--rel-oid={rel_oid}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r


@pytest.mark.skipif(not BACKUP_DIR.exists(), reason="备份样本缺失")
def test_control_version_and_redo_lsn():
    """AC-1: 真实备份 pg_control 解析出版本号与 redo 起点。"""
    tmp = tempfile.mkdtemp(prefix="pgwrecover-ac1-")
    out_heap = os.path.join(tmp, "heap.out")
    out_clog = os.path.join(tmp, "clog")
    r = _run_pgwrecover(BACKUP_DIR, out_heap, out_clog, rel_oid=1946522)
    # 解析 stderr 中起点 LSN 打印
    assert r.returncode == 0, r.stderr
    assert f"pg_control 版本 {EXPECTED_VERSION}" in r.stderr
    assert f"恢复起点 LSN {EXPECTED_REDO_STR}" in r.stderr
    stats = json.loads(r.stdout)
    assert stats["pg_control_version"] == EXPECTED_VERSION
    assert stats["start_lsn"] == EXPECTED_REDO_STR


def test_backup_label_overrides_start():
    """AC-1: backup_label START WAL LOCATION 覆盖默认起点。"""
    if not BACKUP_DIR.exists():
        pytest.skip("备份样本缺失，跳过")
    tmp = tempfile.mkdtemp(prefix="pgwrecover-ac1-")
    # 复制备份并注入 backup_label（起点故意不同于 pg_control 默认）
    shutil.copytree(BACKUP_DIR, os.path.join(tmp, "bk"), dirs_exist_ok=True)
    label = os.path.join(tmp, "bk", "backup_label")
    with open(label, "w") as f:
        f.write("START WAL LOCATION: C/820805B8 (file 000000010000000C00000082)\n")
        f.write("CHECKPOINT LOCATION: C/82080610\n")
        f.write("BACKUP METHOD: streamed\n")
    out_heap = os.path.join(tmp, "heap.out")
    out_clog = os.path.join(tmp, "clog")
    r = _run_pgwrecover(os.path.join(tmp, "bk"), out_heap, out_clog, rel_oid=1946522)
    assert r.returncode == 0, r.stderr
    assert "检测到 backup_label, 起点覆盖为 C/820805B8" in r.stderr
    stats = json.loads(r.stdout)
    assert stats["start_lsn"] == "C/820805B8"