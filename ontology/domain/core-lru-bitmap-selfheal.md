---
schema: pdca.asset/v2
id: ontology:domain/core-lru-bitmap-selfheal
type: domain
layer: Knowledge
status: active
summary: LRU位图点操作 + 缺失自愈 + 反向校验归位
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: LRU位图维护、缺失自愈、反向校验场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/alloc/lru.c 在仓库中存在且含 bch2_lru_change 定义
  evidence_level: unclassified
- name: constraints
  desc: 位图维护前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认点编码、单向补齐、分段归位三条前提在引用代码中有对应实现
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

# LRU 位图自愈与归位

沉淀自 T0500（内核第十二轮）。对照 bcachefs `fs/alloc/lru.c`、
`fs/alloc/lru.h`、`fs/alloc/check.c`。

## 核心概念

1. **位图点操作**：(lru_id,bucket,time) 编码为位，置位清位两步
   走，相同跳过（`__bch2_lru_change`）。
2. **缺失自愈单向补齐**：精确点查无则先刷缓冲再报错后补写；
   升级前快道无条件补，防误判（`bch2_lru_check_set`）。
3. **反向校验归位**：id 分段管理；按期望回算归位，错位删点；
   旧段升级删；设备移除快删（`bch2_check_lru_key`、
   `bch2_dev_remove_lrus`）。
4. **与既有节点边界**：CopyGC选桶节点管消费侧，本节点管生产
   侧维护与自愈。

## 复用指南

- 位图索引必须生产消费分离，消费侧只读不修。
- 缺失必须单向补齐，禁止双向回写。
