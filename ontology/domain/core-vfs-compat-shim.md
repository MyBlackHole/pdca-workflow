---
schema: pdca.asset/v2
id: ontology:domain/core-vfs-compat-shim
type: domain
layer: Knowledge
status: active
summary: 跨内核VFS拆除路径双分支垫片
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-vfs-namespace-operations
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 跨内核版本 VFS 接口兼容、拆除路径适配场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/vfs/ioctl.c 在仓库中存在且含 start_removing_user_path_at 定义
  evidence_level: unclassified
- name: constraints
  desc: 垫片前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认版本分支、写者配对两条前提在引用代码中有对应实现
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

# 跨内核 VFS 拆除垫片

沉淀自 T0501（内核第十三轮）。对照 bcachefs `fs/vfs/ioctl.c`。

## 核心概念

1. **双分支垫片**：适配新旧内核拆除接口，处理写者计数与父目
   录重验（`start_removing_user_path_at`、
   `bch2_fs_file_ioctl`）。
2. **与既有节点边界**：命名空间节点管操作语义，本节点管版本
   兼容垫片。

## 复用指南

- 跨版本接口必须双分支垫片，禁止单分支假设。
- 写者计数与重验必须配对，禁止半截适配。
