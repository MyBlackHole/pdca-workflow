"""
T0336 AC-1/AC-2: MULTI_INSERT 与 UPDATE prefix/suffix 增量重放单元测试。

基于真实 PG18 样本验证 pgwrecover 的增量重放与运行库最终状态一致：
- AC-1 MULTI_INSERT（RM_HEAP2）：COPY 批量插入落地
- AC-2 UPDATE prefix/suffix：XLH_UPDATE_PREFIX_FROM_OLD / SUFFIX 重组落地

样本（/tmp/opencode/t0336-*/backup）为容器 PG18 真实备份 + 增量：
  - t0336-scope : 备份=100 行 COPY；增量=COPY 10（MULTI_INSERT）+ 4 UPDATE（无压缩）
  - t0336-prefix: 备份=1 行长文本（TOAST）；增量=1 HOT_UPDATE（flags 0x20 prefix）
  - t0336-psuf  : 备份=1 行内联 1500B 文本；增量=1 HOT_UPDATE（flags 0x60 prefix+suffix）

验证方式：重放输出 heap 与运行库 heap（live_heap.bin）逐字节对比（跳过页头 LSN）。
"""
import json
import os
import struct
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PG_RECOVER = REPO / "build" / "pgwrecover"

SAMPLE_ROOT = Path("/tmp/opencode")

SCENARIOS = [
    # sample_name, 场景, 验证 blk 列表
    # 说明: t0336-scope 的 blk0/blk1 会被运行库后续 VACUUM prune 影响（旧版本
    # 标记 DEAD），不属于增量 WAL 重放范围，只验证增量新页 blk2。
    pytest.param(
        "t0336-scope", "multi_insert_and_update", [2],
        marks=pytest.mark.skipif(not (SAMPLE_ROOT / "t0336-scope" / "backup").exists(),
                                 reason="t0336-scope 样本缺失"),
    ),
    pytest.param(
        "t0336-prefix", "update_prefix", [0],
        marks=pytest.mark.skipif(not (SAMPLE_ROOT / "t0336-prefix" / "backup").exists(),
                                 reason="t0336-prefix 样本缺失"),
    ),
    pytest.param(
        "t0336-psuf", "update_prefix_suffix", [0],
        marks=pytest.mark.skipif(not (SAMPLE_ROOT / "t0336-psuf" / "backup").exists(),
                                 reason="t0336-psuf 样本缺失"),
    ),
]


def parse_linp(page_bytes, offnum):
    """ItemIdData (PG18): 32-bit word, lp_off:15, lp_flags:2, lp_len:15。"""
    v = struct.unpack_from("<I", page_bytes, 24 + (offnum - 1) * 4)[0]
    return (v & 0x7FFF), ((v >> 15) & 3), (v >> 17)


def page_items(page_bytes):
    lower = struct.unpack_from("<H", page_bytes, 12)[0]
    n = (lower - 24) // 4
    return [parse_linp(page_bytes, i) for i in range(1, n + 1)]


# HEAP_XMIN_COMMITTED(0x100) / HEAP_XMAX_COMMITTED(0x400) 为运行时 hint bit：
# 运行库在读取时按 clog 动态标记并写回，备份/重放不设置（可见性由 clog 判断）。
# 另：HEAP_XMAX_INVALID(0x800) 时 xmax 字段为残留值（运行库可能写 1），不比较。
_HINT_MASK = 0x100 | 0x400
_XMAX_INVALID = 0x800


def masked_heap_equals(a, b):
    """逐字节比较两个页，屏蔽各 item 的 hint bit 与 XMAX_INVALID 时的 xmax。"""
    if len(a) != len(b):
        return False
    a = bytearray(a)
    b = bytearray(b)
    items = page_items(a)
    for idx, (off, fl, ln) in enumerate(items):
        if fl != 1:  # 仅 NORMAL item 有 tuple 头
            continue
        im_off = off + 20
        if im_off + 1 >= len(a):
            continue
        va = struct.unpack_from("<H", a, im_off)[0]
        vb = struct.unpack_from("<H", b, im_off)[0]
        struct.pack_into("<H", a, im_off, va & ~_HINT_MASK)
        struct.pack_into("<H", b, im_off, vb & ~_HINT_MASK)
        # XMAX_INVALID 时 xmax 字段 (off+8 .. +11) 为残留值，不比较
        if va & _XMAX_INVALID:
            for k in range(8, 12):
                a[off + k] = 0
        if vb & _XMAX_INVALID:
            for k in range(8, 12):
                b[off + k] = 0
    return bytes(a[24:]) == bytes(b[24:])


