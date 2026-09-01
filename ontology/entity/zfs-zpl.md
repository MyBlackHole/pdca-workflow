---
schema: pdca.asset/v1
id: ontology:entity/zfs-zpl
type: entity
layer: Knowledge
status: active
summary: ZFS ZPL 实体 — POSIX 层 zfs_znode/zpl_inode 与 DMU 对象映射
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: posix_mapping
    desc: POSIX 语义到 DMU 对象的映射可测
    constraint: 覆盖 zpl_inode ↔ zfs_znode ↔ dnode 的 object 上下映射与 zfs_vnops 分发
    testable_signal: "运行 grep -q 'ZPL' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'zfs_znode' module/zfs/zfs_znode.c 命中"
  - name: sa_bonus_layout
    desc: SA 与 bonus 缓冲布局可测
    constraint: 覆盖 SA (System Attributes) 与 dnode bonus 对小文件/属性的存储优化
    testable_signal: "运行 grep -q 'dnode.*bonus' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'DN_BONUS' include/sys/dnode.h 命中"
---

# ZFS ZPL（POSIX Layer）

POSIX 层：`zpl_inode`/`zfs_znode` 为 VFS inode 与 ZFS 对象的桥梁，`zfs_vnops` 分发 `read/write/create/unlink` 至 DMU（`dmu_read/write`/`zap`）；`SA` 与 `bonus` 缓冲对小文件/扩展属性做 inline 存储；`ZIL` 介入同步写（`zil_commit`）。

Source: `openzfs/zfs/module/zfs/zfs_vnops.c`（vnops 分发）+ `openzfs/zfs/module/zpl/zpl_inode.c`（inode 映射）+ `https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Datasets/`
