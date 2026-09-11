---
schema: pdca.asset/v2
id: ontology:domain/core-bcachefs-study-map
type: domain
layer: Knowledge
status: active
summary: bcachefs学习总导航与设计哲学
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-sixlock-study-guide
  - ontology:domain/core-journal-study-guide
  - ontology:domain/core-ec-study-guide
  - ontology:domain/core-alloc-study-guide
  - ontology:domain/core-btreetrans-study-guide
  - ontology:domain/core-snapshot-study-guide
  - ontology:domain/core-userspace-study-guide
  - ontology:domain/core-crypto-study-guide
  - ontology:domain/core-observability-study-guide
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: bcachefs 全体系学习入口、专题导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 9 个指南节点 id 全部存在
  evidence_level: unclassified
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: 通读正文学习路径节，确认九专题顺序与每阶段指南映射在正文中明确
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

# bcachefs 学习总导航

沉淀自 T0523（收官总报告），来源 `records/T0523-0906-study-finale/`。
聚合 9 个专题指南节点与七条设计哲学。

## 背景

九专题报告与指南节点已备，但缺总入口与跨专题共性。本节点收官。

## 学习路径（九专题顺序）

锁→journal→EC→分配器→事务→快照→用户态→压缩→可观测。
先并发原语，再存储中枢，再数据面，最后运维面。

1. **锁**：`ontology:domain/core-sixlock-study-guide`（T0512）
2. **journal**：`ontology:domain/core-journal-study-guide`（T0515）
3. **EC**：`ontology:domain/core-ec-study-guide`（T0516）
4. **分配器**：`ontology:domain/core-alloc-study-guide`（T0517）
5. **事务**：`ontology:domain/core-btreetrans-study-guide`（T0518）
6. **快照**：`ontology:domain/core-snapshot-study-guide`（T0519）
7. **用户态**：`ontology:domain/core-userspace-study-guide`（T0520）
8. **压缩**：`ontology:domain/core-crypto-study-guide`（T0521）
9. **可观测**：`ontology:domain/core-observability-study-guide`（T0522）

## 七条设计哲学速查

显式优于隐式、分段语义、引用显式持有、错误不掩盖、可观测前置、
版本隔离演进、文档即代码。详见总报告第二节。

## 复用指南

- 新人按顺序通读九报告，再按需深入单专题。
- 设计新系统先背七条哲学，再看具体机制。
