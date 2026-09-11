---
schema: pdca.asset/v2
id: ontology:domain/core-snapshot-delete-execution
type: domain
layer: Knowledge
status: active
summary: 快照删除 v2 索引 + dying 下迁 + 先迁后验落盘序
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-snapshot-table-lifecycle-filter-semantics
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 快照子树批量删除、 dying 键迁移、子卷删除收尾场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/snapshots/delete.c 在仓库中存在且含 delete_dead_snapshot_keys_v2 定义
  evidence_level: unclassified
- name: constraints
  desc: 删除执行前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认索引完备性、下迁合并、落盘顺序三条前提在引用代码中有对应实现
  evidence_level: unclassified
revision: 3.1.0
authority: reference
dcterms_modified: '2026-09-12'
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 快照删除 v2 索引 + 先迁后验

沉淀自 T0492（内核第四轮）。对照 bcachefs
`fs/snapshots/delete.c`、`fs/snapshots/subvolume.c`、
`fs/snapshots/check_snapshots.c`。

## 核心概念

1. **v2 以 inode 为索引范围删**：有内容必有同快照 inode，先扫
   inodes 按 inum 范围删 extents/dirents/xattrs/damage，再扫
   inodes 自身；残留回退 v1 全表扫，仍残留拉 check_allocations
   （`delete_dead_snapshot_keys_v2`）。
2. **dying 键下迁与 damage 合并**：有活孩子时搬键到活槽，
   damage 双存则归并折叠；无活孩子叶直接删
   （`bch2_delete_dead_snapshot_key`）。
3. **Eytzinger dying 判定**：对删除列表二分查，叶与冗余终点
   分流，收集时已链式归一、单跳迁移到位
   （`snapshot_id_dying`）。
4. **先迁后验落盘序**：迁移 → 熔断校验（拒删停全删）→ 逐叶提
   交 → 置 no_keys；墓碑按版本置 deleted/删键，不碰派生记账
   （`delete_dead_snapshots_locked`）。
5. **子卷删除收尾三步**：子孙改挂父 → 清 master + 置 deleted
   同事务 → unlink 挂 hook + 驱逐页缓存后异步正式删
   （`bch2_subvolumes_reparent`、`__bch2_subvolume_set_deleted`）。
6. **逆序全量校验**：自 POS_MAX 逆扫使父 depth 先正；按状态
   恢复 → accounting 复活 → 边互指 → 树/depth/skip → 子卷回指
   顺序修（`bch2_check_snapshots_trans`）。

## 复用指南

- 批量删除必须有索引快路 + 全表回退两档，禁止只有全表扫。
- 迁移与校验必须分阶段落盘，熔断校验失败停全删而非跳过。
- 删除收尾（改挂/墓碑/页缓存）必须同事务或有序，禁止半截。
