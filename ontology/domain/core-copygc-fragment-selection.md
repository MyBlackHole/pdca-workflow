---
schema: pdca.asset/v2
id: ontology:domain/core-copygc-fragment-selection
type: domain
layer: Knowledge
status: active
summary: CopyGC碎片选桶 + 预留 + 去重 + 独立线程
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
  desc: 数据侧碎片清运、最差桶选择、预留保障场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/copygc.c 在仓库中存在且含 bch2_copygc_get_buckets 定义
  evidence_level: unclassified
- name: constraints
  desc: 选桶清运前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认碎片排序、预留比例、去重三条前提在引用代码中有对应实现
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

# CopyGC 碎片选桶策略

沉淀自 T0499（内核第十一轮）。对照 bcachefs
`fs/data/copygc.c`。

## 核心概念

1. **按碎片 LRU 选最差桶**：数据侧按碎片度排序选桶，非全盘
   扫描（`bch2_copygc_get_buckets`）。
2. **预留比例保障**：copygc_reserve 预留空间，防清运自饿死
   （`bch2_copygc_dev_wait_amount`）。
3. **在途去重**：in_flight 去重，同一桶不重复入队。
4. **独立线程**：独立 copygc 线程，与前台分配解耦
   （`bch2_copygc_thread`）。
5. **与既有节点边界**：move 引擎管搬迁执行，本节点管选桶策略；
   btree GC 管元数据，本节点管数据侧。

## 复用指南

- 清运选桶必须按碎片排序，禁止顺序扫描。
- 清运必须自留预留，禁止把空间搬空后无处落笔。