def assert_heap_matches(out_heap, live_path):
    """重放 heap 与运行库 heap 逐字节一致（跳过页头 24B 元数据 + hint bit）。"""
    rec = bytearray(Path(out_heap).read_bytes())
    live = bytearray(Path(live_path).read_bytes())
    assert len(rec) == len(live), f"大小不一致: 重放 {len(rec)} vs 运行库 {len(live)}"

    for blk in range(len(rec) // 8192):
        r = rec[blk * 8192:(blk + 1) * 8192]
        l = live[blk * 8192:(blk + 1) * 8192]
        assert masked_heap_equals(r, l), f"blk{blk} 除页头/hint bit 外存在内容差异"

        # 页布局（linp 数量与偏移）也应一致
        assert page_items(r) == page_items(l), f"blk{blk} linp 布局不一致"


def replay_scope(sample_name, tmp):
    """运行 pgwrecover，返回 (stats, out_heap, live_heap)。"""
    sample = SAMPLE_ROOT / sample_name
    rel_oid = (sample / "relnode.txt").read_text().strip()
    out_heap = os.path.join(tmp, "heap.out")
    out_clog = os.path.join(tmp, "clog")

    r = subprocess.run(
        [str(PG_RECOVER), str(sample / "backup"), out_heap, out_clog,
         f"--rel-oid={rel_oid}"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    stats = json.loads(r.stdout)

    live = sample / "live_heap.bin"
    assert live.exists(), f"缺少运行库对照 {live}"
    return stats, out_heap, live


def assert_heap_matches(out_heap, live_path, blks=None):
    """重放 heap 与运行库 heap 逐字节一致（跳过页头 24B 元数据 + hint bit）。

    blks: 指定验证的 blk 列表；None 表示验证全部 blk。
    """
    rec = bytearray(Path(out_heap).read_bytes())
    live = bytearray(Path(live_path).read_bytes())
    assert len(rec) == len(live), f"大小不一致: 重放 {len(rec)} vs 运行库 {len(live)}"

    page_count = len(rec) // 8192
    blk_list = blks if blks is not None else range(page_count)
    for blk in blk_list:
        assert 0 <= blk < page_count, f"blk{blk} 超出页数 {page_count}"
        r = rec[blk * 8192:(blk + 1) * 8192]
        l = live[blk * 8192:(blk + 1) * 8192]
        assert masked_heap_equals(r, l), f"blk{blk} 除页头/hint bit 外存在内容差异"

        # 页布局（linp 数量与偏移）也应一致
        assert page_items(r) == page_items(l), f"blk{blk} linp 布局不一致"


@pytest.mark.parametrize("sample_name,scenario,blks", SCENARIOS)
def test_replay_matches_live_heap(sample_name, scenario, blks):
    """重放输出 heap 与运行库最终状态一致。"""
    tmp = tempfile.mkdtemp(prefix=f"pgwrecover-{scenario}-")
    stats, out_heap, live = replay_scope(sample_name, tmp)
    assert stats["incremental_applied"] >= 1, \
        f"场景 {scenario} 未应用增量记录: {stats}"
    assert_heap_matches(out_heap, live, blks)


def test_multi_insert_creates_new_page():
    """AC-1: MULTI_INSERT 在备份不含的 blk2 上创建页（2 增量行 + 4 更新行）。"""
    sample = SAMPLE_ROOT / "t0336-scope"
    if not (sample / "backup").exists():
        pytest.skip("t0336-scope 样本缺失")
    tmp = tempfile.mkdtemp(prefix="pgwrecover-mi-")
    stats, out_heap, live = replay_scope("t0336-scope", tmp)
    assert stats["incremental_applied"] == 5

    rec = Path(out_heap).read_bytes()
    liveb = Path(live).read_bytes()
    assert len(rec) == 3 * 8192, f"重放应扩展至 3 页, 实际 {len(rec)}"
    items_rec = page_items(rec[2 * 8192:3 * 8192])
    items_live = page_items(liveb[2 * 8192:3 * 8192])
    assert len(items_rec) == 6, f"blk2 应有 6 items (2 MULTI_INSERT + 4 UPDATE), 实际 {len(items_rec)}"
    assert items_rec == items_live, "blk2 linp 布局与运行库不一致"