---
schema: pdca.asset/v2
id: ontology:domain/core-journal-entry-selfheal-validate
type: domain
layer: Knowledge
status: active
summary: journal条目边校验边删坏键自愈
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
  desc: 日志条目内逐键校验、坏键删除自愈场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/journal/validate.c 在仓库中存在且含 journal_validate_key 定义
  evidence_level: unclassified
- name: constraints
  desc: 自愈校验前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认边验边删、范围置空两条前提在引用代码中有对应实现
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

# journal 条目边验边删自愈

沉淀自 T0501（内核第十三轮）。对照 bcachefs
`fs/journal/validate.c`。

## 核心概念

1. **逐键边验边删**：条目内逐键校验，坏键就地置空移删，返回
   已删标记（`journal_validate_key`、
   `journal_entry_null_range`）。
2. **与既有节点边界**：黑名单节点管 seq 过滤，组装节点管写入，
   本节点管条目内自愈。

## 复用指南

- 容器内校验必须边验边删，禁止整容器丢弃。
- 删坏键必须置空移删并标记，禁止静默跳过。
