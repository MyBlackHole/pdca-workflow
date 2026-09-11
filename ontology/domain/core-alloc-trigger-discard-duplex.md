---
schema: pdca.asset/v2
id: ontology:domain/core-alloc-trigger-discard-duplex
type: domain
layer: Knowledge
status: active
summary: alloc触发器两阶段分流 + discard后台双工
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 分配状态机索引维护、后台TRIM快慢双工场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/alloc/background.c 在仓库中存在且含 bch2_trigger_alloc 定义
  evidence_level: unclassified
- name: constraints
  desc: 触发分流前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认状态机分流、序号未知延迟、三门跳过三条前提在引用代码中有对应实现
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

# alloc触发器分流与discard双工

沉淀自 T0496（内核第八轮，全扫复核）。对照 bcachefs
`fs/alloc/background.c`、`fs/alloc/discard.c`。

## 核心概念

1. **触发器两阶段分流**：事务段非空走翻转，空走直接改；空闲
   位图直接改位，丢弃索引因序号未知走写缓冲延迟定址
   （`bch2_trigger_alloc`、`bch2_bucket_do_freespace_index`、
   `bch2_bucket_do_discard_index`）。
2. **discard 后台双工**：按日志三水位门跳过；快慢双工，快路
   数组加写引用队列（`bch2_discard_one_bucket`、
   `bch2_do_discards_fast_work`）。
3. **与既有节点边界**：WFQ 节点管前台调度，记账节点管用量，
   本节点管状态机索引维护与后台 TRIM。

## 复用指南

- 状态未知时索引维护必须延迟定址，禁止原子段内猜位置。
- 后台清运必须快慢双工，快路旁路队列而非抢慢路锁。
