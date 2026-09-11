---
schema: pdca.asset/v2
id: ontology:domain/core-journal-pin-leak-tradeoff
type: domain
layer: Knowledge
status: active
summary: 错误路径泄漏pin换正确性权衡讲解
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-journal-pin-lifetime-flush
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 日志错误路径引用处理、空间换正确性决策场景
  constraint: 见正文
  testable_signal: 抽查正文借条语义与关闭函数的对应关系
  evidence_level: unclassified
- name: constraints
  desc: 泄漏决策前提
  constraint: 见正文
  testable_signal: 通读正文三段，确认借条语义、不泄漏后果、泄漏代价三条在引用代码中有对应实现
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

# 错误路径泄漏 pin 换正确性

沉淀自教学（T0541），来源为 journal 第二讲深讲用户确认内容。
对照 bcachefs `fs/journal/journal.c:__journal_entry_close_one`。
本节点只讲错误路径权衡，不讲正常钉住机制（见 pin-lifetime 节点）。

## 背景

pin 是脏数据对日志的借条：引用计数归零即欠条还清，即可回收。
关闭条目出错时，放与不放 pin 是生死抉择。

## 场景

1. **借条语义**：脏节点落盘前不许回收对应日志段，靠 pin 引用计数保证。
2. **不泄漏的后果**：放 pin 后回收线程收回未落盘脏数据对应的日志；crash 后数据既不在树也不在日志，永久丢失。
3. **泄漏的代价**：引用永不归零，该段空间永久占用；但序号链不断，恢复有起点。错误值向上传播转紧急只读，宁停机不丢数据。

## 核心概念

1. **空间换正确性**：几 MB 空间占用换不丢数据，必做交易。
2. **错误路径保推进**：序号单调推进不断，坏条明确标错。
3. **价值观**：宁可停机，不丢数据。

## 复用指南

- 错误路径设计先问：最坏丢什么？能用空间换就换。
- 泄漏必须可观测可告警，禁止静默泄漏。
