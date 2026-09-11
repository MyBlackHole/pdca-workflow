---
schema: pdca.asset/v2
id: ontology:domain/core-writepath-study-guide
type: domain
layer: Knowledge
status: active
summary: 写路径全链路专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-vfs-folio-reservation-writeback
  - ontology:domain/core-pagecache-buffered-direct-io
  - ontology:domain/core-dio-write-engine
  - ontology:domain/core-vfs-namespace-operations
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 写路径全链路系统学习、节点导航场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 5 个写相关节点 id 全部存在
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

# 写路径全链路专题学习指南

沉淀自 T0525（写路径全链路专题学习报告），来源
`records/T0525-0906-study-writepath/`。对照 bcachefs
`fs/vfs/`、`fs/data/write.c`、`fs/alloc/`。

## 背景

写知识分散在 5 个本体节点与三处源码中，初学者无入口。本节点做
导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **VFS 入口**：先读 T0525 报告二三节，再读
   `core-vfs-folio-reservation-writeback`（预留）与
   `core-pagecache-buffered-direct-io`（缓存直通），对照
   pagecache.c 与 buffered.c。
2. **直通与组装**：`core-dio-write-engine`（直通）与
   `core-vfs-namespace-operations`（重整打洞），对照 direct.c。
3. **分配落盘**：`core-allocator-wfq-watermark-reservation`（选盘
   水位），理解开桶追踪与反压。

## 七条启示速查

见 T0525 学习报告第七节：分段降级、预留先行、免读快路、聚合节流、
对齐快检、记账精确、染色隔离。

## 复用指南

- 学写先分四段，再逐段深入，最后看降级。
- 预留与记账是贯穿线，单拎出来先学。

详见 T0536 代码级精讲扩充版报告（逐函数签名参数返回调用链）。
