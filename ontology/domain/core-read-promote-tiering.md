---
schema: pdca.asset/v2
id: ontology:domain/core-read-promote-tiering
type: domain
layer: Knowledge
status: active
summary: 读提升三否决 + 双路径 + 限流 + 整区分片
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
  desc: 成功读热数据分层、提升限流、事务安全降级场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/read.c 在仓库中存在且含 should_promote 定义
  evidence_level: unclassified
- name: constraints
  desc: 提升前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认三否决、限流、重启透传三条前提在引用代码中有对应实现
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

# 成功读提升分层

沉淀自 T0498（内核第十轮）。对照 bcachefs `fs/data/read.c`。

## 核心概念

1. **三否决**：已在目标、未写入、目标拥塞各计事件并返错；自愈
   路径跳过（`should_promote`）。
2. **双路径**：非 IO 错走提升路径（加副本 + 缓存 + 指定盘 +
   免等）；IO 错走自愈路径（按失败置位），无重写位不提升
   （`__promote_alloc`）。
3. **per-CPU 信号量限流**：先取写引用，再试拿本 CPU 信号量，
   失败计数；释放按 CPU 归还；初值 32（`promote_free`）。
4. **整区与碎片**：自愈/全读/选项定整区，否则碎片；reflink 走
   共享树余走数据树；子读继承选项并强制弹跳全读
   （`promote_alloc`）。
5. **重启不可吞**：仅事务重启以指针回传令读重试，其余只打点
   降级普通读，防毒化事务后崩溃（`promote_alloc:418-419`）。
6. **与既有节点边界**：误报过滤节点管失败读降噪，本节点管成
   功读分层。

## 复用指南

- 热分层必须在成功读路径，与错误重试路径分离。
- 提升必须限流 + 否决条件，禁止无节制复制。
- 事务重启必须透传，禁止吞错降级。
