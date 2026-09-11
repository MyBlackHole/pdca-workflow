---
schema: pdca.asset/v2
id: ontology:domain/core-acl-codec-idempotent
type: domain
layer: Knowledge
status: active
summary: ACL长短条目编解码 + 删建幂等 + 标志同步
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-inode-acl-opts-shortcircuit
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: ACL 盘上编解码、删建幂等、标志同步场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/fs/acl.c 在仓库中存在且含 bch2_acl_from_disk 定义
  evidence_level: unclassified
- name: constraints
  desc: 编解码前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认步长校验、幂等语义两条前提在引用代码中有对应实现
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

# ACL 长短编解码与幂等

沉淀自 T0501（内核第十三轮）。对照 bcachefs `fs/fs/acl.c`、
`fs/fs/acl.h`。

## 核心概念

1. **长短条目两遍编解码**：版本号头加短条目与长条目；解码先
   校验步长计数再分配转换；编码先计数再定长，超限报错
   （`bch2_acl_from_disk`、`bch2_acl_to_xattr`）。
2. **删建幂等加标志同步**：有则设，无则删且缺失归零；非目录
   默认值按有无区分报错；成功同步标志位；另落模式与时间
   （`bch2_set_acl_trans`）。
3. **与既有节点边界**：短路节点管查询快路，本节点管编解码与
   删建语义。

## 复用指南

- 变长编解码必须先校验步长再分配，禁止边解边扩。
- 删建必须幂等，缺失删除归零而非报错。
