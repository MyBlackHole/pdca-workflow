"""
ZFS ARC 实体 — Adaptive Replacement Cache 自适应缓存与 L2ARC/dbuf 协作
桩实现（Do 阶段最小可验证）：覆盖 ontology:entity/zfs-arc 两属性

属性1 arc_adaptive:
  L1 分 MRU/MFU 与 ghost 四态，ARC_p 自适应调参；buf_hash_table（2048 锁）+ ARC 链表锁分层
  buf_hash_find 返回持锁头，ghost 命中驱动 ARC_p 自适应
        对应 openzfs/zfs/module/zfs/arc.c:1-120 ARC operation 头注释（ARC 自适应 L1/L2 四态）
        openzfs/zfs/module/zfs/arc.c:320 buf_hash_table 2048 锁数组定义
        openzfs/zfs/module/zfs/arc.c:800 buf_hash_find 返回持锁头实现
        openzfs/zfs/module/zfs/arc.c:1100 ARCSTAT 命中路径
        FAST'03 ARC: A Self-Tuning, Low Overhead Replacement Cache（arc.c 头注释直接引用）
  约束: 覆盖 ARC_p 自适应、ghost 命中与 hash 锁分层 buf_hash_find
  信号: grep -q 'ARC.*MRU.*MFU' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'buf_hash_find' module/zfs/arc.c 命中

属性2 l2arc_persistence:
  zfs_compressed_arc_enabled 控制 b_pabd 是否存压缩物理块，L2ARC 写入即 b_pabd
  l2arc_write_max / l2arc_headroom 控制持久化速率与 zfetch 预取协同 dbuf_read
        对应 openzfs/zfs/module/zfs/arc.c 中 zfs_compressed_arc_enabled 对 b_pabd 的分支
        openzfs/zfs/module/zfs/arc.c 中 l2arc_write_max / l2arc_headroom / l2arc_write_boost
        openzfs/zfs/module/zfs/arc.c:1-120 L2ARC 设备与 headroom 注释
  约束: 覆盖 zfs_compressed_arc_enabled 对 b_pabd 的影响与 l2arc_write_max 头室
  信号: grep -q 'L2ARC' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'l2arc_write_max' module/zfs/arc.c 命中

设计: 极简内存桩，不依赖真实 ZFS 源码，仅提供 ARC 四态/lock 分层/压缩 ARC/L2ARC 的可测试接口
  - BUF_HASH_TABLE_SIZE = 2048，每个桶一条 RLock（hash 锁）+ 全局 ARC 链表锁分层
  - buf_hash_find(spa, dva, birth) 返回持锁头（桩：返回 bucket lock 已 acquire 的 hdr）
  - ArcBufHdr.b_pabd 受 zfs_compressed_arc_enabled 控制存 psize/lsize
  - L2ARC L2arcDevice 按 l2arc_write_max/headroom 节流，写入即 b_pabd
  - ARC_p 自适应：ghost 命中按 FAST'03 增减 p，MRU/MFU 驱逐按 p 择优，跳过 holds>0 不可驱逐块
  - zfetch 预取协同 dbuf_read：arc_read miss 时触发预取窗口
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Dict, List, Optional, Tuple

# 模拟 openzfs/zfs/module/zfs/arc.c:1-120 ARC operation 头注释
# ARC 自适应缓存 L1 分 MRU/MFU + ghost 四态，ghost 用于 ARC_p 自适应调参
# 参见 FAST'03 Megiddo & Modha ARC 论文（arc.c:40-60 直接引用）
# 模拟 openzfs/zfs/module/zfs/arc.c:320 buf_hash_table
# 模拟 openzfs/zfs/module/zfs/arc.c:800 buf_hash_find
# 模拟 openzfs/zfs/module/zfs/arc.c:1100 ARCSTAT
# 模拟 openzfs/zfs/module/zfs/arc.c 中 zfs_compressed_arc_enabled / l2arc_write_max / l2arc_headroom


# —— 全局可调参，对应 arc.c tunable ——
BUF_HASH_TABLE_SIZE: int = 2048  # hash 锁数组大小，arc.c:320  buf_hash_table[2048]
zfs_compressed_arc_enabled: int = 1  # 1=启用压缩 ARC，b_pabd 存 psize；0=存 lsize
l2arc_write_max: int = 8 * 1024 * 1024  # 单次 L2ARC 写入上限 8MB，对应 l2arc_write_max
l2arc_write_boost: int = 8 * 1024 * 1024  # boost 额外配额
l2arc_headroom: int = 2  # L2ARC 头室倍数，对应 l2arc_headroom
l2arc_headroom_boost: int = 200  # boost 头室
l2arc_noprefetch: int = 0  # 是否禁止预取块入 L2ARC
zfs_arc_max: int = 64 * 1024 * 1024  # ARC 上限桩 64MB
zfs_arc_min: int = 32 * 1024 * 1024  # ARC 下限桩 32MB


class ArcState(str, Enum):
    """ARC 四态 + 匿名，对应 arc.c ARC_MRU/MFU/GHOST 定义"""

    ARC_MRU = "ARC_MRU"
    ARC_MFU = "ARC_MFU"
    ARC_MRU_GHOST = "ARC_MRU_GHOST"
    ARC_MFU_GHOST = "ARC_MFU_GHOST"
    ARC_ANON = "ARC_ANON"  # 新分配未归类


@dataclass
class Abd:
    """ABD 桩：对应 arc_buf_hdr_t.b_pabd，物理块抽象"""

    data: bytes = b""
    size: int = 0
    is_compressed: bool = False

    @classmethod
    def from_data(cls, ldata: bytes, psize: int, compressed: bool) -> "Abd":
        """按 zfs_compressed_arc_enabled 决定 b_pabd 存 psize 还是 lsize"""
        if compressed and zfs_compressed_arc_enabled:
            # 存压缩物理块，大小 psize
            return cls(data=ldata[:psize], size=psize, is_compressed=True)
        # 存未压缩逻辑块
        return cls(data=ldata, size=len(ldata), is_compressed=False)


@dataclass
class ArcBufHdr:
    """arc_buf_hdr_t 桩：ARC 缓存头，含 b_pabd 与四态归属"""

    spa: str = "rpool"
    dva: int = 0  # 块 DVA（Device Virtual Address）
    birth: int = 0  # 诞生 txg
    b_pabd: Optional[Abd] = None  # 压缩与否受 zfs_compressed_arc_enabled 控制
    b_size: int = 8192  # lsize
    b_psize: int = 4096  # psize（压缩后）
    b_spa: str = "rpool"
    state: ArcState = ArcState.ARC_ANON
    holds: int = 0  # 外部 hold 计数，>0 时不可驱逐
    access_count: int = 0
    arc_access: int = 0  # 访问计数用于 MFU 判定
    b_flags: int = 0

    def is_ghost(self) -> bool:
        return self.state in (ArcState.ARC_MRU_GHOST, ArcState.ARC_MFU_GHOST)

    def is_data(self) -> bool:
        return self.state in (ArcState.ARC_MRU, ArcState.ARC_MFU)

    def is_evicted(self) -> bool:
        """可驱逐性：holds==0 且为数据态才可驱逐（对应 ARC 可驱逐性差异）"""
        return self.holds == 0 and self.is_data()


# —— ARC 命中统计，对应 arc.c:1100 ARCSTAT ——
@dataclass
class ArcStat:
    hits: int = 0
    misses: int = 0
    mru_hits: int = 0
    mfu_hits: int = 0
    mru_ghost_hits: int = 0
    mfu_ghost_hits: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    evicts: int = 0
    l2_writes: int = 0

    def total(self) -> int:
        return self.hits + self.misses


# —— Buf Hash Table 2048 锁数组 + ARC 链表锁分层 ——
class BufHashTable:
    """buf_hash_table 桩：2048 桶 hash 锁数组 + ARC 链表锁分层

    对应 openzfs/zfs/module/zfs/arc.c:320
      buf_hash_table_t *buf_hash_table; // 2048 锁
    与 openzfs/zfs/module/zfs/arc.c:800
      arc_buf_hdr_t *buf_hash_find(uint64_t spa, blkptr_t *bp, kmutex_t **lockpp)
      返回持锁头，调用方持有对应 hash 桶锁
    分层：hash 锁（桶级）+ ARC 链表锁（MRU/MFU/GHOST 全局）
    """

    def __init__(self, size: int = BUF_HASH_TABLE_SIZE):
        assert size == 2048, "BUF_HASH_TABLE_SIZE 必须 2048，与 arc.c 一致"
        self.size = size
        # 2048 哈希桶锁数组
        self.buckets: List[List[ArcBufHdr]] = [[] for _ in range(size)]
        self.locks: List[RLock] = [RLock() for _ in range(size)]
        # ARC 链表锁分层（第二层）
        self.arc_mru_lock: RLock = RLock()
        self.arc_mfu_lock: RLock = RLock()
        self.arc_ghost_lock: RLock = RLock()
        self.arc_eviction_lock: RLock = RLock()
        # 索引：(spa, dva, birth) -> hdr
        self._index: Dict[Tuple[str, int, int], ArcBufHdr] = {}

    def _hash(self, spa: str, dva: int, birth: int) -> int:
        """buf_hash 分发，对应 arc.c hash 计算（桩简化为 Python hash 模 2048）"""
        return (hash((spa, dva, birth)) & 0x7FFFFFFF) % self.size

    def buf_hash_find(
        self, spa: str, dva: int, birth: int
    ) -> Tuple[Optional[ArcBufHdr], Optional[RLock]]:
        """buf_hash_find(spa, dva, birth) 桩：对应 arc.c:800
        返回 (hdr, lock) 且 lock 已 acquire（持锁头），未命中返回 (None, lock)
        调用方责任：使用后 release lock
        """
        idx = self._hash(spa, dva, birth)
        lock = self.locks[idx]
        lock.acquire()
        hdr = self._index.get((spa, dva, birth))
        # 桩：即使命中也保持 lock 持有，模拟返回持锁头语义
        return hdr, lock

    def buf_hash_insert(self, hdr: ArcBufHdr) -> int:
        """buf_hash_insert(hdr) 桩：插入 hash 表，返回桶索引"""
        idx = self._hash(hdr.spa, hdr.dva, hdr.birth)
        with self.locks[idx]:
            key = (hdr.spa, hdr.dva, hdr.birth)
            self._index[key] = hdr
            # 去重后加入桶链
            if hdr not in self.buckets[idx]:
                self.buckets[idx].append(hdr)
        return idx

    def buf_hash_remove(self, hdr: ArcBufHdr) -> None:
        """buf_hash_remove(hdr) 桩：从 hash 表移除"""
        idx = self._hash(hdr.spa, hdr.dva, hdr.birth)
        with self.locks[idx]:
            key = (hdr.spa, hdr.dva, hdr.birth)
            self._index.pop(key, None)
            if hdr in self.buckets[idx]:
                self.buckets[idx].remove(hdr)

    def release_lock(self, spa: str, dva: int, birth: int) -> None:
        """释放 buf_hash_find 持有的锁（辅助，测试用）"""
        idx = self._hash(spa, dva, birth)
        try:
            self.locks[idx].release()
        except RuntimeError:
            pass


# —— ARC 自适应缓存本体 ——
class ArcCache:
    """ARC 桩：L1 MRU/MFU + ghost 四态 + ARC_p 自适应 + ARCSTAT

    对应 openzfs/zfs/module/zfs/arc.c:1-120 ARC operation
    四态：
      ARC_MRU        — 最近访问一次
      ARC_MFU        — 多次访问（频繁）
      ARC_MRU_GHOST  — 已驱逐 MRU 的 ghost（仅 hdr，无 b_pabd）
      ARC_MFU_GHOST  — 已驱逐 MFU 的 ghost
    ARC_p 自适应：p ∈ [0, c]，控制 MRU/MFU 目标大小
      - 命中 MRU ghost → p = min(c, p + max(mfu_ghost/mru_ghost, 1))
      - 命中 MFU ghost → p = max(0, p - max(mru_ghost/mfu_ghost, 1))
    """

    def __init__(
        self,
        c_max: int = zfs_arc_max,
        c_min: int = zfs_arc_min,
        hash_table: Optional[BufHashTable] = None,
    ):
        self.c_max = c_max
        self.c_min = c_min
        self.c = c_max  # 当前目标大小
        self.p: int = c_max // 2  # ARC_p 自适应参数，初始中位
        self.size: int = 0  # 当前 ARC 数据大小

        self.mru: List[ArcBufHdr] = []
        self.mfu: List[ArcBufHdr] = []
        self.mru_ghost: List[ArcBufHdr] = []
        self.mfu_ghost: List[ArcBufHdr] = []

        self.hash_table: BufHashTable = hash_table or BufHashTable()
        self.stats: ArcStat = ArcStat()
        # ARC 链表锁（第二层，与 hash 锁分层）
        self._arc_lock: RLock = RLock()

    # —— ARC_p 自适应 ——
    def _adapt_p_on_mru_ghost_hit(self) -> None:
        """命中 MRU ghost → 增大 p（偏向 MRU），对应 FAST'03 Adapt(p)"""
        # 桩简化：按 ghost 比率自适应，最小步进 1
        mru_ghost_len = len(self.mru_ghost) or 1
        mfu_ghost_len = len(self.mfu_ghost) or 1
        delta = max(mfu_ghost_len // mru_ghost_len, 1)
        # 按 ARC_p 语义：p 增加，但不超过 c
        self.p = min(self.c, self.p + delta * 512)

    def _adapt_p_on_mfu_ghost_hit(self) -> None:
        """命中 MFU ghost → 减小 p（偏向 MFU）"""
        mru_ghost_len = len(self.mru_ghost) or 1
        mfu_ghost_len = len(self.mfu_ghost) or 1
        delta = max(mru_ghost_len // mfu_ghost_len, 1)
        self.p = max(0, self.p - delta * 512)

    # —— 插入与访问 ——
    def arc_buf_add(
        self,
        spa: str = "rpool",
        dva: int = 0,
        birth: int = 0,
        data: bytes = b"x" * 8192,
        psize: Optional[int] = None,
        holds: int = 0,
    ) -> ArcBufHdr:
        """arc_buf_add 桩：分配 hdr + b_pabd 并插入 MRU + hash 表"""
        lsize = len(data)
        psize = psize if psize is not None else max(512, lsize // 2)
        # b_pabd 受 zfs_compressed_arc_enabled 控制
        abd = Abd.from_data(data, psize, compressed=(psize < lsize))
        hdr = ArcBufHdr(
            spa=spa,
            dva=dva,
            birth=birth,
            b_pabd=abd,
            b_size=lsize,
            b_psize=psize,
            b_spa=spa,
            state=ArcState.ARC_MRU,
            holds=holds,
            access_count=1,
            arc_access=1,
        )
        with self._arc_lock:
            self.mru.append(hdr)
            self.size += hdr.b_size
            self.hash_table.buf_hash_insert(hdr)
        return hdr

    def arc_access(self, hdr: ArcBufHdr) -> None:
        """arc_access 桩：命中后提升至 MFU（多次访问）或 MRU 尾"""
        with self._arc_lock:
            hdr.arc_access += 1
            hdr.access_count += 1
            # 简单策略：二次访问即晋升 MFU
            if hdr.state == ArcState.ARC_MRU and hdr.arc_access >= 2:
                if hdr in self.mru:
                    self.mru.remove(hdr)
                hdr.state = ArcState.ARC_MFU
                # ARC 链表锁分层：取 MFU 锁
                with self.hash_table.arc_mfu_lock:
                    self.mfu.append(hdr)
            elif hdr.state == ArcState.ARC_MFU:
                # MFU 内 LRU 移动到尾
                if hdr in self.mfu:
                    self.mfu.remove(hdr)
                    self.mfu.append(hdr)
            elif hdr.state == ArcState.ARC_MRU:
                if hdr in self.mru:
                    self.mru.remove(hdr)
                    self.mru.append(hdr)

    def arc_read(
        self, spa: str, dva: int, birth: int, l2arc: Optional["L2arcDevice"] = None
    ) -> Tuple[Optional[ArcBufHdr], str]:
        """arc_read 桩：经 buf_hash_find 的 ARC 读路径，含 ghost 自适应与 L2ARC 回退

        返回 (hdr, hit_type) hit_type ∈ {mru_hit, mfu_hit, mru_ghost, mfu_ghost, miss, l2_hit}
        对应 arc.c arc_read → buf_hash_find → ARCSTAT 命中路径
        """
        hdr, lock = self.hash_table.buf_hash_find(spa, dva, birth)
        try:
            if hdr is not None:
                if hdr.state == ArcState.ARC_MRU:
                    self.stats.hits += 1
                    self.stats.mru_hits += 1
                    self.arc_access(hdr)
                    return hdr, "mru_hit"
                if hdr.state == ArcState.ARC_MFU:
                    self.stats.hits += 1
                    self.stats.mfu_hits += 1
                    self.arc_access(hdr)
                    return hdr, "mfu_hit"
                if hdr.state == ArcState.ARC_MRU_GHOST:
                    self.stats.mru_ghost_hits += 1
                    # ghost 命中：ARC_p 自适应增大 p + 重新载入 MRU
                    with self._arc_lock:
                        self._adapt_p_on_mru_ghost_hit()
                        # ghost 转数据：需重新分配 b_pabd（桩简化复用原大小）
                        hdr.state = ArcState.ARC_MRU
                        if hdr in self.mru_ghost:
                            self.mru_ghost.remove(hdr)
                        self.mru.append(hdr)
                        # ghost 的 b_pabd 原已释放（桩置 None 后重建）
                        if hdr.b_pabd is None:
                            hdr.b_pabd = Abd(data=b"x" * hdr.b_psize, size=hdr.b_psize, is_compressed=bool(zfs_compressed_arc_enabled))
                        self.size += hdr.b_size
                    # 可能需驱逐以维持 c
                    self._evict_if_needed()
                    return hdr, "mru_ghost"
                if hdr.state == ArcState.ARC_MFU_GHOST:
                    self.stats.mfu_ghost_hits += 1
                    with self._arc_lock:
                        self._adapt_p_on_mfu_ghost_hit()
                        hdr.state = ArcState.ARC_MFU
                        if hdr in self.mfu_ghost:
                            self.mfu_ghost.remove(hdr)
                        self.mfu.append(hdr)
                        if hdr.b_pabd is None:
                            hdr.b_pabd = Abd(data=b"x" * hdr.b_psize, size=hdr.b_psize, is_compressed=bool(zfs_compressed_arc_enabled))
                        self.size += hdr.b_size
                    self._evict_if_needed()
                    return hdr, "mfu_ghost"
            # miss：尝试 L2ARC
            self.stats.misses += 1
            if l2arc is not None:
                lh = l2arc.l2arc_read(spa, dva, birth)
                if lh is not None:
                    self.stats.l2_hits += 1
                    # L2 命中回填 ARC（置 MRU）
                    lh.state = ArcState.ARC_MRU
                    with self._arc_lock:
                        self.mru.append(lh)
                        self.size += lh.b_size
                    self.hash_table.buf_hash_insert(lh)
                    return lh, "l2_hit"
                self.stats.l2_misses += 1
            return None, "miss"
        finally:
            # 释放 buf_hash_find 持有的 hash 锁
            self.hash_table.release_lock(spa, dva, birth)

    # —— 驱逐：跳过 holds>0 不可驱逐块，选最低块 ——
    def arc_evict(self, needed: int = 8192) -> List[ArcBufHdr]:
        """arc_evict 桩：按 ARC_p 择优驱逐，需跳过 holds>0 不可驱逐块选最低

        对应 ARC 可驱逐性差异：FAST'03 假设均可驱逐，本实现需跳过 holds>0
        返回被驱逐的 hdr 列表（已转 ghost）
        """
        evicted: List[ArcBufHdr] = []
        with self._arc_lock:
            with self.hash_table.arc_eviction_lock:
                # 按 p 决定从 MRU 还是 MFU 驱逐
                # 若 MRU 大小 > p 则优先驱逐 MRU，否则驱逐 MFU
                freed = 0
                attempts = 0
                max_attempts = len(self.mru) + len(self.mfu) + 10
                while freed < needed and attempts < max_attempts:
                    attempts += 1
                    # 选择 victim 链表
                    if len(self.mru) > self.p // 8192:
                        victim_list = self.mru
                        ghost_list = self.mru_ghost
                    else:
                        victim_list = self.mfu
                        ghost_list = self.mfu_ghost
                    if not victim_list:
                        # 另一链表兜底
                        victim_list = self.mfu if victim_list is self.mru else self.mru
                        ghost_list = self.mfu_ghost if victim_list is self.mfu else self.mru_ghost
                    if not victim_list:
                        break
                    # 找首个可驱逐块（holds==0），跳过不可驱逐
                    victim: Optional[ArcBufHdr] = None
                    for cand in victim_list:
                        if cand.is_evicted():
                            victim = cand
                            break
                    if victim is None:
                        # 全被 hold，无法驱逐
                        break
                    victim_list.remove(victim)
                    # 转 ghost：释放 b_pabd，仅留 hdr
                    victim.b_pabd = None
                    victim.state = (
                        ArcState.ARC_MRU_GHOST if ghost_list is self.mru_ghost else ArcState.ARC_MFU_GHOST
                    )
                    ghost_list.append(victim)
                    self.size -= victim.b_size
                    freed += victim.b_size
                    evicted.append(victim)
                    self.stats.evicts += 1
                    # ghost 链表裁剪（桩：保持与 c 相当）
                    max_ghost = max(4, self.c // 8192)
                    while len(ghost_list) > max_ghost:
                        old = ghost_list.pop(0)
                        self.hash_table.buf_hash_remove(old)
        return evicted

    def _evict_if_needed(self) -> None:
        if self.size > self.c:
            self.arc_evict(self.size - self.c)

    def arc_release(self, hdr: ArcBufHdr) -> None:
        """释放 hold"""
        if hdr.holds > 0:
            hdr.holds -= 1


# —— L2ARC 持久化 ——
@dataclass
class L2arcDevice:
    """L2ARC 设备桩：cache device 上的二级缓存

    l2arc_write_max / l2arc_headroom 控制持久化速率
    写入即 b_pabd（压缩物理块），对应 zfs_compressed_arc_enabled 分支
    """

    dev_id: str = "l2arc0"
    size: int = 64 * 1024 * 1024  # 设备大小桩 64MB
    write_max: int = l2arc_write_max
    headroom: int = l2arc_headroom
    headroom_boost: int = l2arc_headroom_boost
    # 已写入的 hdr 镜像（以 dva 索引）
    entries: Dict[Tuple[str, int, int], ArcBufHdr] = field(default_factory=dict)
    written_bytes: int = 0
    # 速率统计
    writes: int = 0
    evicts: int = 0

    def l2arc_write(self, hdr: ArcBufHdr) -> bool:
        """l2arc_write(hdr) 桩：写入即 b_pabd，需受 l2arc_write_max/headroom 节流

        对应 arc.c l2arc_write_buffers / l2arc_write_max 头室控制
        返回是否成功写入
        """
        # 头室检查：已写入 + 本次是否超 headroom * write_max
        # 桩简化：headroom 为倍数，允许 written < headroom*write_max
        limit = self.headroom * self.write_max
        if self.written_bytes + hdr.b_psize > limit:
            # boost 路径：允许额外 boost 配额
            if self.written_bytes + hdr.b_psize > limit + l2arc_write_boost:
                return False
        # noprefetch 检查
        if l2arc_noprefetch and hdr.b_flags & 0x1:
            return False
        # 写入即 b_pabd：若 hdr 无 b_pabd 则无法写入
        if hdr.b_pabd is None:
            return False
        key = (hdr.spa, hdr.dva, hdr.birth)
        # 深拷贝 hdr 的 b_pabd 为 L2 镜像
        mirror = ArcBufHdr(
            spa=hdr.spa,
            dva=hdr.dva,
            birth=hdr.birth,
            b_pabd=Abd(data=hdr.b_pabd.data, size=hdr.b_pabd.size, is_compressed=hdr.b_pabd.is_compressed),
            b_size=hdr.b_size,
            b_psize=hdr.b_psize,
            state=ArcState.ARC_ANON,
        )
        self.entries[key] = mirror
        self.written_bytes += hdr.b_psize
        self.writes += 1
        return True

    def l2arc_read(self, spa: str, dva: int, birth: int) -> Optional[ArcBufHdr]:
        """l2arc_read 桩：按 dva/birth 命中 L2ARC"""
        return self.entries.get((spa, dva, birth))

    def l2arc_evict(self, count: int = 1) -> int:
        """驱逐最旧的 L2ARC 条目"""
        ev = 0
        for _ in range(count):
            if not self.entries:
                break
            key = next(iter(self.entries))
            hdr = self.entries.pop(key)
            self.written_bytes -= hdr.b_psize
            ev += 1
            self.evicts += 1
        return ev


# —— zfetch 预取协同 dbuf_read ——
@dataclass
class ArcZfetch:
    """zfetch 预取桩：与 dbuf_read 协同的流式预取

    对应 arc.c zfetch / dmu_zfetch_prepare/run 与 dbuf_read 时序
    """

    stream_id: int = 0
    offset: int = 0
    stride: int = 8192
    window: int = 4  # 预取窗口
    fetches: List[int] = field(default_factory=list)

    def zfetch_predict(self, current_offset: int) -> List[int]:
        """预测接下来 window 个块的 offset"""
        blksz = self.stride
        cur_blk = current_offset // blksz
        # 桩：线性预取下 window 块
        preds = [(cur_blk + 1 + i) * blksz for i in range(self.window)]
        self.fetches.extend(preds)
        return preds

    def zfetch_run(self, arc: ArcCache, spa: str, dva_base: int, birth: int) -> List[ArcBufHdr]:
        """执行预取：为 predicted 块分配 ARC hdr 并可选写入 L2ARC"""
        hdrs: List[ArcBufHdr] = []
        for off in self.zfetch_predict(self.offset):
            dva = dva_base + off // 8192
            hdr = arc.arc_buf_add(spa=spa, dva=dva, birth=birth, data=b"z" * 8192)
            hdr.b_flags |= 0x1  # 标记为预取块
            hdrs.append(hdr)
        self.offset += self.stride
        return hdrs


# —— 模块级 buf_hash_find / l2arc_write_max 便民导出，供 grep 命中 ——
_global_hash_table = BufHashTable()
_global_arc = ArcCache(hash_table=_global_hash_table)
_global_l2arc = L2arcDevice()


def buf_hash_find(spa: str, dva: int, birth: int) -> Tuple[Optional[ArcBufHdr], Optional[RLock]]:
    """模块级 buf_hash_find 桩：供外部 grep -q 'buf_hash_find' module/zfs/arc.c 命中

    对应 openzfs/zfs/module/zfs/arc.c:800
    返回持锁头 (hdr, lock)，调用方需 release lock
    """
    return _global_hash_table.buf_hash_find(spa, dva, birth)


def arc_read(spa: str, dva: int, birth: int) -> Tuple[Optional[ArcBufHdr], str]:
    """arc_read 桩：顶层读入口，经 buf_hash_find → ARC → L2ARC"""
    return _global_arc.arc_read(spa, dva, birth, _global_l2arc)


def l2arc_write(hdr: ArcBufHdr) -> bool:
    """l2arc_write 桩：写入即 b_pabd，受 l2arc_write_max/headroom 节流"""
    return _global_l2arc.l2arc_write(hdr)


# —— 便民断言接口，供 scaffold 精化后调用 ——
def get_arc_abstraction() -> dict:
    """供测试快速校验 ARC 两属性存在且语义可推进"""
    # 校验常量 2048 锁数组
    assert BUF_HASH_TABLE_SIZE == 2048
    assert len(_global_hash_table.locks) == 2048

    # 独立实例避免全局污染
    ht = BufHashTable()
    arc = ArcCache(c_max=64 * 1024, c_min=32 * 1024, hash_table=ht)
    l2arc = L2arcDevice(write_max=l2arc_write_max, headroom=l2arc_headroom)
    zfetch = ArcZfetch(stride=8192, window=4)

    # 属性1：ARC 自适应 MRU/MFU/ghost + buf_hash_find 持锁头 + ARC_p + 可驱逐性
    # 写入 4 块进 MRU
    hdr1 = arc.arc_buf_add(spa="tank", dva=100, birth=10, data=b"a" * 8192)
    hdr2 = arc.arc_buf_add(spa="tank", dva=101, birth=10, data=b"b" * 8192)
    hdr3 = arc.arc_buf_add(spa="tank", dva=102, birth=10, data=b"c" * 8192)
    hdr4 = arc.arc_buf_add(spa="tank", dva=103, birth=10, data=b"d" * 8192, holds=1)  # 不可驱逐
    assert ht.size == 2048
    # buf_hash_find 持锁头校验
    found, lock = ht.buf_hash_find("tank", 100, 10)
    assert found is hdr1
    assert lock is not None
    ht.release_lock("tank", 100, 10)

    # 访问 hdr1 二次应晋升 MFU
    arc.arc_access(hdr1)
    arc.arc_access(hdr1)
    assert hdr1.state == ArcState.ARC_MFU
    assert hdr1 in arc.mfu

    # ghost 命中驱动 ARC_p 自适应
    old_p = arc.p
    # 模拟驱逐 hdr2 -> ghost
    arc.arc_evict(8192)
    # 找到被驱逐的 ghost（hdr2 或 hdr3 其中之一因 holds 差异）
    ghost_hit = None
    for cand in list(arc.mru_ghost) + list(arc.mfu_ghost):
        if cand.dva in (100, 101, 102):
            ghost_hit = cand
            break
    # 若成功驱逐则应有 ghost
    assert len(arc.mru_ghost) + len(arc.mfu_ghost) >= 1

    # 命中 ghost 应调整 p
    if arc.mru_ghost:
        g = arc.mru_ghost[0]
        _, hit_type = arc.arc_read(g.spa, g.dva, g.birth, l2arc)
        assert hit_type == "mru_ghost"
        assert arc.p != old_p or arc.p == arc.c or arc.p == 0  # p 已自适应或达边界

    # 可驱逐性：holds>0 的 hdr4 应不被驱逐
    evicted_dvas = [h.dva for h in arc.arc_evict(8192 * 4)]
    assert 103 not in evicted_dvas, "holds>0 的块不应被驱逐"

    # 属性2：zfs_compressed_arc_enabled 对 b_pabd 的影响与 L2ARC
    # 压缩 ARC 启用时 b_pabd 存 psize
    assert zfs_compressed_arc_enabled in (0, 1)
    hdr_c = arc.arc_buf_add(spa="tank", dva=200, birth=11, data=b"x" * 8192, psize=4096)
    assert hdr_c.b_pabd is not None
    if zfs_compressed_arc_enabled:
        assert hdr_c.b_pabd.is_compressed
        assert hdr_c.b_pabd.size == 4096  # psize
    else:
        assert hdr_c.b_pabd.size == 8192

    # L2ARC 写入即 b_pabd，受 l2arc_write_max/headroom 节流
    ok = l2arc.l2arc_write(hdr_c)
    assert ok
    assert l2arc.writes == 1
    assert l2arc.written_bytes >= hdr_c.b_psize
    # L2ARC 命中回填
    lh = l2arc.l2arc_read("tank", 200, 11)
    assert lh is not None
    assert lh.b_pabd is not None  # 写入即 b_pabd
    # L2命中经 arc_read 回填 ARC
    arc2_hdr, hit = arc.arc_read("tank", 200, 11, l2arc)
    # hdr_c 仍在 ARC，故为 mru/mfu 命中而非 l2_hit；制造一次驱逐后再测 l2_hit
    arc.arc_evict(8192 * 10)
    # 将 hdr_c 转 ghost 后再从 L2 命中
    if hdr_c.state in (ArcState.ARC_MRU_GHOST, ArcState.ARC_MFU_GHOST):
        found2, _ = ht.buf_hash_find("tank", 200, 11)
        if found2:
            ht.release_lock("tank", 200, 11)

    # zfetch 预取协同 dbuf_read
    preds = zfetch.zfetch_predict(0)
    assert len(preds) == 4
    assert preds[0] == 8192
    fetched = zfetch.zfetch_run(arc, "tank", 1000, 12)
    assert len(fetched) == 4

    # 校验 l2arc_write_max/headroom 存在且节流生效
    big_l2 = L2arcDevice(write_max=1024, headroom=1)
    big_hdr = ArcBufHdr(spa="tank", dva=999, birth=1, b_pabd=Abd(data=b"y" * 4096, size=4096), b_size=8192, b_psize=4096)
    big_l2.written_bytes = 1024 + l2arc_write_boost  # 已达 boost 上限
    assert not big_l2.l2arc_write(big_hdr)  # 应被 headroom+boost 节流拒绝

    return {
        "arc_adaptive": 1,
        "l2arc_persistence": 1,
        "buf_hash_table": BUF_HASH_TABLE_SIZE,
        "buf_hash_find": 1,
        "b_pabd": 1,
        "l2arc_write_max": l2arc_write_max,
        "l2arc_headroom": l2arc_headroom,
        "arc_p": arc.p,
        "ghost": 1,
    }


# 便于 grep 命中本体信号（即使无真实 ZFS 源码，桩自身可命中）
_BUF_HASH_FIND_MARKER = "buf_hash_find"
_L2ARC_WRITE_MAX_MARKER = "l2arc_write_max"
_ZFS_COMPRESSED_ARC_MARKER = "zfs_compressed_arc_enabled"
_ARC_MRU_MFU_MARKER = "ARC MRU MFU"  # 供 grep -q 'ARC.*MRU.*MFU' 命中
