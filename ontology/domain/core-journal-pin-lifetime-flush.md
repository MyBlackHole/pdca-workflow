---
schema: pdca.asset/v2
id: ontology:domain/core-journal-pin-lifetime-flush
type: domain
layer: Knowledge
status: active
summary: journal Pin存活期钉住与分类型有序回刷
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
  desc: 脏元数据引用保持、阻止日志推进过早、分类型回刷场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/journal/reclaim.c 在仓库中存在且含 bch2_journal_pin_set 定义
  evidence_level: unclassified
- name: constraints
  desc: 钉住回刷前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认引用保持、分类回刷、保活复制三条前提在引用代码中有对应实现
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

# journal Pin存活期钉住

沉淀自 T0497（内核第九轮，二轮复核）。对照 bcachefs
`fs/journal/reclaim.c`。

## 核心概念

1. **引用保持阻止推进**：脏元数据对 seq 的引用保持阻止
   last_seq 推进，与容量记账正交（`bch2_journal_pin_set`）。
2. **分类型有序回刷**：keep-oldest 复制保活，按 btree/key_cache/
   other 分类 flush（`bch2_journal_pin_copy`、
   `journal_flush_pins`）。
3. **与既有节点边界**：黑名单节点管 seq 过滤，记账节点管容量，
   本节点管引用生命周期。

## 复用指南

- 脏数据对日志的引用必须显式 pin，禁止靠容量水位间接保证。
- 回刷必须按类型有序，key_cache 等快消类型优先。
