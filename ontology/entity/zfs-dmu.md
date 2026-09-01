---
schema: pdca.asset/v1
id: ontology:entity/zfs-dmu
type: entity
layer: Knowledge
status: active
summary: ZFS DMU 实体 — dnode/dbuf 对象-块两级抽象与读写/脏数据路径
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: dnode_dbuf_abstraction
    desc: dnode/dbuf 两级抽象与 dn_struct_rwlock/db_mtx 协同
    constraint: 覆盖 dnode_hold → dbuf_whichblock → dbuf_hold → dbuf_read 状态机 DB_CACHED/DB_FILL
    testable_signal: "运行 grep -q 'dmu_buf_hold_array_by_dnode' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'dnode_hold' module/zfs/dmu.c 命中"
  - name: dirty_throttle_signal
    desc: 脏数据记账与 TXG 反压可测
    constraint: dsl_pool_dirty_space 累加 dp_dirty_pertxg 并在 zfs_dirty_data_sync_percent 触发 txg_kick
    testable_signal: "运行 grep -q 'dsl_pool_dirty_space' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'zfs_dirty_data_sync_percent' module/zfs/dsl_pool.c 命中"
---

# ZFS DMU（Data Management Unit）

对象-事务层：`dnode_t` 为对象头（含 `dn_struct_rwlock`、`dn_dbufs`、`dn_datablksz`），`dbuf_t` 为块缓冲（含 `db_mtx`、`db_state` `DB_CACHED/DB_FILL/DB_READ`），`objset_t` 为对象集。读路径 `dmu_buf_hold_array_by_dnode → dbuf_read → ARC → ZIO` 并行；写路径 `dmu_buf_will_dirty/will_fill → dsl_pool_dirty_space → txg_kick` 进入 TXG。

Source: `openzfs/zfs/module/zfs/dmu.c:740`（`dmu_buf_hold_array_by_dnode` 并行读）+ `openzfs/zfs/module/zfs/dmu.c:1180`（`dmu_read_impl`）+ `openzfs/zfs/module/zfs/dsl_pool.c:20-60`（Write Throttle）
