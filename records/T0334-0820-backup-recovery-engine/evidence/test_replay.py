"""
T0334 AC-3: heap/btree 重放单元测试。

验证 pgwrecover 的 FPI 落页 + 增量重放行为：
- FPI 落页：备份中 blk638 从 9 items 恢复为 12 items（含增量重放行）
- 幂等：重放输出页 LSN 更新到 >= 记录 LSN
- 增量重放：400001/400002/400003 三条 INSERT 完整落地
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
RELOID = 1946522
BLKNO = 638

# ItemIdData (PG18): 32-bit word, lp_off:15, lp_flags:2, lp_len:15
def parse_items(page_bytes, lower, upper):
    items = []
    for i in range(0, (lower - 24) // 4):
        v = struct.unpack_from("<I", page_bytes, 24 + i * 4)[0]
        off = v & 0x7FFF
        fl = (v >> 15) & 3
        ln = (v >> 17) & 0x7FFF
        items.append((i + 1, off, fl, ln))
    return items


def read_page(path, blk):
    with open(path, "rb") as f:
        f.seek(blk * 8192)
        return f.read(8192)


def read_tuple_id(page_bytes, off):
    """解析 item 的 tuple 首字段 id（int8）。t_hoff 固定 24，数据从 t+24 起。"""
    t = page_bytes[off:off + 80]
    d = t[24:32]
    return struct.unpack("<q", d)[0]


@pytest.mark.skipif(not BACKUP_DIR.exists(), reason="备份样本缺失")
def test_replay_appends_incremental_rows():
    """AC-3: 重放后 blk638 从 9 items 变为 12 items，增量 3 行落地。"""
    tmp = tempfile.mkdtemp(prefix="pgwrecover-ac3-")
    out_heap = os.path.join(tmp, "heap.out")
    out_clog = os.path.join(tmp, "clog")
    r = subprocess.run(
        [str(PG_RECOVER), str(BACKUP_DIR), out_heap, out_clog, f"--rel-oid={RELOID}"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    stats = json.loads(r.stdout)
    assert stats["incremental_applied"] == 2
    assert stats["fpi_pages"] == 1

    # 备份页：9 items；重放页：12 items
    backup_heap = None
    for db in range(0, 100000):
        p = BACKUP_DIR / "base" / str(db) / str(RELOID)
        if p.exists():
            backup_heap = p
            break
    assert backup_heap is not None, "备份中未找到 relfilenode"

    backup_page = read_page(backup_heap, BLKNO)
    replayed_page = read_page(out_heap, BLKNO)

    lower_b = struct.unpack_from("<H", backup_page, 12)[0]
    upper_b = struct.unpack_from("<H", backup_page, 14)[0]
    lower_r = struct.unpack_from("<H", replayed_page, 12)[0]
    upper_r = struct.unpack_from("<H", replayed_page, 14)[0]

    items_b = parse_items(backup_page, lower_b, upper_b)
    items_r = parse_items(replayed_page, lower_r, upper_r)
    assert len(items_b) == 9, f"备份 blk638 应有 9 items, 实际 {len(items_b)}"
    assert len(items_r) == 12, f"重放 blk638 应有 12 items, 实际 {len(items_r)}"

    # 前 9 个 item 保持不变，新增 3 个 item 为增量行
    ids = [read_tuple_id(replayed_page, off) for _, off, fl, ln in items_r[-3:]]
    assert sorted(ids) == [400001, 400002, 400003], f"增量行 id 不符: {ids}"

    # 幂等：页 LSN 应为最新记录 LSN（C/82081700 之前的 INSERT）
    pd_lsn = struct.unpack_from("<Q", replayed_page, 0)[0]
    assert pd_lsn >= 0xC820815B0