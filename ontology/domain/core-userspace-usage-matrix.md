---
schema: pdca.asset/v2
id: ontology:domain/core-userspace-usage-matrix
type: domain
layer: Knowledge
status: active
summary: 用量冗余矩阵 + degraded折算 + EC分组
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 文件系统用量展示、降级折算、纠删配置分组场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 src/commands/fs_usage.rs 在仓库中存在且含 durability_matrix_add 定义
  evidence_level: unclassified
- name: constraints
  desc: 矩阵展示前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认动态扩维、缺盘折算、缓存分流三条前提在引用代码中有对应实现
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

# 用量冗余矩阵展示

沉淀自 T0503（20 轮第 2 轮）。对照 bcachefs
`src/commands/fs_usage.rs`。

## 核心概念

1. **冗余矩阵**：按耐久与降级二维累加扇区，动态扩维，打表头
   加行，非零才转单位（`durability_matrix_add/to_text`）。
2. **degraded 折算**：累加每盘耐久，找不到盘折算降级，多副本
   强制耐久公式（`replicas_durability`）。
3. **EC 分组加缓存分流**：多副本走纠删配置聚降级数组排序打
   标识，缓存单独累加不进矩阵（`ec_config_add`）。

## 复用指南

- 冗余展示必须二维矩阵，禁止单数字。
- 缺盘必须折算降级，禁止按全盘算。
