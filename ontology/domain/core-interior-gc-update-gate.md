---
schema: pdca.asset/v2
id: ontology:domain/core-interior-gc-update-gate
type: domain
layer: Knowledge
status: active
summary: interior更新双路径门控 + 最高水位特权 + GC读写互斥
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-btree-transaction-memory-io
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: btree内部节点指针更新、GC与分裂并发、异步落盘场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/btree/interior.c 在仓库中存在且含 bch2_btree_node_update_key 定义
  evidence_level: unclassified
- name: constraints
  desc: 更新门控前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认意图锁持有、水位放行、读写互斥三条前提在引用代码中有对应实现
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

# interior更新门控 + GC 读写互斥

沉淀自 T0492（内核第四轮）。对照 bcachefs
`fs/btree/interior.c`、`fs/btree/interior.h`、
`fs/btree/interior_types.h`、`fs/btree/check_types.h`、
`fs/alloc/types.h`。

## 核心概念

1. **update_key 双路径按可达门控**：非可达走父迭代器遍历更新；
   已可达持 commit_lock 复检防嵌套重启，同时改新旧两处 key；
   外层先升级层级并加 intent 防降级
   （`__bch2_btree_node_update_key`）。
2. **interior_updates 最高水位特权**：水位列末最高保留；该水位
   提交天然被 journal 放行；重写分支遇该水位跳过合并防自死锁；
   hipri 提升 copygc/btree 下限（`BCH_WATERMARKS`、
   `btree_update_nodes_written`）。
3. **GC 读写锁互斥**：更新持 GC 读锁至 done/free；插入断言持读
   锁；GC 整树阶段持写锁排斥分裂/重写
   （`bch2_btree_update_start`、`bch2_btree_insert_node`）。
4. **异步两阶段 + 阻塞闸**：双链表 + 锁 + worker + 内存池管理；
   新节点置可达闸后先写子节点；回调置位后排队由 worker 做
   journal + 触发器提交；flush 侧等链表清空
   （`btree_interior_update_work`、
   `bch2_btree_interior_updates_flush`）。

## 复用指南

- 内部指针更新必须按可达性分路径，不可达走遍历、可达走复检。
- 最高水位留给元数据自更新，journal 必须天然放行该水位。
- GC 与更新用读写锁互斥，更新路径断言持锁，禁止无锁改指针。
