---
schema: pdca.asset/v2
id: ontology:domain/core-ec-repair-evacuate-retry
type: domain
layer: Knowledge
status: active
summary: EC修复单坏即降级 + 缺口疏散 + retry 队列 + 意图锁防删
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 纠删条带降级检测、设备不足时重建、并发修复竞态场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/ec/create.c 在仓库中存在且含 bch2_stripe_repair 定义
  evidence_level: unclassified
- name: constraints
  desc: 修复流程前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认降级阈值、疏散前置、意图锁持有三条前提在引用代码中有对应实现
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

# EC修复疏散重试队列

沉淀自 T0492（内核第四轮）。对照 bcachefs
`fs/data/ec/create.c:bch2_stripe_repair/stripe_degraded`、
`fs/data/reconcile/work.c:do_reconcile_stripe`。

## 核心概念

1. **单坏即降级**：遍历全部 ptrs 任一坏/疏散即判降级，无数量
   容忍，阈值为 1（`stripe_degraded`）。
2. **修复竞态空转返回**：入口先判已不降级则打 trace 直接返回，
   把并发已修复/设备恢复的误触发变可观测事件而非锁
   （`stripe_repair_race`）。
3. **缺口疏散前置**：`need = max(0, live + redundant - devs)`，
   缺口>0 先疏散活块再重建，返回特殊码而非原地死等
   （`bch2_evacuate_data`）。
4. **retry 延后队列**：捕获疏散码则压入 `{idx, io_seq}`，排空
   move IO 后逐项重做，每 key 后调用排空（`stripe_retry_
   must_wait`、`do_retry_stripes`）。
5. **意图锁防空 stripe 误删**：修复首行 BUG_ON 意图锁，与删空
   stripe 触发器互斥；handle 获取失败视为已删返回
   （`bch2_stripe_handle_tryget`）。

## 复用指南

- 降级检测阈值必须显式（1 坏即降 vs 容忍 N 坏），禁止隐式。
- 设备不足时先疏散后重建 + 延后重试，禁止原地死等。
- 并发修复的后来者必须无害化退出并留 trace，禁止重复分配。
