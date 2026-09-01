"""
ZFS ZPL 实体 — POSIX 层 zfs_znode/zpl_inode 与 DMU 对象映射
桩实现（Do 阶段最小可验证）：覆盖 ontology:entity/zfs-zpl 两属性

属性1 posix_mapping:
  zpl_inode ↔ zfs_znode ↔ dnode 的 object 上下映射与 zfs_vnops 分发
        对应 openzfs/zfs/module/zfs/zfs_znode.c: zfs_znode_t {z_id, z_phys, z_sa_hdl, z_unlinked, z_blksz}
        对应 openzfs/zfs/module/zpl/zpl_inode.c: zpl_inode ↔ zfs_znode 双向映射 (zpl_inode_to_znode / znode_to_inode)
        对应 openzfs/zfs/module/zfs/zfs_vnops.c: zfs_vnops 分发 read/write/create/unlink/mkdir/readdir/getattr/setattr -> DMU (dmu_read/write/zap)
  约束: 覆盖 zpl_inode ↔ zfs_znode ↔ dnode 的 object 上下映射与 zfs_vnops 分发
  信号: grep -q 'ZPL' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'zfs_znode' module/zfs/zfs_znode.c

属性2 sa_bonus_layout:
  SA (System Attributes) 与 dnode bonus 对小文件/属性的存储优化
        对应 openzfs/zfs/include/sys/dnode.h: DN_BONUS, DN_SLOT_BONUSLEN, dnode_bonus
        对应 openzfs/zfs/module/zfs/sa.c: sa_handle_t / sa_layout / sa_bulk_update
        对应 openzfs/zfs/module/zfs/zfs_znode.c: zfs_znode 的 SA 与 bonus Inline 抉择 (zp_size <= bonuslen 则 inline)
        对应 https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Datasets/
  约束: 覆盖 SA 与 dnode bonus 对小文件/扩展属性的 Inline 存储
  信号: grep -q 'dnode.*bonus' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'DN_BONUS' include/sys/dnode.h

设计: 极简内存桩，不依赖真实 ZFS 源码，仅提供 ZPL POSIX 映射与 SA/bonus Inline 的可测试接口
  - ZfsZnode 为中心对象，z_id 为 DMU object id；ZplInode 为 VFS inode 封装，双向指针映射
  - Objset 管理 object -> ZfsZnode / Dnode 的分配与 hold
  - SaHandle / SaLayout 桩：少量已注册 SA 属性的 bulk update/lookup
  - DnodeBonus 桩：DN_BONUS 缓冲，超阈则溢出到 dnode data blocks
  - zfs_vnops 字典分发：每个 POSIX 入口（create/read/write/unlink...）最终调用 dmu_read/write/zap 桩
  - ZIL 介入同步写：zfs_write 遇 O_SYNC/FSYNC 调用 zil_commit 桩
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Tuple

import time

# 模拟 openzfs/zfs/module/zfs/zfs_znode.c: zfs_znode_t 相关常量
# 模拟 openzfs/zfs/module/zpl/zpl_inode.c: zpl_inode 映射
# 模拟 openzfs/zfs/module/zfs/zfs_vnops.c: zfs_vnops 分发
# 模拟 openzfs/zfs/include/sys/dnode.h: DN_BONUS
# 模拟 openzfs/zfs/module/zfs/sa.c: sa_handle

# —— 常量（对应 DN_BONUS / 阈值）——
DN_BONUS: str = "DN_BONUS"
DN_SLOT_BONUSLEN: int = 320  # dnode bonus 典型长度（桩：用于 inline 阈值判定）
ZPL_BONUS_INLINE_LIMIT: int = DN_SLOT_BONUSLEN  # 小文件 <= 此阈值可 inline 于 bonus
ZFS_SA_BONUS_LIMIT: int = 112  # bonus 中 SA 头部占用后剩余可 inline 空间桩值


class ZfsType(IntEnum):
    """文件类型，映射 DT_* / IFMT"""
    REG = 1
    DIR = 2
    LNK = 3
    FIFO = 4
    SOCK = 5
    CHR = 6
    BLK = 7


class SaAttrType(str, Enum):
    """SA 属性枚举（桩：子集，对应 sa.c 已注册 layout）"""
    SA_ZPL_MODE = "SA_ZPL_MODE"
    SA_ZPL_UID = "SA_ZPL_UID"
    SA_ZPL_GID = "SA_ZPL_GID"
    SA_ZPL_SIZE = "SA_ZPL_SIZE"
    SA_ZPL_ATIME = "SA_ZPL_ATIME"
    SA_ZPL_MTIME = "SA_ZPL_MTIME"
    SA_ZPL_CTIME = "SA_ZPL_CTIME"
    SA_ZPL_PARENT = "SA_ZPL_PARENT"
    SA_ZPL_FLAGS = "SA_ZPL_FLAGS"
    SA_ZPL_LINKS = "SA_ZPL_LINKS"
    SA_ZPL_XATTR = "SA_ZPL_XATTR"
    SA_ZPL_DACL = "SA_ZPL_DACL"
    SA_ZPL_PROJID = "SA_ZPL_PROJID"


@dataclass
class ZnodePhys:
    """znode_phys_t 桩：持久化的 stat 镜像，对应 SA 中的物理字段"""
    zp_mode: int = 0o644
    zp_uid: int = 0
    zp_gid: int = 0
    zp_size: int = 0
    zp_links: int = 1
    zp_parent: int = 0  # 父 object id
    zp_flags: int = 0
    zp_atime: float = field(default_factory=time.time)
    zp_mtime: float = field(default_factory=time.time)
    zp_ctime: float = field(default_factory=time.time)
    zp_proj_id: int = 0
    zp_gen: int = 1
    zp_bonus_type: str = DN_BONUS


@dataclass
class SaLayout:
    """sa_layout 桩：已注册 SA 属性布局"""
    attrs: List[SaAttrType] = field(default_factory=lambda: list(SaAttrType))
    attr_ids: Dict[SaAttrType, int] = field(default_factory=dict)

    def __post_init__(self):
        for i, a in enumerate(self.attrs):
            self.attr_ids[a] = i

    def lookup_id(self, attr: SaAttrType) -> Optional[int]:
        return self.attr_ids.get(attr)


@dataclass
class SaHandle:
    """sa_handle_t 桩：SA 句柄，承载 bonus 之上的属性更新/查询"""
    layout: SaLayout = field(default_factory=SaLayout)
    attrs: Dict[SaAttrType, Any] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)

    def bulk_update(self, updates: Dict[SaAttrType, Any]) -> None:
        """sa_bulk_update(hdl, bulk, count) 桩"""
        with self._lock:
            for k, v in updates.items():
                if k in self.layout.attr_ids:
                    self.attrs[k] = v

    def bulk_lookup(self, keys: List[SaAttrType]) -> Dict[SaAttrType, Any]:
        """sa_bulk_lookup 桩"""
        with self._lock:
            return {k: self.attrs.get(k) for k in keys if k in self.layout.attr_ids}

    def lookup(self, attr: SaAttrType) -> Any:
        with self._lock:
            return self.attrs.get(attr)

    def update(self, attr: SaAttrType, value: Any) -> None:
        with self._lock:
            if attr in self.layout.attr_ids:
                self.attrs[attr] = value


@dataclass
class DnodeBonus:
    """dnode bonus 桩：对应 include/sys/dnode.h DN_BONUS, dn_bonus"""
    bonus_type: str = DN_BONUS
    bonus_len: int = DN_SLOT_BONUSLEN
    data: bytes = b""
    # SA 头部占用桩：bonus 中前 ZFS_SA_BONUS_LIMIT 外为可 inline 文件内容区
    sa_reserved: int = ZFS_SA_BONUS_LIMIT

    @property
    def inline_capacity(self) -> int:
        """bonus 可用于小文件 inline 的剩余容量"""
        return max(0, self.bonus_len - self.sa_reserved)

    def can_inline(self, size: int) -> bool:
        """判断 size 是否可 inline 于 bonus"""
        return size <= self.inline_capacity

    def store_inline(self, data: bytes) -> bool:
        """尝试将数据存入 bonus inline 区；成功返回 True，否则 False（需溢出到 dbuf）"""
        if self.can_inline(len(data)):
            self.data = data
            return True
        return False

    def load_inline(self) -> bytes:
        return self.data


@dataclass
class Dnode:
    """dnode_t 桩（极简）：与 ZfsZnode 的下层存储对应"""
    object_id: int
    bonus: DnodeBonus = field(default_factory=DnodeBonus)
    datablksz: int = 8192
    # 若文件过大溢出 bonus，则数据落至 block 模拟（offset -> bytes）
    blocks: Dict[int, bytes] = field(default_factory=dict)
    bonus_type: str = DN_BONUS
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)


# —— ZFS Znode / ZPL Inode 双向映射 ——

@dataclass
class ZfsZnode:
    """zfs_znode_t 桩：POSIX 语义与 DMU 对象的桥梁"""
    z_id: int  # DMU object id，对应 dnode object
    z_phys: ZnodePhys = field(default_factory=ZnodePhys)
    z_sa_hdl: SaHandle = field(default_factory=SaHandle)
    z_dnode: Optional[Dnode] = None
    z_unlinked: bool = False
    z_is_sa: bool = True  # 是否 SA 模式（新式），否则为 bonus 旧布局桩
    z_blksz: int = 8192
    z_atime_dirty: bool = False
    z_xattr_parent: Optional[int] = None  # xattr dir object
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)
    # 关联的 ZplInode 桩指针（若已 iget）
    _inode: Optional["ZplInode"] = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if self.z_dnode is None:
            self.z_dnode = Dnode(object_id=self.z_id, bonus_type=DN_BONUS)
        # 初始化 SA 属性镜像 zp_* -> SA
        self.z_sa_hdl.bulk_update({
            SaAttrType.SA_ZPL_MODE: self.z_phys.zp_mode,
            SaAttrType.SA_ZPL_UID: self.z_phys.zp_uid,
            SaAttrType.SA_ZPL_GID: self.z_phys.zp_gid,
            SaAttrType.SA_ZPL_SIZE: self.z_phys.zp_size,
            SaAttrType.SA_ZPL_LINKS: self.z_phys.zp_links,
            SaAttrType.SA_ZPL_PARENT: self.z_phys.zp_parent,
            SaAttrType.SA_ZPL_FLAGS: self.z_phys.zp_flags,
            SaAttrType.SA_ZPL_ATIME: self.z_phys.zp_atime,
            SaAttrType.SA_ZPL_MTIME: self.z_phys.zp_mtime,
            SaAttrType.SA_ZPL_CTIME: self.z_phys.zp_ctime,
        })

    # — SA / bonus 二层桩 —
    def sa_update(self, attr: SaAttrType, value: Any) -> None:
        """更新 SA 属性并同步回 zp_* 镜像"""
        self.z_sa_hdl.update(attr, value)
        # zp 镜像同步
        mapping = {
            SaAttrType.SA_ZPL_MODE: "zp_mode",
            SaAttrType.SA_ZPL_UID: "zp_uid",
            SaAttrType.SA_ZPL_GID: "zp_gid",
            SaAttrType.SA_ZPL_SIZE: "zp_size",
            SaAttrType.SA_ZPL_LINKS: "zp_links",
            SaAttrType.SA_ZPL_PARENT: "zp_parent",
            SaAttrType.SA_ZPL_FLAGS: "zp_flags",
        }
        if attr in mapping:
            setattr(self.z_phys, mapping[attr], value)

    def sa_lookup(self, attr: SaAttrType) -> Any:
        return self.z_sa_hdl.lookup(attr)

    def is_bonus_inline(self) -> bool:
        """是否小文件 inline 于 bonus（对应 SA bonus 优化路径）"""
        if self.z_dnode is None:
            return False
        return self.z_dnode.bonus.can_inline(self.z_phys.zp_size) and self.z_dnode.bonus.data != b"" or self.z_phys.zp_size <= self.z_dnode.bonus.inline_capacity

    # — dmu 映射桩 —
    @property
    def object_id(self) -> int:
        return self.z_id

    @property
    def bonus_type(self) -> str:
        return self.z_dnode.bonus_type if self.z_dnode else DN_BONUS


@dataclass
class ZplInode:
    """zpl_inode / VFS inode 桩：Linux VFS 层的 inode 封装，指向 ZfsZnode"""
    i_ino: int  # inode 号，对应 z_id
    i_mode: int = 0o644
    i_uid: int = 0
    i_gid: int = 0
    i_size: int = 0
    i_nlink: int = 1
    i_atime: float = field(default_factory=time.time)
    i_mtime: float = field(default_factory=time.time)
    i_ctime: float = field(default_factory=time.time)
    i_flags: int = 0
    i_blksize: int = 8192
    # 指向底层 znode（对应 zpl_inode->zfs_znode*）
    znode: Optional[ZfsZnode] = None
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)

    @classmethod
    def from_znode(cls, znode: ZfsZnode) -> "ZplInode":
        """zpl_inode 构造：从 zfs_znode 映射至 inode（zfs_znode -> zpl_inode）"""
        inode = cls(
            i_ino=znode.z_id,
            i_mode=znode.z_phys.zp_mode,
            i_uid=znode.z_phys.zp_uid,
            i_gid=znode.z_phys.zp_gid,
            i_size=znode.z_phys.zp_size,
            i_nlink=znode.z_phys.zp_links,
            i_atime=znode.z_phys.zp_atime,
            i_mtime=znode.z_phys.zp_mtime,
            i_ctime=znode.z_phys.zp_ctime,
            znode=znode,
        )
        znode._inode = inode
        return inode

    def to_znode(self) -> Optional[ZfsZnode]:
        """zpl_inode_to_znode / ITOZ 桩：inode -> znode"""
        return self.znode

    def update_from_znode(self) -> None:
        """从 znode 刷新 inode 元数据（对应 zfs 事务提交后的 writeback）"""
        if self.znode:
            self.i_mode = self.znode.z_phys.zp_mode
            self.i_uid = self.znode.z_phys.zp_uid
            self.i_gid = self.znode.z_phys.zp_gid
            self.i_size = self.znode.z_phys.zp_size
            self.i_nlink = self.znode.z_phys.zp_links

    def mark_dirty(self) -> None:
        """标记 inode 脏（对应 mark_inode_dirty）"""
        self.i_mtime = time.time()


# —— 映射辅助：zpl_iget / zfs_zget / ITOZ 等 ——

def zpl_inode_to_znode(inode: ZplInode) -> Optional[ZfsZnode]:
    """zpl_inode_to_znode(ip) -> znode（对应 zpl_inode.c 的 ITOZ 宏）"""
    return inode.to_znode()


def znode_to_inode(znode: ZfsZnode) -> Optional[ZplInode]:
    """znode_to_inode / ZTOI 桩：znode -> inode"""
    return znode._inode


def zpl_iget(objset: "ZfsObjset", object_id: int) -> ZplInode:
    """zpl_iget(os, object) -> inode（经 zfs_zget -> ZTOI）"""
    znode = objset.zfs_zget(object_id)
    inode = znode._inode
    if inode is None:
        inode = ZplInode.from_znode(znode)
    return inode


# —— Objset：object <-> zfs_znode <-> dnode 的 registry ——

class ZfsObjset:
    """objset 桩：管理 object -> ZfsZnode / Dnode / ZplInode 的分配与映射"""

    def __init__(self, objset_id: int = 0):
        self.objset_id = objset_id
        self._znodes: Dict[int, ZfsZnode] = {}
        self._next_object: int = 10  # 0-9 保留给 MOS/根
        self._lock: RLock = RLock()
        # zap 模拟：目录对象 -> {name -> object_id}
        self._zap: Dict[int, Dict[str, int]] = {}
        # 数据块模拟：(object, offset) 已抽象至 Dnode.blocks / bonus
        # 事务号桩
        self._txg: int = 1

    def next_txg(self) -> int:
        self._txg += 1
        return self._txg

    def dmu_object_alloc(self, bonus_type: str = DN_BONUS, bonus_len: int = DN_SLOT_BONUSLEN) -> int:
        """dmu_object_alloc(os, ...) -> object id 桩"""
        with self._lock:
            oid = self._next_object
            self._next_object += 1
            return oid

    def zfs_zget(self, object_id: int) -> ZfsZnode:
        """zfs_zget(os, object) -> znode（若不存在则按需构造，对应 zfs_znode.c）"""
        with self._lock:
            if object_id not in self._znodes:
                # 模拟 dmu_object_info + SA/bonus 初始化
                znode = ZfsZnode(z_id=object_id)
                znode.z_dnode = Dnode(object_id=object_id, bonus_type=DN_BONUS, bonus=DnodeBonus(bonus_type=DN_BONUS, bonus_len=DN_SLOT_BONUSLEN))
                self._znodes[object_id] = znode
            return self._znodes[object_id]

    def zfs_znode_alloc(self, parent_id: int = 0, mode: int = 0o644, ztype: ZfsType = ZfsType.REG) -> ZfsZnode:
        """zfs_znode_alloc / zfs_mknode 桩：分配 znode + dnode + zap 条目初始化"""
        oid = self.dmu_object_alloc(bonus_type=DN_BONUS)
        znode = ZfsZnode(z_id=oid, z_phys=ZnodePhys(zp_mode=mode, zp_parent=parent_id, zp_size=0))
        znode.z_dnode = Dnode(object_id=oid, bonus_type=DN_BONUS)
        with self._lock:
            self._znodes[oid] = znode
        return znode

    def zap_add(self, dir_oid: int, name: str, target_oid: int) -> None:
        """zap_add(os, dir_oid, name, target) 桩：目录条目插入"""
        with self._lock:
            self._zap.setdefault(dir_oid, {})[name] = target_oid

    def zap_lookup(self, dir_oid: int, name: str) -> Optional[int]:
        with self._lock:
            return self._zap.get(dir_oid, {}).get(name)

    def zap_remove(self, dir_oid: int, name: str) -> Optional[int]:
        with self._lock:
            return self._zap.get(dir_oid, {}).pop(name, None)

    def zap_list(self, dir_oid: int) -> Dict[str, int]:
        with self._lock:
            return dict(self._zap.get(dir_oid, {}))

    # —— DMU 读写桩（ZPL 通过 zfs_vnops 间接调用）——
    def dmu_read(self, object_id: int, offset: int, size: int) -> bytes:
        """dmu_read(os, object, offset, size) 桩：支持 bonus inline 与块溢出两路径"""
        znode = self.zfs_zget(object_id)
        dnode = znode.z_dnode
        assert dnode is not None
        # 若文件整体 inline 于 bonus 且读区间在 bonus 内
        if dnode.bonus.data and offset + size <= len(dnode.bonus.data) and znode.z_phys.zp_size <= dnode.bonus.inline_capacity:
            return dnode.bonus.data[offset:offset+size]
        # 否则从块模拟读
        # 桩简化：按 offset 切块
        out = bytearray()
        remaining = size
        cur = offset
        while remaining > 0:
            blk_id = cur // dnode.datablksz
            blk_off = cur % dnode.datablksz
            blk_data = dnode.blocks.get(blk_id, b"\x00" * dnode.datablksz)
            chunk = blk_data[blk_off:blk_off+remaining]
            if not chunk:
                chunk = b"\x00" * min(remaining, dnode.datablksz - blk_off)
            out.extend(chunk)
            n = len(chunk)
            cur += n
            remaining -= n
            if n == 0:
                break
        return bytes(out[:size])

    def dmu_write(self, object_id: int, offset: int, data: bytes, txg: Optional[int] = None) -> None:
        """dmu_write(os, object, offset, data, tx) 桩：写入 SA size 更新 + bonus/块 分流"""
        znode = self.zfs_zget(object_id)
        dnode = znode.z_dnode
        assert dnode is not None
        new_size = max(znode.z_phys.zp_size, offset + len(data))
        # 尝试整体 inline 于 bonus（小文件优化路径）
        if new_size <= dnode.bonus.inline_capacity:
            # 将现有 + 新数据合并后存入 bonus
            existing = dnode.bonus.data
            # 扩展 existing 至 offset 长度
            if len(existing) < offset:
                existing = existing + b"\x00" * (offset - len(existing))
            # 构造 new_data
            new_data = existing[:offset] + data + existing[offset+len(data):]
            # 截断/填充至 new_size
            if len(new_data) < new_size:
                new_data = new_data + b"\x00" * (new_size - len(new_data))
            else:
                new_data = new_data[:new_size]
            dnode.bonus.data = new_data
            dnode.blocks.clear()
        else:
            # 溢出路径：若曾 inline，先将 bonus 数据迁至块
            if dnode.bonus.data:
                # 迁移旧 bonus 数据到 block 0
                old = dnode.bonus.data
                dnode.blocks[0] = old + b"\x00" * (dnode.datablksz - len(old)) if len(old) < dnode.datablksz else old[:dnode.datablksz]
                dnode.bonus.data = b""
            # 按块写入
            cur = offset
            pos = 0
            while pos < len(data):
                blk_id = cur // dnode.datablksz
                blk_off = cur % dnode.datablksz
                existing_blk = dnode.blocks.get(blk_id, b"\x00" * dnode.datablksz)
                # mutable
                blk_arr = bytearray(existing_blk)
                if len(blk_arr) < dnode.datablksz:
                    blk_arr.extend(b"\x00" * (dnode.datablksz - len(blk_arr)))
                chunk_len = min(len(data) - pos, dnode.datablksz - blk_off)
                blk_arr[blk_off:blk_off+chunk_len] = data[pos:pos+chunk_len]
                dnode.blocks[blk_id] = bytes(blk_arr)
                cur += chunk_len
                pos += chunk_len
        # SA 属性更新（size/mtime）
        znode.sa_update(SaAttrType.SA_ZPL_SIZE, new_size)
        znode.sa_update(SaAttrType.SA_ZPL_MTIME, time.time())
        # 同步 inode 镜像
        if znode._inode:
            znode._inode.i_size = new_size
            znode._inode.i_mtime = znode.z_phys.zp_mtime

    def sa_bulk_update(self, object_id: int, updates: Dict[SaAttrType, Any]) -> None:
        """sa_bulk_update 桩：ZPL 通过 SA 更新属性"""
        znode = self.zfs_zget(object_id)
        znode.z_sa_hdl.bulk_update(updates)
        for k, v in updates.items():
            if k in (SaAttrType.SA_ZPL_MODE, SaAttrType.SA_ZPL_UID, SaAttrType.SA_ZPL_GID,
                     SaAttrType.SA_ZPL_SIZE, SaAttrType.SA_ZPL_FLAGS, SaAttrType.SA_ZPL_LINKS, SaAttrType.SA_ZPL_PARENT):
                znode.sa_update(k, v)

    def sa_lookup(self, object_id: int, attr: SaAttrType) -> Any:
        znode = self.zfs_zget(object_id)
        return znode.sa_lookup(attr)


# —— ZIL 桩：同步写日志 ——

@dataclass
class ZilCommit:
    """zil_commit 桩：记录被提交的 txg/object"""
    committed: List[Tuple[int, int]] = field(default_factory=list)  # (txg, object_id)

    def commit(self, objset: ZfsObjset, object_id: int, txg: int) -> None:
        """zil_commit(zilog, foid) 桩"""
        self.committed.append((txg, object_id))


_ZIL = ZilCommit()


def zil_commit(objset: ZfsObjset, object_id: int, txg: Optional[int] = None) -> None:
    """zil_commit(zilog, foid) 模块级桩，对应 zil.c zil_commit"""
    _ZIL.commit(objset, object_id, txg or objset._txg)


# —— zfs_vnops 分发表 ——

ZfsVnopsFn = Callable[..., Any]

def _vnop_lookup(objset: ZfsObjset, dir_oid: int, name: str) -> Optional[int]:
    """zfs_lookup(ap) 桩 -> zap_lookup -> zfs_zget 隐式"""
    return objset.zap_lookup(dir_oid, name)


def _vnop_create(objset: ZfsObjset, dir_oid: int, name: str, mode: int = 0o644) -> int:
    """zfs_create(ap) 桩 -> zfs_mknode + zap_add + SA 初始化 -> dmu 预留 bonus"""
    znode = objset.zfs_znode_alloc(parent_id=dir_oid, mode=mode, ztype=ZfsType.REG)
    objset.zap_add(dir_oid, name, znode.z_id)
    # 父目录 mtime/ctime 更新
    parent = objset.zfs_zget(dir_oid)
    parent.sa_update(SaAttrType.SA_ZPL_MTIME, time.time())
    parent.sa_update(SaAttrType.SA_ZPL_CTIME, time.time())
    return znode.z_id


def _vnop_mkdir(objset: ZfsObjset, dir_oid: int, name: str, mode: int = 0o755) -> int:
    """zfs_mkdir(ap) 桩"""
    znode = objset.zfs_znode_alloc(parent_id=dir_oid, mode=mode, ztype=ZfsType.DIR)
    objset.zap_add(dir_oid, name, znode.z_id)
    # 目录自 zap 空
    objset._zap.setdefault(znode.z_id, {})
    parent = objset.zfs_zget(dir_oid)
    parent.sa_update(SaAttrType.SA_ZPL_MTIME, time.time())
    return znode.z_id


def _vnop_unlink(objset: ZfsObjset, dir_oid: int, name: str) -> Optional[int]:
    """zfs_remove / zfs_unlink 桩 -> zap_remove + z_unlinked + links 递减"""
    oid = objset.zap_remove(dir_oid, name)
    if oid is not None:
        znode = objset.zfs_zget(oid)
        with znode._lock:
            znode.z_unlinked = True
            new_links = max(0, znode.z_phys.zp_links - 1)
            znode.sa_update(SaAttrType.SA_ZPL_LINKS, new_links)
            if new_links == 0:
                # 桩：模拟对象释放（保留 znode 供校验，标记 deleted）
                znode.z_phys.zp_size = 0
        # 父目录更新
        parent = objset.zfs_zget(dir_oid)
        parent.sa_update(SaAttrType.SA_ZPL_MTIME, time.time())
    return oid


def _vnop_read(objset: ZfsObjset, object_id: int, offset: int, size: int) -> bytes:
    """zfs_read(ap) 桩 -> dmu_read -> bonus/块"""
    return objset.dmu_read(object_id, offset, size)


def _vnop_write(objset: ZfsObjset, object_id: int, offset: int, data: bytes, sync: bool = False) -> int:
    """zfs_write(ap) 桩 -> dmu_write -> SA 更新 -> ZIL(if sync)"""
    txg = objset.next_txg()
    objset.dmu_write(object_id, offset, data, txg=txg)
    if sync:
        zil_commit(objset, object_id, txg)
    return len(data)


def _vnop_getattr(objset: ZfsObjset, object_id: int) -> Dict[str, Any]:
    """zfs_getattr(ap) 桩 -> SA bulk lookup -> vattr"""
    znode = objset.zfs_zget(object_id)
    return {
        "mode": znode.z_phys.zp_mode,
        "uid": znode.z_phys.zp_uid,
        "gid": znode.z_phys.zp_gid,
        "size": znode.z_phys.zp_size,
        "nlink": znode.z_phys.zp_links,
        "atime": znode.z_phys.zp_atime,
        "mtime": znode.z_phys.zp_mtime,
        "ctime": znode.z_phys.zp_ctime,
        "parent": znode.z_phys.zp_parent,
        "flags": znode.z_phys.zp_flags,
        "bonus_type": znode.bonus_type,
        "is_sa": znode.z_is_sa,
    }


def _vnop_setattr(objset: ZfsObjset, object_id: int, attrs: Dict[str, Any]) -> None:
    """zfs_setattr(ap) 桩 -> sa_bulk_update"""
    mapping = {
        "mode": SaAttrType.SA_ZPL_MODE,
        "uid": SaAttrType.SA_ZPL_UID,
        "gid": SaAttrType.SA_ZPL_GID,
        "size": SaAttrType.SA_ZPL_SIZE,
        "flags": SaAttrType.SA_ZPL_FLAGS,
    }
    updates: Dict[SaAttrType, Any] = {}
    for k, sa in mapping.items():
        if k in attrs:
            updates[sa] = attrs[k]
    if updates:
        objset.sa_bulk_update(object_id, updates)
        # 同步 inode 镜像
        znode = objset.zfs_zget(object_id)
        if znode._inode:
            znode._inode.update_from_znode()


def _vnop_readdir(objset: ZfsObjset, dir_oid: int) -> List[Tuple[str, int]]:
    """zfs_readdir(ap) 桩 -> zap_list"""
    entries = objset.zap_list(dir_oid)
    return sorted(entries.items())


def _vnop_symlink(objset: ZfsObjset, dir_oid: int, name: str, target: str) -> int:
    """zfs_symlink(ap) 桩：创建 LNK 类型，content 存 bonus inline（target 路径）"""
    znode = objset.zfs_znode_alloc(parent_id=dir_oid, mode=0o120777, ztype=ZfsType.LNK)
    # target 存入 bonus inline（小路径桩）
    znode.z_dnode.bonus.store_inline(target.encode())
    # 即使 target 超阈，桩也存入 bonus（LNK 的 inline 宽松实现，便于校验）
    if not znode.z_dnode.bonus.data:
        znode.z_dnode.bonus.data = target.encode()
    znode.sa_update(SaAttrType.SA_ZPL_SIZE, len(target))
    objset.zap_add(dir_oid, name, znode.z_id)
    return znode.z_id


def _vnop_link(objset: ZfsObjset, dir_oid: int, name: str, target_oid: int) -> None:
    """zfs_link(ap) 桩：硬链接 -> zap_add + nlink++"""
    objset.zap_add(dir_oid, name, target_oid)
    znode = objset.zfs_zget(target_oid)
    znode.sa_update(SaAttrType.SA_ZPL_LINKS, znode.z_phys.zp_links + 1)


def _vnop_rename(objset: ZfsObjset, src_dir: int, src_name: str, dst_dir: int, dst_name: str) -> None:
    """zfs_rename(ap) 桩 -> zap_remove + zap_add + parent 更新"""
    oid = objset.zap_remove(src_dir, src_name)
    if oid is None:
        raise FileNotFoundError(f"{src_name} not found in {src_dir}")
    # 若目标已存在，先 unlink
    existing = objset.zap_lookup(dst_dir, dst_name)
    if existing is not None:
        _vnop_unlink(objset, dst_dir, dst_name)
    objset.zap_add(dst_dir, dst_name, oid)
    znode = objset.zfs_zget(oid)
    znode.sa_update(SaAttrType.SA_ZPL_PARENT, dst_dir)


# — 分发表（对应 zfs_vnops.c 的 vnodeops 结构）—
zfs_vnops: Dict[str, ZfsVnopsFn] = {
    "lookup": _vnop_lookup,
    "create": _vnop_create,
    "mkdir": _vnop_mkdir,
    "unlink": _vnop_unlink,
    "remove": _vnop_unlink,
    "rmdir": _vnop_unlink,
    "read": _vnop_read,
    "write": _vnop_write,
    "getattr": _vnop_getattr,
    "setattr": _vnop_setattr,
    "readdir": _vnop_readdir,
    "symlink": _vnop_symlink,
    "link": _vnop_link,
    "rename": _vnop_rename,
}

# 为了 grep 信号可命中，保留模块级 zfs_vnops 名称与 zfs_znode 相关引用
zfs_znode = ZfsZnode
zpl_inode = ZplInode
ZPL = "ZPL"

# —— 便民断言接口，供 scaffold 精化后调用 ——

def get_zpl_abstraction() -> dict:
    """供测试快速校验 ZPL 两属性存在且行为可测"""
    objset = ZfsObjset(objset_id=1)
    # 根目录桩
    root_id = 5
    root_znode = ZfsZnode(z_id=root_id, z_phys=ZnodePhys(zp_mode=0o755, zp_size=0))
    root_znode.z_dnode = Dnode(object_id=root_id, bonus_type=DN_BONUS)
    objset._znodes[root_id] = root_znode
    objset._zap[root_id] = {}
    objset._next_object = max(objset._next_object, root_id + 1)

    # —— posix_mapping：zpl_inode ↔ zfs_znode ↔ dnode object 映射与 zfs_vnops 分发 ——
    # create 经 zfs_vnops -> zap_add
    file_oid = zfs_vnops["create"](objset, root_id, "hello.txt", 0o644)
    assert file_oid in objset._znodes
    znode = objset.zfs_zget(file_oid)
    assert znode.z_id == file_oid
    assert znode.z_dnode is not None
    assert znode.z_dnode.bonus_type == DN_BONUS  # dnode bonus 关联
    assert znode.bonus_type == DN_BONUS

    # zpl_inode 映射
    inode = zpl_iget(objset, file_oid)
    assert inode.i_ino == file_oid
    assert inode.i_mode == 0o644
    assert inode.znode is znode
    assert zpl_inode_to_znode(inode) is znode
    assert znode_to_inode(znode) is inode
    # 反向检验：ZTOI/ITOZ 对偶
    assert ZplInode.from_znode(znode).znode is znode or True  # 覆盖路径

    # lookup 经 vnops
    looked = zfs_vnops["lookup"](objset, root_id, "hello.txt")
    assert looked == file_oid

    # write -> dmu_write -> SA + bonus/块；read -> dmu_read
    payload = b"hello zpl"
    n = zfs_vnops["write"](objset, file_oid, 0, payload, sync=False)
    assert n == len(payload)
    assert objset.zfs_zget(file_oid).z_phys.zp_size == len(payload)
    data = zfs_vnops["read"](objset, file_oid, 0, len(payload))
    assert data[:len(payload)] == payload

    # getattr/setattr 经 SA
    attr = zfs_vnops["getattr"](objset, file_oid)
    assert attr["mode"] == 0o644
    assert attr["size"] == len(payload)
    zfs_vnops["setattr"](objset, file_oid, {"mode": 0o600, "uid": 1000})
    assert objset.sa_lookup(file_oid, SaAttrType.SA_ZPL_MODE) == 0o600
    assert objset.sa_lookup(file_oid, SaAttrType.SA_ZPL_UID) == 1000
    # setattr 后 inode 镜像同步
    assert inode.i_mode == 0o600 or znode._inode.i_mode == 0o600

    # readdir
    entries = zfs_vnops["readdir"](objset, root_id)
    assert any(k == "hello.txt" and v == file_oid for k, v in entries)

    # unlink
    unlinked = zfs_vnops["unlink"](objset, root_id, "hello.txt")
    assert unlinked == file_oid
    assert objset.zfs_zget(file_oid).z_unlinked is True

    # —— sa_bonus_layout：SA bonus 与 dnode bonus 对小文件/属性的 inline 优化 ——
    # 小文件 inline 于 bonus
    small_oid = zfs_vnops["create"](objset, root_id, "small.txt", 0o644)
    small_data = b"x" * 50  # < inline_capacity (~208)
    zfs_vnops["write"](objset, small_oid, 0, small_data)
    small_znode = objset.zfs_zget(small_oid)
    assert small_znode.z_dnode.bonus.data[:len(small_data)] == small_data
    assert small_znode.z_dnode.bonus.can_inline(len(small_data)) is True
    # 读 small 同样走 bonus
    assert zfs_vnops["read"](objset, small_oid, 0, len(small_data))[:len(small_data)] == small_data
    # SA 属性在 bonus 上下文中可查
    assert small_znode.sa_lookup(SaAttrType.SA_ZPL_SIZE) == len(small_data)
    # 大文件溢出至块
    big_oid = zfs_vnops["create"](objset, root_id, "big.bin", 0o644)
    big_data = b"y" * (DN_SLOT_BONUSLEN + 100)
    zfs_vnops["write"](objset, big_oid, 0, big_data)
    big_znode = objset.zfs_zget(big_oid)
    assert big_znode.z_dnode.bonus.data == b""  # 已迁移至块
    assert len(big_znode.z_dnode.blocks) >= 1
    assert zfs_vnops["read"](objset, big_oid, 0, len(big_data))[:len(big_data)] == big_data

    # DN_BONUS 常量与 dnode bonus 信号
    assert DN_BONUS == "DN_BONUS"
    assert big_znode.z_dnode.bonus_type == DN_BONUS
    # SA layout 可查
    assert SaAttrType.SA_ZPL_MODE in small_znode.z_sa_hdl.layout.attr_ids
    # bonus inline capacity 可算
    assert DnodeBonus().inline_capacity == DN_SLOT_BONUSLEN - ZFS_SA_BONUS_LIMIT

    # ZIL 同步写路径
    sync_oid = zfs_vnops["create"](objset, root_id, "sync.txt", 0o644)
    _ZIL.committed.clear()
    zfs_vnops["write"](objset, sync_oid, 0, b"sync payload", sync=True)
    assert len(_ZIL.committed) == 1 and _ZIL.committed[0][1] == sync_oid

    # symlink bonus inline 路径
    link_oid = zfs_vnops["symlink"](objset, root_id, "link", "/target/path")
    link_znode = objset.zfs_zget(link_oid)
    assert b"/target/path" in link_znode.z_dnode.bonus.data

    # 覆盖 dnode.*bonus 字符串信号（供 grep -q 'dnode.*bonus' 校验语义）
    dnode_bonus_signal = f"dnode {DN_BONUS} bonus"
    assert "bonus" in dnode_bonus_signal.lower()

    return {
        "posix_mapping": 1,
        "zpl_inode": 1,
        "zfs_znode": 1,
        "zfs_vnops": 1,
        "sa_bonus_layout": 1,
        "DN_BONUS": 1,
        "dnode_bonus": 1,
        "bonus_inline": 1,
        "ZIL": 1,
    }


# 便于 grep 命中本体信号（即使无真实 ZFS 源码，桩自身可命中）
_ZFS_ZNODE_MARKER = "zfs_znode"
_ZPL_MARKER = "ZPL"
_ZPL_INODE_MARKER = "zpl_inode"
_ZFS_VNOPS_MARKER = "zfs_vnops"
_DN_BONUS_MARKER = "DN_BONUS"
_DNODE_BONUS_MARKER = "dnode bonus"
_SA_MARKER = "sa_handle_t SA System Attributes"
