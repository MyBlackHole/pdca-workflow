---
schema: pdca.asset/v2
id: ontology:domain/core-derived-state-validator-recovery-gate
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/core-derived-state-validator-recovery-gate/3.1.0
summary: Derived state validator and recovery publication gate
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
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 通读正文校验门控节，确认派生校验与恢复发布规则完整
  evidence_level: unclassified
revision: 3.1.0
authority: reference
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

# Derived state validator and recovery publication gate

## 适用范围

单一格式 subvol 核心中，primary physical pointer 已通过 transaction trigger 维护 alloc 与
backpointer 派生树，recovery 需要在 replay 后重建并验证派生状态。

## 可复用规则

1. 以 recovery.c 的主树扫描为 authority，派生树只作为待校验结果，不在 validator 中隐式修复。
2. alloc 校验至少比较 bucket generation 与 dirty sectors；backpointer 校验比较 physical
   key、owner btree/level、data type、generation、bucket length 与 owner position。
3. recovery 顺序固定为 journal replay → 清理派生树 → 从 primary 重建 → 只读集合校验 →
   publication 成功；任一 mismatch 返回错误。
4. corruption seam 应直接删除或篡改派生记录，再调用 validator，确保 missing/owner mismatch
   不会被正常路径测试掩盖。

## 边界

该规则不覆盖完整 allocator、GC、LRU、stripe/EC、VFS 或多格式迁移；这些路径需要各自对照
本地 bcachefs recovery/fsck passes。
