---
schema: pdca.asset/v2
id: ontology:domain/core-read-replica-pick
type: domain
layer: Knowledge
status: active
summary: 读副本延迟加权择优 + 重试分级 + EC降级
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 多副本读优选、校验重试分级、EC 重建降级场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/extents.c 在仓库中存在且含 bch2_bkey_pick_read_device 定义
  evidence_level: unclassified
- name: constraints
  desc: 择优前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认缓存剔除、延迟加权、EC兜底三条前提在引用代码中有对应实现
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

# 读副本延迟加权择优

沉淀自 T0498（内核第十轮）。对照 bcachefs
`fs/data/extents.c`。

## 核心概念

1. **延迟平方加权随机**：偏好快盘，缓存与过期剔除
   （`ptr_better`）。
2. **校验重试分级**：按重试次数分级，逐级放宽
   （`crc_retry_nr`）。
3. **EC 降级兜底**：副本不足转 EC 重建
   （`has_ec → do_ec_reconstruct`）。
4. **与既有节点边界**：EC 修复节点管条带重建，本节点管读时
   副本选择与降级决策。

## 复用指南

- 多副本读必须延迟加权择优，禁止固定首盘。
- 重试必须分级放宽，一次失败不直接降级。
