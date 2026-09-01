---
schema: pdca.asset/v1
id: ontology:entity/zfs-spa
type: entity
layer: Knowledge
status: active
summary: ZFS SPA 实体 — Storage Pool Allocator 与 TXG 状态机及 metaslab 分配
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: txg_state_machine
    desc: TXG 三状态机 open/quiescing/syncing 可验证
    constraint: 覆盖 txg_init/txg_hold_open/txg_quiesce/txg_sync_thread/quiesce_thread 与 zfs_txg_timeout
    testable_signal: "运行 grep -q 'txg_quiesce' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'tx_open_txg' module/zfs/txg.c 命中"
  - name: spa_sync_convergence
    desc: spa_sync 多 pass 收敛与 metaslab 调度
    constraint: 覆盖 zfs_sync_pass_deferred_free/dont_compress/rewrite 三收敛开关与 spa_taskq_dispatch
    testable_signal: "运行 grep -q 'spa_sync' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'zfs_sync_pass_deferred_free' module/zfs/zio.c 命中"
---

# ZFS SPA（Storage Pool Allocator）

池分配器：`spa_t` 持有 `uberblock`/`MOS`/`vdev 树`/`metaslab class`；`TXG` 三状态 `open→quiescing→syncing` 由 `txg_quiesce_thread`/`txg_sync_thread` 驱动，`zfs_txg_timeout=5s` 保活；`spa_sync` 迭代写出脏数据，`zfs_sync_pass_*` 逐 pass 禁压缩/推迟 free 以收敛；`spa_taskq_dispatch` 按 `zio_taskqs` 四类任务队列分发至 VDEV。

Source: `openzfs/zfs/module/zfs/spa.c:20-60`（SPA 注释）+ `openzfs/zfs/module/zfs/txg.c:20-80`（TXG 头注释）+ `openzfs/zfs/module/zfs/txg.c:310,480`
