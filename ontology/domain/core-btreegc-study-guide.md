---
schema: pdca.asset/v2
id: ontology:domain/core-btreegc-study-guide
type: domain
layer: Knowledge
status: active
summary: btreeGC专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-btree-gc-mark-sweep
  - ontology:domain/core-interior-gc-update-gate
  - ontology:domain/core-btree-node-scan-rebuild
  - ontology:domain/core-accounting-delta-reconcile
  - ontology:domain/core-copygc-fragment-selection
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: btree GC 机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 5 个 GC 相关节点 id 全部存在
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

# btree GC 专题学习指南

沉淀自 T0527（btree GC 专题学习报告），来源
`records/T0527-0906-study-btreegc/`。对照 bcachefs
`fs/btree/check.c`。

## 背景

GC 知识分散在 5 个本体节点与 check.c 中，初学者无入口。本节点做
导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **扫描标记**：先读 T0527 报告二至五节，再读
   `core-btree-gc-mark-sweep`（位点水位补标），对照 check.c
   主流程。
2. **落盘协同**：`core-interior-gc-update-gate`（指针更新）与
   `core-accounting-delta-reconcile`（记账），理解提交协同。
3. **重建清运**：`core-btree-node-scan-rebuild`（扫描重建）与
   `core-copygc-fragment-selection`（数据侧清运），对照两端。

## 八条启示速查

见 T0527 学习报告第八节：合一遍历、全序位点、单调水位、补标对账、
自适应深度、记后改、持锁显式、分段协同。

## 复用指南

- 学 GC 先定遍历序，再看标记，最后看协同。
- 元数据 GC 与数据 copygc 对照学，一次懂两边。

 详见 T0537 代码级精讲扩充版报告（逐函数签名参数返回调用链）。

详见 T0539 深挖驱动版报告（`records/T0539-0906-study-btreegc2/`，
基于 B 向深挖 10 条，侧重位点水位补标拓扑全流程）。
