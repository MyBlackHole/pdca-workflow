---
schema: pdca.asset/v2
id: ontology:domain/core-journal-lifecycle-flush
type: domain
layer: Knowledge
status: active
summary: journal开关机状态机 + 按序刷 + 免刷区 + 重写区间
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
  desc: 日志开关机、按序刷盘、免刷区、重写区间场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/journal/journal.c 在仓库中存在且含 bch2_journal_flush_seq 定义
  evidence_level: unclassified
- name: constraints
  desc: 生命周期前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认循环开关、单调刷盘、特性门控三条前提在引用代码中有对应实现
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

# journal 生命周期与刷盘

沉淀自 T0500（内核第十二轮）。对照 bcachefs
`fs/journal/journal.c`。

## 核心概念

1. **开关机状态机**：循环关开条目，强制开关与刷等待判定，避
   免旧递归（`bch2_journal_cycle_locked`）；停机置错唤醒防驻留
   （`bch2_journal_halt_locked`）；静默等落盘否则先关
   （`bch2_journal_quiesce`）。
2. **按序刷与单调**：三剪枝加单调刷盘号，在途重定；错态回错防
   永等（`bch2_journal_flush_seq_async`）；超时打印
   （`bch2_journal_flush_seq`）。
3. **免刷区与重写区间**：免刷需特性门控；重写区间记覆盖；空
   预留强制落盘推进（`bch2_journal_noflush_seq`、
   `bch2_journal_add_rewind_range`、`bch2_journal_meta`）。
4. **与既有节点边界**：黑名单节点管 seq 过滤，水位机管触发，
   本节点管开关机与刷盘语义。

## 复用指南

- 日志开关机必须是显式状态机，禁止递归开关。
- 刷盘号必须单调，错态必须回错防永等。
