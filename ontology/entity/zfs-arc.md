---
schema: pdca.asset/v1
id: ontology:entity/zfs-arc
type: entity
layer: Knowledge
status: active
summary: ZFS ARC 实体 — Adaptive Replacement Cache 自适应缓存与 L2ARC/dbuf 协作
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: arc_adaptive
    desc: ARC 自适应 MRU/MFU/ghost 命中可测
    constraint: 覆盖 ARC_p 自适应、ghost 命中与 hash 锁分层 buf_hash_find
    testable_signal: "运行 grep -q 'ARC.*MRU.*MFU' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'buf_hash_find' module/zfs/arc.c 命中"
  - name: l2arc_persistence
    desc: L2ARC 持久化与压缩 ARC 可测
    constraint: 覆盖 zfs_compressed_arc_enabled 对 b_pabd 的影响与 l2arc_write_max 头室
    testable_signal: "运行 grep -q 'L2ARC' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'l2arc_write_max' module/zfs/arc.c 命中"
---

# ZFS ARC（Adaptive Replacement Cache）

自适应缓存：L1 分 `MRU/MFU` 与 `ghost` 四态，`ARC_p` 自适应调参；`buf_hash_table`（2048 锁）+ `ARC 链表锁`分层，`buf_hash_find` 返回持锁头；`zfs_compressed_arc_enabled` 控制 `b_pabd` 是否存压缩物理块，L2ARC 写入即 `b_pabd`；`l2arc_write_max`/`headroom` 控制持久化速率与 `zfetch` 预取协同 `dbuf_read`。

Source: `openzfs/zfs/module/zfs/arc.c:1-120`（ARC operation 头注释）+ `openzfs/zfs/module/zfs/arc.c:800`（buf_hash_find）+ `FAST'03 ARC: A Self-Tuning, Low Overhead Replacement Cache`
