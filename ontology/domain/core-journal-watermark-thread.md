---
schema: pdca.asset/v2
id: ontology:domain/core-journal-watermark-thread
type: domain
layer: Knowledge
status: active
summary: journal水位四条件 + 双指针推进 + 节拍刷盘线程
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 日志水位触发回收、脏指针推进、后台节拍刷盘场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/journal/reclaim.c 在仓库中存在且含 bch2_journal_set_watermark 定义
  evidence_level: unclassified
- name: constraints
  desc: 水位推进前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认四条件或语义、指针前移、节拍唤醒三条前提在引用代码中有对应实现
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

# journal 水位机线程

沉淀自 T0500（内核第十二轮）。对照 bcachefs
`fs/journal/reclaim.c`。

## 核心概念

1. **水位四条件**：空间/pin/写缓冲/开桶任一紧张即回收水位，
   否则条带水位；中位空间置位踢线程
   （`bch2_journal_set_watermark`）。
2. **双指针推进**：持锁按落盘序号前移脏指针，再触发丢弃判定
   排队异步丢弃（`bch2_journal_space_available`）。
3. **节拍刷盘线程**：取各盘半桶与半钉中较大者为目标；持锁免
   换页内存；超时/中位/脏超标定最小量后循环刷；按节拍睡，
   踢醒或空队唤醒（`__bch2_journal_reclaim`、
   `bch2_journal_reclaim_thread`）。
4. **与既有节点边界**：记账节点管容量公式，钉住节点管引用，
   本节点管水位触发与线程节拍。

## 复用指南

- 水位必须是多条件或语义，禁止单指标。
- 后台线程用节拍睡 + 踢醒，禁止忙轮询。
