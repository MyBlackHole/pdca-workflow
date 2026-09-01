"""
ZFS DMU 实体 — dnode/dbuf 对象-块两级抽象与读写/脏数据路径
桩实现（Do 阶段最小可验证）：覆盖 ontology:entity/zfs-dmu 两属性

属性1 dnode_dbuf_abstraction:
  dnode_t {dn_struct_rwlock, dn_dbufs, dn_datablksz}
  dbuf_t  {db_mtx, db_state: DB_CACHED/DB_FILL/DB_READ, db_data}
  读路径: dnode_hold -> dbuf_whichblock -> dbuf_hold -> dbuf_read -> ARC -> ZIO
        对应 openzfs/zfs/module/zfs/dmu.c:740 dmu_buf_hold_array_by_dnode 并行读
        openzfs/zfs/module/zfs/dmu.c:1180 dmu_read_impl
  约束: 覆盖 dnode_hold → dbuf_whichblock → dbuf_hold → dbuf_read 状态机 DB_CACHED/DB_FILL
  信号: grep -q 'dmu_buf_hold_array_by_dnode' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'dnode_hold' module/zfs/dmu.c

属性2 dirty_throttle_signal:
  写路径: dmu_buf_will_dirty/will_fill -> dsl_pool_dirty_space(dp, space, tx) 累加 dp_dirty_pertxg
          -> 若 dirty > zfs_dirty_data_sync_percent 触发 txg_kick
        对应 openzfs/zfs/module/zfs/dsl_pool.c:20-60 Write Throttle
  约束: dsl_pool_dirty_space 累加 dp_dirty_pertxg 并在 zfs_dirty_data_sync_percent 触发 txg_kick
  信号: grep -q 'dsl_pool_dirty_space' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'zfs_dirty_data_sync_percent' module/zfs/dsl_pool.c

设计: 极简内存桩，不依赖真实 ZFS 源码，仅提供状态机与脏数据记账的可测试接口
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Dict, List, Optional


class DbufState(str, Enum):
    DB_CACHED = "DB_CACHED"
    DB_FILL = "DB_FILL"
    DB_READ = "DB_READ"


# 模拟 openzfs/zfs/module/zfs/dmu.c:740 dmu_buf_hold_array_by_dnode 并行读
# 模拟 openzfs/zfs/module/zfs/dmu.c:1180 dmu_read_impl
# 模拟 openzfs/zfs/module/zfs/dsl_pool.c:20-60 dsl_pool_dirty_space

@dataclass
class Dnode:
    """dnode_t 桩：对象头"""
    object_id: int
    datablksz: int = 8192
    dn_struct_rwlock: RLock = field(default_factory=RLock)
    dn_dbufs: Dict[int, "Dbuf"] = field(default_factory=dict)

    def hold(self):
        """dnode_hold(os, object) -> rw_enter(dn_struct_rwlock)"""
        self.dn_struct_rwlock.acquire()
        return self

    def release(self):
        self.dn_struct_rwlock.release()

    def whichblock(self, offset: int) -> int:
        """dbuf_whichblock(dnode, offset) -> level0 blkid"""
        return offset // self.datablksz


@dataclass
class Dbuf:
    """dbuf_t 桩：块缓冲"""
    dnode: Dnode
    blkid: int
    db_mtx: RLock = field(default_factory=RLock)
    db_state: DbufState = DbufState.DB_FILL
    db_data: Optional[bytes] = None
    dirty_txg: Optional[int] = None

    def hold(self) -> "Dbuf":
        """dbuf_hold(dnode, blkid) -> dbuf_t"""
        return self

    def read(self, txg: int = 0) -> bytes:
        """dbuf_read(dbuf) 状态机 DB_FILL -> DB_CACHED，经 ARC->ZIO 桩"""
        with self.db_mtx:
            if self.db_state == DbufState.DB_FILL:
                # 模拟 ARC miss -> ZIO fetch
                self.db_state = DbufState.DB_READ
                # 模拟 ZIO 完成
                self.db_data = b"\x00" * self.dnode.datablksz
                self.db_state = DbufState.DB_CACHED
            return self.db_data or b""

    def will_dirty(self, tx) -> None:
        """dmu_buf_will_dirty(db, tx) -> 标记脏并记账"""
        with self.db_mtx:
            self.dirty_txg = tx.txg
            tx.pool.dirty_space(len(self.db_data or b"\x00"), tx)


@dataclass
class DslPool:
    """dsl_pool_t 桩：脏数据记账与 TXG 反压"""
    dp_dirty_pertxg: Dict[int, int] = field(default_factory=dict)
    dp_dirty_total: int = 0
    zfs_dirty_data_sync_percent: int = 20  # 默认 20% 触发 txg_kick
    zfs_dirty_data_max: int = 100 * 1024 * 1024  # 桩：100MB 上限
    _kicked_txgs: List[int] = field(default_factory=list)

    def dirty_space(self, space: int, tx) -> None:
        """dsl_pool_dirty_space(dp, space, tx) 累加 dp_dirty_pertxg"""
        txg = tx.txg
        self.dp_dirty_pertxg[txg] = self.dp_dirty_pertxg.get(txg, 0) + space
        self.dp_dirty_total += space
        # zfs_dirty_data_sync_percent 触发 txg_kick
        threshold = self.zfs_dirty_data_max * self.zfs_dirty_data_sync_percent // 100
        if self.dp_dirty_total > threshold:
            self.txg_kick(txg)

    def txg_kick(self, txg: int) -> None:
        """txg_kick(txg) 桩：记录被 kick 的 txg"""
        if txg not in self._kicked_txgs:
            self._kicked_txgs.append(txg)


@dataclass
class DmuTx:
    """dmu_tx_t 桩"""
    txg: int
    pool: DslPool


class DmuObjset:
    """objset_t 桩：对象集，聚合 dnode"""

    def __init__(self, pool: DslPool):
        self.pool = pool
        self.objects: Dict[int, Dnode] = {}

    def dnode_hold(self, object_id: int) -> Dnode:
        """dnode_hold(os, object)"""
        if object_id not in self.objects:
            self.objects[object_id] = Dnode(object_id=object_id)
        return self.objects[object_id].hold()

    def dbuf_hold(self, object_id: int, blkid: int) -> Dbuf:
        """dbuf_hold(dnode, blkid)"""
        dnode = self.objects[object_id]
        if blkid not in dnode.dn_dbufs:
            dnode.dn_dbufs[blkid] = Dbuf(dnode=dnode, blkid=blkid)
        return dnode.dn_dbufs[blkid].hold()

    def dmu_buf_hold_array_by_dnode(self, dnode: Dnode, offset: int, size: int, read: bool = True) -> List[Dbuf]:
        """dmu_buf_hold_array_by_dnode 桩：并行读抽象，返回 blkid 连续的 dbuf 列表"""
        start = dnode.whichblock(offset)
        end = dnode.whichblock(offset + size - 1) if size > 0 else start
        bufs = []
        for blkid in range(start, end + 1):
            dbuf = self.dbuf_hold(dnode.object_id, blkid)
            if read:
                dbuf.read()
            bufs.append(dbuf)
        return bufs

    def dmu_read(self, object_id: int, offset: int, size: int) -> bytes:
        """dmu_read_impl 桩：批量 hold+memcpy"""
        dnode = self.dnode_hold(object_id)
        try:
            bufs = self.dmu_buf_hold_array_by_dnode(dnode, offset, size, read=True)
            return b"".join(b.db_data or b"" for b in bufs)[:size]
        finally:
            dnode.release()

    def dmu_write(self, object_id: int, offset: int, data: bytes, tx: DmuTx) -> None:
        """dmu_write -> will_dirty -> dirty_space -> txg_kick"""
        dnode = self.dnode_hold(object_id)
        try:
            blkid = dnode.whichblock(offset)
            dbuf = self.dbuf_hold(object_id, blkid)
            dbuf.db_data = data
            dbuf.will_dirty(tx)
        finally:
            dnode.release()


# —— 便民断言接口，供 scaffold 精化后调用 ——

def get_dmu_abstraction() -> dict:
    """供测试快速校验 DMU 两级抽象存在"""
    pool = DslPool()
    os = DmuObjset(pool)
    dnode = os.dnode_hold(1)
    try:
        bufs = os.dmu_buf_hold_array_by_dnode(dnode, 0, 8192)
        assert bufs[0].db_state == DbufState.DB_CACHED
        tx = DmuTx(txg=1, pool=pool)
        os.dmu_write(1, 0, b"x" * 100, tx)
        assert pool.dp_dirty_pertxg[1] > 0
        return {"dmu": 1, "dnode_dbuf": 1, "dirty_throttle": 1}
    finally:
        dnode.release()
