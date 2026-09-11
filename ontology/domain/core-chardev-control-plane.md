---
schema: pdca.asset/v2
id: ontology:domain/core-chardev-control-plane
type: domain
layer: Knowledge
status: active
summary: chardev外部引用防死锁 + 长任务文件流回传
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-observability-status-text-matrix
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 用户态控制分发、长任务进度流式回传场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/init/chardev.c 在仓库中存在且含 bch2_device_lookup_outer 定义
  evidence_level: unclassified
- name: constraints
  desc: 控制面前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认外部引用、流式回传两条前提在引用代码中有对应实现
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

# chardev 控制面防死锁与流回传

沉淀自 T0498（内核第十轮）。对照 bcachefs `fs/init/chardev.c`。

## 核心概念

1. **外部引用防死锁**：设备查找用外部引用规避引用计数与状态
   锁死锁（`bch2_device_lookup_outer`）。
2. **长任务文件流回传**：数据任务经线程文件以读流式回传进度
   总量与完成量（`bch2_ioctl_data`、`bch2_data_job_read`）。
3. **与既有节点边界**：成员全周期节点管生命周期，可观测矩阵
   管状态文本，本节点管用户态控制分发。

## 复用指南

- 控制面引用必须与状态锁解耦，禁止持锁取引用。
- 长任务进度用文件流回传，禁止一次性大缓冲。
