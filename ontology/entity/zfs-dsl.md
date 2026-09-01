---
schema: pdca.asset/v1
id: ontology:entity/zfs-dsl
type: entity
layer: Knowledge
status: active
summary: ZFS DSL 实体 — dsl_pool/dsl_dataset/dsl_dir 数据集层与快照克隆语义
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: dataset_lifecycle
    desc: 数据集/快照/克隆生命周期与 deadlist 衔接
    constraint: 覆盖 dsl_dataset_block_born/block_kill 的 referenced/unique 计数与 parent_delta 上卷
    testable_signal: "运行 grep -q 'dsl_dataset_block_born' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'dsl_dataset_phys' module/zfs/dsl_dataset.c 命中"
  - name: pool_sync_coverage
    desc: DSL Pool Sync 多 pass 覆盖
    constraint: dsl_pool_sync 首 pass 写用户数据、后续 pass 只写元数据，与 spa_sync 协同
    testable_signal: "运行 grep -q 'dsl_pool_sync' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'dp_dirty_datasets' module/zfs/dsl_pool.c 命中"
---

# ZFS DSL（Dataset Layer）

数据集层：`dsl_pool_t` 聚合 `dp_dirty_datasets/dp_dirty_dirs/dp_sync_tasks` 三 TXG 链表；`dsl_dataset_t` 维护 `ds_prev_snap_obj/txg`、`ds_deadlist`、`ds_next_clones`；`dsl_dir_t` 管理 `dd_head_dataset` 与 `zap` 属性。`dsl_pool_sync` 由 `spa_sync` 驱动，首 pass 写脏块、后 pass 处理 `sync_tasks` 与 MOS。

Source: `openzfs/zfs/module/zfs/dsl_pool.c:430`（`dsl_pool_sync`）+ `openzfs/zfs/module/zfs/dsl_dataset.c:40-180`（block_born/block_kill）
