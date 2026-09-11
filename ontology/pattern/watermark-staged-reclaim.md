---
schema: pdca.asset/v2
id: ontology:pattern/watermark-staged-reclaim
type: pattern
layer: Knowledge
status: active
summary: 多条件水位分级回收模式
source_task: T0506
relations:
  relates_to:
  - ontology:domain/core-journal-watermark-thread
  - ontology:domain/core-journal-space-topk-ram
  instance_of:
  - ontology:pattern
attributes:
- name: applicability
  desc: 日志空间回收触发、后台节拍刷盘场景
  constraint: ''
  testable_signal: 抽查源节点 core-journal-watermark-thread 存在
  evidence_level: unclassified
- name: consequences
  desc: 回收及时、误触发少、水位定义需精确
  constraint: ''
  testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
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

# 多条件水位分级回收

来源：T0506 提炼；源节点 `core-journal-watermark-thread`、
`core-journal-space-topk-ram`；对照 bcachefs
`fs/journal/reclaim.c`。

## 问题

单指标触发回收要么过早（浪费 IO）要么过晚（卡死写入）。

## 方案

空间/pin/写缓冲/开桶四条件或触发；三视角记账供水位计算；
RAM 封顶防误报；后台线程节拍睡加踢醒；满时就地回收。

## 后果

回收及时且误触发少；代价是水位定义必须精确，四条件缺一即
漏场景；钳制不对称性必须显式论证。
