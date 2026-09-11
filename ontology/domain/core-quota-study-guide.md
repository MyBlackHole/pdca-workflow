---
schema: pdca.asset/v2
id: ontology:domain/core-quota-study-guide
type: domain
layer: Knowledge
status: active
summary: 配额记账专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-quota-charge-enforce
  - ontology:domain/core-accounting-delta-reconcile
  - ontology:domain/core-vfs-folio-reservation-writeback
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 配额记账机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 3 个记账节点 id 全部存在
  evidence_level: unclassified
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: 通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确
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

# 配额记账专题学习指南

沉淀自 T0531（配额记账专题学习报告），来源
`records/T0531-0906-study-quota/`。对照 bcachefs
`fs/fs/quota.c`、`fs/alloc/accounting.c`。

## 背景

记账知识分散在 3 个本体节点与两处源码中（配额实际在 `fs/fs/`），
初学者无入口。本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **收费强制**：先读 T0531 报告二至五节，再读
   `core-quota-charge-enforce`（预留联动三档强制），对照 quota.c。
2. **记账归并**：`core-accounting-delta-reconcile`（双轨归并自愈），
   对照 accounting.c。
3. **预留贯通**：`core-vfs-folio-reservation-writeback`（页预留），
   理解 VFS 到配额的预留链。

## 八条启示速查

见 T0531 学习报告第八节：分离联动、分档收费、宽限硬限、检查后累、
迁移回滚、只读重建、双轨归并，外加预留贯通。

## 复用指南

- 学记账先分收费记账两域，再看预留桥，最后看归并。
- 配额位置反直觉（fs/fs 非 fs/quota），导航注明防误找。

详见 T0537 代码级精讲扩充版报告（逐函数签名参数返回调用链）。
