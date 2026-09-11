---
schema: pdca.asset/v2
id: ontology:domain/core-backpointer-dup-to-reflink
type: domain
layer: Knowledge
status: active
summary: 双活重复物理空间转reflink共享合并
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-reflink-trigger-refcount-self-delete
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 反向指针校验发现双活重复块的合并处理场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/alloc/backpointers.c 在仓库中存在且含 check_bp_dup 定义
  evidence_level: unclassified
- name: constraints
  desc: 合并前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认双副本干净、重叠区切分两条前提在引用代码中有对应实现
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

# 双活重复转reflink共享

沉淀自 T0497（内核第九轮，二轮复核）。对照 bcachefs
`fs/alloc/backpointers.c`。

## 核心概念

1. **校验分支内合并**：backpointers 校验发现双副本均干净时，
   不删任一副本，切重叠区为 reflink 共享
   （`check_bp_dup`、`extents_to_reflink`）。
2. **与既有节点边界**：EC 节点管条带重建，move 节点管搬运，
   自愈节点管分级，本节点是校验分支内的特定合并策略。

## 复用指南

- 校验发现的重复数据优先转共享而非删除，删除丢冗余。
- 合并必须在校验分支内原子完成，禁止先报后修两步走。
