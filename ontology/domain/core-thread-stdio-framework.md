---
schema: pdca.asset/v2
id: ontology:domain/core-thread-stdio-framework
type: domain
layer: Knowledge
status: active
summary: kthread与fd管道后台交互线程框架
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-chardev-control-plane
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 后台交互线程、管道流式交互、关 fd 停线程场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/util/thread_with_file.c 在仓库中存在且含 bch2_run_thread_with_stdio 定义
  evidence_level: unclassified
- name: constraints
  desc: 框架前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认关停语义、懒分配两条前提在引用代码中有对应实现
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

# kthread 管道交互框架

沉淀自 T0500（内核第十二轮）。对照 bcachefs
`fs/util/thread_with_file.c`。

## 核心概念

1. **关 fd 即停线程**：后台交互线程与 fd 生命周期绑定
   （`bch2_run_thread_with_stdio`）。
2. **懒分配管道**：4K 管道按需分配，poll 驱动交互。
3. **与既有节点边界**：chardev 节点管控制分发，本节点管线程
   与管道框架。

## 复用指南

- 后台交互线程必须与 fd 同生命周期，禁止孤儿线程。
- 管道按需分配，禁止常驻大缓冲。
