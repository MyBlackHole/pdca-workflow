"""
T0334 AC-2: WAL XLogRecord 读取器单元测试。

验证对真实备份产物 WAL 段的重放统计：
- records_seen 记录数符合预期（11 条）
- heap_rmgr_records 分派正确（6 条）
- CRC 校验在 xlogreader 内完成，损坏记录可检测（构造损坏段）
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PG_RECOVER = REPO / "build" / "pgwrecover"
BACKUP_DIR = Path("/tmp/opencode/pgwrecover-e2e/fpi_backup")

# 真实样本预期值（与 pg_waldump 实测一致）
EXPECTED_RECORDS_SEEN = 11
EXPECTED_HEAP_RMGR = 6
EXPECTED_FPI_PAGES = 1
EXPECTED_LAST_LSN = "C/82081700"


def _run_pgwrecover(backup_dir, out_heap, out_clog, rel_oid=None):
    cmd = [str(PG_RECOVER), str(backup_dir), str(out_heap), str(out_clog)]
    if rel_oid is not None:
        cmd.append(f"--rel-oid={rel_oid}")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


@pytest.mark.skipif(not BACKUP_DIR.exists(), reason="备份样本缺失")
def test_wal_records_parsed():
    """AC-2: 真实 WAL 段解析出预期记录数与统计。"""
    tmp = tempfile.mkdtemp(prefix="pgwrecover-ac2-")
    out_heap = os.path.join(tmp, "heap.out")
    out_clog = os.path.join(tmp, "clog")
    r = _run_pgwrecover(BACKUP_DIR, out_heap, out_clog, rel_oid=1946522)
    assert r.returncode == 0, r.stderr
    stats = json.loads(r.stdout)
    assert stats["records_seen"] == EXPECTED_RECORDS_SEEN
    assert stats["heap_rmgr_records"] == EXPECTED_HEAP_RMGR
    assert stats["fpi_pages"] == EXPECTED_FPI_PAGES
    assert stats["last_lsn"] == EXPECTED_LAST_LSN


def test_crc_corruption_detected():
    """AC-2: 损坏 WAL 记录可被检测（CRC 校验失败）。"""
    if not BACKUP_DIR.exists():
        pytest.skip("备份样本缺失，跳过")
    wal_files = list((BACKUP_DIR / "pg_wal").glob("000000010000000C*"))
    if not wal_files:
        pytest.skip("无 WAL 段，跳过")
    tmp = tempfile.mkdtemp(prefix="pgwrecover-ac2-")
    # 复制备份并损坏 WAL 段首字节
    shutil.copytree(BACKUP_DIR, os.path.join(tmp, "bk"), dirs_exist_ok=True)
    for wf in wal_files:
        src = os.path.join(tmp, "bk", "pg_wal", wf.name)
        data = bytearray(open(src, "rb").read())
        if len(data) > 8192:
            data[8192] ^= 0xFF  # 破坏第一条记录所在页的数据
            open(src, "wb").write(bytes(data))
    out_heap = os.path.join(tmp, "heap.out")
    out_clog = os.path.join(tmp, "clog")
    r = _run_pgwrecover(os.path.join(tmp, "bk"), out_heap, out_clog, rel_oid=1946522)
    # 允许返回码 0 或 1；关键断言：stderr 应报告 WAL 读取/CRC 错误
    combined = r.stderr + r.stdout
    assert ("CRC" in combined or "读取错误" in combined
            or "invalid record length" in combined), combined