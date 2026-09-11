---
schema: pdca.asset/v2
id: ontology:domain/core-alloc-study-guide
type: domain
layer: Knowledge
status: active
summary: 分配器专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:domain/core-device-membership-lifecycle
  - ontology:domain/core-accounting-delta-reconcile
  - ontology:domain/core-quota-charge-enforce
  - ontology:domain/core-lru-bitmap-selfheal
  - ontology:domain/core-alloc-trigger-discard-duplex
  - ontology:domain/core-copygc-fragment-selection
  - ontology:pattern/weighted-fair-allocation
  - ontology:pattern/unified-relocation-engine
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 分配器机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 9 个分配相关节点 id 全部存在
  evidence_level: unclassified
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: 通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确
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

# 分配器专题学习指南

沉淀自 T0517（分配器专题学习报告），来源
`records/T0517-0906-study-alloc/`。对照 bcachefs `fs/alloc/`。

## 背景

分配知识分散在 9 个本体节点与 12700 行源码中，初学者无入口。
本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **前台分配**：先读 T0517 报告一至四节，再读
   `core-allocator-wfq-watermark-reservation`（选盘水位预留）与
   `pattern/weighted-fair-allocation`，对照 foreground.c DOC。
2. **成员与记账**：`core-device-membership-lifecycle`（全周期）、
   `core-accounting-delta-reconcile`（双轨）、
   `core-quota-charge-enforce`（收费），对照 members.c 与
   accounting.c。
3. **后台维护**：`core-lru-bitmap-selfheal`（位图）、
   `core-alloc-trigger-discard-duplex`（触发丢弃）、
   `core-copygc-fragment-selection`（选桶），对照 lru.c 与
   discard.c；搬迁看 `pattern/unified-relocation-engine`。

## 九条启示速查

见 T0517 学习报告第九节：死同穴、零递归、加权无饿死、多档水位、
双层预留、全流水线、双轨记账、生产消费分离，外加借位省内存。

## 复用指南

- 学分配先定写点隔离策略，再看选盘，最后看回收。
- 前台后台分开学，记账贯穿两边。

详见 T0535 代码级精讲扩充版报告（`records/T0535-0906-detail-batch1/`，逐函数签名参数返回调用链）。
