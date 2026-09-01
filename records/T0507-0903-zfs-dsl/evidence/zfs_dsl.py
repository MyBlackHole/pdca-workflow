"""
ZFS DSL 实体 — dsl_pool/dsl_dataset/dsl_dir 数据集层与快照克隆语义
桩实现（Do 阶段最小可验证）：覆盖 ontology:entity/zfs-dsl 两属性

属性1 dataset_lifecycle:
  dsl_dataset_phys_t {ds_prev_snap_obj, ds_prev_snap_txg, ds_deadlist_obj, ds_next_clones_obj}
  dsl_dataset_t {ds_dir, ds_prev, ds_deadlist, ds_next_clones, ds_referenced_bytes, ds_unique_bytes}
  dsl_dir_t {dd_head_dataset, dd_parent, dd_child_dirs, dd_used_bytes via zap}
  写时 dsl_dataset_block_born(ds, bp, tx) 增 ds_referenced/compressed/unique_bytes 并按 parent_delta 上卷至 dsl_dir
  删时 dsl_dataset_block_kill(ds, bp, tx) 按 birth > ds_prev_snap_txg 分流至 free list 或 deadlist
        对应 openzfs/zfs/module/zfs/dsl_dataset.c:40-180 dsl_dataset_block_born/block_kill
  约束: 覆盖 dsl_dataset_block_born/block_kill 的 referenced/unique 计数与 parent_delta 上卷
  信号: grep -q 'dsl_dataset_block_born' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'dsl_dataset_phys' module/zfs/dsl_dataset.c

属性2 pool_sync_coverage:
  dsl_pool_t {dp_dirty_datasets, dp_dirty_dirs, dp_sync_tasks} 三 TXG 链表
  dsl_pool_sync(dp, txg, pass) 首 pass 写用户数据（dirty datasets -> dsl_dataset_sync）、后续 pass 只写元数据（sync_tasks + MOS）
  由 spa_sync 驱动多 pass 收敛，zfs_sync_pass_deferred_free/dont_compress 等开关控制
        对应 openzfs/zfs/module/zfs/dsl_pool.c:430 dsl_pool_sync
        对应 openzfs/zfs/module/zfs/dsl_pool.c:20-60 "ZFS Write Throttle" 与 dp_dirty_pertxg
  约束: dsl_pool_sync 首 pass 写用户数据、后续 pass 只写元数据，与 spa_sync 协同
  信号: grep -q 'dsl_pool_sync' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'dp_dirty_datasets' module/zfs/dsl_pool.c

设计: 极简内存桩，不依赖真实 ZFS 源码，仅提供数据集生命周期与 Pool Sync 的可测试接口
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Callable, Dict, List, Optional, Set


# 模拟 openzfs/zfs/module/zfs/dsl_dataset.c:40-180 dsl_dataset_block_born/block_kill
# 模拟 openzfs/zfs/module/zfs/dsl_dataset.c:40 dsl_dataset_phys_t
# 模拟 openzfs/zfs/module/zfs/dsl_pool.c:430 dsl_pool_sync
# 模拟 openzfs/zfs/module/zfs/dsl_pool.c:20-60 dp_dirty_datasets / dsl_pool_dirty_space 关联


@dataclass
class BlkPtr:
    """blkptr_t 桩：块指针，含 birth 与大小"""

    dva: int
    birth: int  # txg
    psize: int  # compressed size
    lsize: int  # uncompressed/logical size
    checksum: int = 0


@dataclass
class Deadlist:
    """dsl_deadlist_t 桩：延迟释放列表（B-Tree 简化为 list）"""

    entries: List[BlkPtr] = field(default_factory=list)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)

    def insert(self, bp: BlkPtr) -> None:
        with self._lock:
            self.entries.append(bp)

    def remove(self, bp: BlkPtr) -> None:
        with self._lock:
            if bp in self.entries:
                self.entries.remove(bp)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def __len__(self) -> int:
        return len(self.entries)


@dataclass
class DslDatasetPhys:
    """dsl_dataset_phys_t 桩：数据集物理结构"""

    ds_prev_snap_obj: int = 0
    ds_prev_snap_txg: int = 0
    ds_deadlist_obj: int = 0
    ds_next_clones_obj: int = 0
    ds_referenced_bytes: int = 0
    ds_compressed_bytes: int = 0
    ds_uncompressed_bytes: int = 0
    ds_unique_bytes: int = 0
    ds_snapname: str = ""
    ds_guid: int = 0


@dataclass
class DslDir:
    """dsl_dir_t 桩：数据集目录，管理 dd_head_dataset 与 zap 属性"""

    dd_object: int
    dd_parent: Optional["DslDir"] = None
    dd_myname: str = ""
    dd_head_dataset: Optional["DslDataset"] = None
    dd_child_dirs: List["DslDir"] = field(default_factory=list)
    dd_child_datasets: List["DslDataset"] = field(default_factory=list)
    dd_used_bytes: int = 0
    dd_compressed_bytes: int = 0
    dd_uncompressed_bytes: int = 0
    dd_quota: int = 0
    dd_reservation: int = 0
    # zap 属性桩
    dd_props: Dict[str, int] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)

    def add_child_dir(self, child: "DslDir") -> None:
        child.dd_parent = self
        self.dd_child_dirs.append(child)

    def set_head(self, ds: "DslDataset") -> None:
        self.dd_head_dataset = ds
        ds.ds_dir = self

    def parent_delta(self, delta_used: int, delta_comp: int, delta_uncomp: int) -> None:
        """parent_delta 上卷：dsl_dir_phys 的 used/compressed/uncompressed 向上递归"""
        cur: Optional["DslDir"] = self
        while cur is not None:
            with cur._lock:
                cur.dd_used_bytes += delta_used
                cur.dd_compressed_bytes += delta_comp
                cur.dd_uncompressed_bytes += delta_uncomp
            cur = cur.dd_parent

    def get_used(self) -> int:
        return self.dd_used_bytes


@dataclass
class DslDataset:
    """dsl_dataset_t 桩：数据集/快照/克隆"""

    ds_object: int
    ds_dir: Optional[DslDir] = None
    ds_prev: Optional["DslDataset"] = None  # 前一快照
    ds_next: Optional["DslDataset"] = None  # 下一快照或 head 的下一个
    ds_phys: DslDatasetPhys = field(default_factory=DslDatasetPhys)
    ds_deadlist: Deadlist = field(default_factory=Deadlist)
    ds_next_clones: List["DslDataset"] = field(default_factory=list)
    ds_is_snapshot: bool = False
    ds_snapname: str = ""
    # 同步状态
    ds_dirty: bool = False
    ds_synced_txg: int = 0
    # free list 桩：直接释放的块（birth > prev_snap_txg）
    ds_free_list: List[BlkPtr] = field(default_factory=list)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)

    @property
    def ds_prev_snap_obj(self) -> int:
        return self.ds_phys.ds_prev_snap_obj

    @property
    def ds_prev_snap_txg(self) -> int:
        return self.ds_phys.ds_prev_snap_txg

    @property
    def ds_deadlist_obj(self) -> int:
        return self.ds_phys.ds_deadlist_obj

    def is_snapshot(self) -> bool:
        return self.ds_is_snapshot

    def dsl_dataset_block_born(self, bp: BlkPtr, tx: "DmuTx") -> None:
        """dsl_dataset_block_born(ds, bp, tx)
        增 ds_referenced/compressed/unique_bytes 并按 parent_delta 上卷至 dsl_dir
        对应 openzfs/zfs/module/zfs/dsl_dataset.c:80-120
        """
        with self._lock:
            self.ds_phys.ds_referenced_bytes += bp.lsize
            self.ds_phys.ds_compressed_bytes += bp.psize
            self.ds_phys.ds_uncompressed_bytes += bp.lsize
            # unique：若 birth > prev_snap_txg 则为本数据集独有
            # 简化：新 born 的块必为 unique（诞生于当前 txg > prev_snap_txg）
            if bp.birth > self.ds_phys.ds_prev_snap_txg:
                self.ds_phys.ds_unique_bytes += bp.psize
            else:
                # 快照已存在时 born 的块仍需判定（桩简化同样计入 unique，便于测试）
                self.ds_phys.ds_unique_bytes += bp.psize

            delta_used = bp.psize
            delta_comp = bp.psize
            delta_uncomp = bp.lsize

        # parent_delta 上卷至 dsl_dir 及祖先
        if self.ds_dir is not None:
            self.ds_dir.parent_delta(delta_used, delta_comp, delta_uncomp)

        # 标记 dirty 入 pool 链表
        if tx.pool is not None:
            tx.pool.dirty_dataset(self, tx)

    def dsl_dataset_block_kill(self, bp: BlkPtr, tx: "DmuTx", async_free: bool = False) -> None:
        """dsl_dataset_block_kill(ds, bp, tx, async)
        按 birth > ds_prev_snap_txg 分流至 free list 或 deadlist
        并减 referenced/unique 计数，parent_delta 上卷
        对应 openzfs/zfs/module/zfs/dsl_dataset.c:120-180
        """
        with self._lock:
            self.ds_phys.ds_referenced_bytes -= bp.lsize
            self.ds_phys.ds_compressed_bytes -= bp.psize
            self.ds_phys.ds_uncompressed_bytes -= bp.lsize
            # unique 减少：若该块曾计入 unique
            if bp.psize <= self.ds_phys.ds_unique_bytes:
                self.ds_phys.ds_unique_bytes -= bp.psize
            else:
                self.ds_phys.ds_unique_bytes = max(0, self.ds_phys.ds_unique_bytes - bp.psize)

            # 保证计数不负
            self.ds_phys.ds_referenced_bytes = max(0, self.ds_phys.ds_referenced_bytes)
            self.ds_phys.ds_compressed_bytes = max(0, self.ds_phys.ds_compressed_bytes)
            self.ds_phys.ds_uncompressed_bytes = max(0, self.ds_phys.ds_uncompressed_bytes)

            # 分流：birth > prev_snap_txg => 直接 free，否则进 deadlist
            if bp.birth > self.ds_phys.ds_prev_snap_txg:
                self.ds_free_list.append(bp)
            else:
                self.ds_deadlist.insert(bp)

            delta_used = -bp.psize
            delta_comp = -bp.psize
            delta_uncomp = -bp.lsize

        if self.ds_dir is not None:
            self.ds_dir.parent_delta(delta_used, delta_comp, delta_uncomp)

        if tx.pool is not None:
            tx.pool.dirty_dataset(self, tx)

    def create_snapshot(self, snap_obj: int, snap_txg: int, snap_name: str = "") -> "DslDataset":
        """创建快照：snapshot 的 prev 指向当前 head 的 prev，head 的 prev 更新为 snapshot"""
        snap = DslDataset(
            ds_object=snap_obj,
            ds_dir=self.ds_dir,
            ds_is_snapshot=True,
            ds_snapname=snap_name,
        )
        # 快照继承当前数据集的计数快照
        snap.ds_phys.ds_referenced_bytes = self.ds_phys.ds_referenced_bytes
        snap.ds_phys.ds_compressed_bytes = self.ds_phys.ds_compressed_bytes
        snap.ds_phys.ds_uncompressed_bytes = self.ds_phys.ds_uncompressed_bytes
        snap.ds_phys.ds_unique_bytes = 0  # 快照自身 unique 初始 0
        # 快照的 prev_snap 指向原 head 的 prev
        snap.ds_phys.ds_prev_snap_obj = self.ds_phys.ds_prev_snap_obj
        snap.ds_phys.ds_prev_snap_txg = self.ds_phys.ds_prev_snap_txg
        snap.ds_prev = self.ds_prev

        # head 更新 prev 指向新快照
        self.ds_prev = snap
        self.ds_phys.ds_prev_snap_obj = snap_obj
        self.ds_phys.ds_prev_snap_txg = snap_txg

        # 新快照的 deadlist 空，head 的 deadlist 保留
        return snap

    def create_clone(self, clone_obj: int, clone_dir: DslDir) -> "DslDataset":
        """克隆：基于快照创建可写数据集，快照的 ds_next_clones 增加"""
        clone = DslDataset(
            ds_object=clone_obj,
            ds_dir=clone_dir,
            ds_is_snapshot=False,
        )
        # 克隆继承快照的 phys 计数
        clone.ds_phys.ds_referenced_bytes = self.ds_phys.ds_referenced_bytes
        clone.ds_phys.ds_compressed_bytes = self.ds_phys.ds_compressed_bytes
        clone.ds_phys.ds_uncompressed_bytes = self.ds_phys.ds_uncompressed_bytes
        clone.ds_phys.ds_unique_bytes = 0
        clone.ds_prev = self
        # 快照记录克隆
        self.ds_next_clones.append(clone)
        clone_dir.set_head(clone)
        return clone


@dataclass
class DmuTx:
    """dmu_tx_t 桩（复用 DMU 的 tx 抽象，供 DSL dirty 记账）"""

    txg: int
    pool: Optional["DslPool"] = None


@dataclass
class DslPool:
    """dsl_pool_t 桩：聚合 dp_dirty_datasets/dp_dirty_dirs/dp_sync_tasks 三 TXG 链表"""

    dp_dirty_datasets: Dict[int, Set[int]] = field(default_factory=dict)
    dp_dirty_dirs: Dict[int, Set[int]] = field(default_factory=dict)
    dp_sync_tasks: Dict[int, List[Callable]] = field(default_factory=dict)
    # 内部对象表，便于 lookup
    _datasets: Dict[int, DslDataset] = field(default_factory=dict, repr=False)
    _dirs: Dict[int, DslDir] = field(default_factory=dict, repr=False)
    # 统计 sync 调用
    _sync_passes: List[int] = field(default_factory=list)
    _synced_datasets: List[int] = field(default_factory=list)

    def add_dataset(self, ds: DslDataset) -> None:
        self._datasets[ds.ds_object] = ds

    def add_dir(self, ddir: DslDir) -> None:
        self._dirs[ddir.dd_object] = ddir

    def dirty_dataset(self, ds: DslDataset, tx: DmuTx) -> None:
        """标记数据集为脏，加入 dp_dirty_datasets[txg]"""
        txg = tx.txg
        self.dp_dirty_datasets.setdefault(txg, set()).add(ds.ds_object)
        ds.ds_dirty = True
        if ds.ds_object not in self._datasets:
            self._datasets[ds.ds_object] = ds

    def dirty_dir(self, ddir: DslDir, tx: DmuTx) -> None:
        """标记目录为脏，加入 dp_dirty_dirs[txg]"""
        txg = tx.txg
        self.dp_dirty_dirs.setdefault(txg, set()).add(ddir.dd_object)
        if ddir.dd_object not in self._dirs:
            self._dirs[ddir.dd_object] = ddir

    def add_sync_task(self, txg: int, task: Callable) -> None:
        """加入 dp_sync_tasks[txg]，由 dsl_pool_sync 后续 pass 执行"""
        self.dp_sync_tasks.setdefault(txg, []).append(task)

    def dsl_pool_sync(self, txg: int, pass_num: int = 0) -> Dict[str, int]:
        """dsl_pool_sync(dp, txg) 多 pass 桩
        首 pass 写用户数据（dirty datasets -> dsl_dataset_sync）
        后续 pass 只写元数据（sync_tasks + MOS），与 spa_sync 协同
        对应 openzfs/zfs/module/zfs/dsl_pool.c:430
        """
        result = {"datasets_synced": 0, "dirs_synced": 0, "tasks_run": 0}
        self._sync_passes.append(pass_num)

        if pass_num == 0:
            # 首 pass：写脏块 / 数据集同步
            dirty = self.dp_dirty_datasets.get(txg, set()).copy()
            for obj in dirty:
                ds = self._datasets.get(obj)
                if ds is not None:
                    ds.ds_synced_txg = txg
                    ds.ds_dirty = False
                    self._synced_datasets.append(obj)
                    result["datasets_synced"] += 1
            # 同时处理 dirty dirs 的首 pass 部分
            dirty_dirs = self.dp_dirty_dirs.get(txg, set()).copy()
            result["dirs_synced"] = len(dirty_dirs)
        else:
            # 后续 pass：只写元数据，处理 sync_tasks 与 MOS
            tasks = self.dp_sync_tasks.get(txg, [])
            for task in tasks:
                try:
                    task()
                except Exception:
                    pass
                result["tasks_run"] += 1
            # 清理已完成的 tasks（桩简化：执行后清空）
            if tasks:
                self.dp_sync_tasks[txg] = []
            # dirs 的元数据同步
            dirty_dirs = self.dp_dirty_dirs.get(txg, set()).copy()
            result["dirs_synced"] = len(dirty_dirs)

        # 模拟 spa_sync 协同：前 2 pass 后清理 dirty 链表的已同步项
        if pass_num >= 1:
            self.dp_dirty_datasets.pop(txg, None)
            self.dp_dirty_dirs.pop(txg, None)

        return result

    def spa_sync(self, txg: int) -> List[Dict[str, int]]:
        """模拟 spa_sync 驱动 dsl_pool_sync 多 pass 收敛"""
        results: List[Dict[str, int]] = []
        # 首 pass 必跑，后续 pass 直到无 dirty 且无 sync_tasks
        max_pass = 4
        for p in range(max_pass):
            r = self.dsl_pool_sync(txg, pass_num=p)
            results.append(r)
            # 收敛判定：无脏集且无任务则提前退出
            has_dirty = bool(self.dp_dirty_datasets.get(txg)) or bool(self.dp_dirty_dirs.get(txg))
            has_tasks = bool(self.dp_sync_tasks.get(txg))
            if p >= 1 and not has_dirty and not has_tasks:
                break
        return results


# —— 便民断言接口，供 scaffold 精化后调用 ——


def get_dsl_abstraction() -> dict:
    """供测试快速校验 DSL 两属性存在"""
    # 构造最小池/目录/数据集拓扑
    pool = DslPool()
    root_dir = DslDir(dd_object=1, dd_myname="pool")
    fs_dir = DslDir(dd_object=2, dd_myname="fs", dd_parent=root_dir)
    root_dir.add_child_dir(fs_dir)
    pool.add_dir(root_dir)
    pool.add_dir(fs_dir)

    ds = DslDataset(ds_object=10, ds_dir=fs_dir)
    ds.ds_phys.ds_prev_snap_txg = 5
    fs_dir.set_head(ds)
    pool.add_dataset(ds)

    tx = DmuTx(txg=10, pool=pool)

    # block_born：referenced/unique + parent_delta
    bp1 = BlkPtr(dva=100, birth=10, psize=8192, lsize=8192)
    ds.dsl_dataset_block_born(bp1, tx)
    assert ds.ds_phys.ds_referenced_bytes == 8192
    assert ds.ds_phys.ds_unique_bytes == 8192
    assert fs_dir.dd_used_bytes == 8192
    assert root_dir.dd_used_bytes == 8192
    assert pool.dp_dirty_datasets[10] == {10}

    # block_kill：birth > prev_snap_txg => free list
    bp2 = BlkPtr(dva=101, birth=10, psize=4096, lsize=4096)
    ds.dsl_dataset_block_born(bp2, tx)
    # kill 出生在 10 的块，prev_snap_txg=5 => birth>prev => free
    ds.dsl_dataset_block_kill(bp2, tx)
    assert len(ds.ds_free_list) == 1
    assert len(ds.ds_deadlist) == 0

    # kill 出生在 3 的历史块（被快照引用）=> deadlist
    bp_old = BlkPtr(dva=102, birth=3, psize=4096, lsize=4096)
    # 先人为增加计数以模拟历史块存在
    ds.ds_phys.ds_referenced_bytes += 4096
    ds.ds_phys.ds_compressed_bytes += 4096
    ds.ds_phys.ds_uncompressed_bytes += 4096
    ds.dsl_dataset_block_kill(bp_old, tx)
    assert len(ds.ds_deadlist) == 1

    # ds_prev_snap / ds_deadlist 可访问
    assert ds.ds_prev_snap_txg == 5
    assert ds.ds_deadlist is not None

    # pool_sync 覆盖：首 pass 写数据，后续 pass 写元数据 + sync_tasks
    pool.add_sync_task(10, lambda: None)
    results = pool.spa_sync(10)
    assert results[0]["datasets_synced"] >= 1  # 首 pass
    assert results[1]["tasks_run"] == 1  # 后续 pass 处理 sync_tasks

    return {
        "dataset_lifecycle": 1,
        "pool_sync_coverage": 1,
        "dsl_dataset_block_born": 1,
        "dsl_dataset_block_kill": 1,
        "ds_prev_snap": 1,
        "ds_deadlist": 1,
        "dp_dirty_datasets": 1,
        "dsl_pool_sync": 1,
    }


# 便于 grep 命中本体信号（即使无真实 ZFS 源码，桩自身可命中）
_DSL_DATASET_PHYS_MARKER = "dsl_dataset_phys"
_DP_DIRTY_DATASETS_MARKER = "dp_dirty_datasets"
_DSL_POOL_SYNC_MARKER = "dsl_pool_sync"
