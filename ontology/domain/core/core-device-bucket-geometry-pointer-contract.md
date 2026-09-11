---
schema: pdca.asset/v2
id: ontology:domain/core-device-bucket-geometry-pointer-contract
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/core-device-bucket-geometry-pointer-contract/3.1.0
summary: 设备 bucket geometry 与 physical pointer 合约
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
  testable_signal: 通读正文geometry合约节，确认物理指针合约规则完整
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

# 设备 bucket geometry 与 physical pointer 合约

physical pointer 的 bucket 归属必须从持久化 members-v2 geometry 得出：

`bucket = ptr.offset / member.bucket_size`，
`bucket_offset = ptr.offset % member.bucket_size`，
`bucket_position = (ptr.dev, bucket)`。

offset 不能直接作为 bucket。有效 mapping 的前置是 member record 存在且 alive、device
online、bucket size 非零，且 `first_bucket <= bucket < nbuckets`；pointer generation 还必须
与 alloc generation 相容。插入无效 pointer 不得创建派生 alloc/backpointer 状态。

members-v2 已是单一格式持久化 geometry 的权威来源。recovery 必须先验证、载入 members
并建立 online-device state，随后才 replay/scan physical pointers。bucket mapping 本身不
包含 allocator、LRU、discard、GC 或 stripe 策略。

来源：T0184，`records/T0184-0802-device-bucket-geometry-contract/conclusion.md`。
