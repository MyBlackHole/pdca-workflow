---
schema: pdca.asset/v2
id: ontology:domain/core-ec-four-lectures
type: domain
layer: Knowledge
status: active
summary: EC四讲教学收束：写洞/生命期/修复/重建
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-ec-study-guide
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-read-replica-pick
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: EC 教学收束、四讲导航场景
  constraint: 见正文
  testable_signal: 抽查正文四讲一句话与源报告对应
  evidence_level: unclassified
- name: constraints
  desc: 收束对应前提
  constraint: 见正文
  testable_signal: 通读正文四讲节，确认每讲一句话与教学内容一致且有代码依据
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

# EC 四讲教学收束

沉淀自教学（T0542），来源为 EC 四讲用户确认内容。对照 bcachefs
`fs/data/ec/`。本节点只做教学收束，不讲机制细节（机制见指南与
修复/优选节点）。

## 背景

四讲散落在对话中，需一页收束供复习。本节点每讲一句话加详述索引。

## 核心概念

1. **写洞绕行**：前台多副本，后台整桶，原子换指针，无中间态
2. **整体生命**：整体出生锁定搬迁死亡，复用判三元一致
3. **激进修复**：阈值 1，竞态自退，不足疏散，删修互斥
4. **静默重建**：直读优先，证明分级，校验两次，降级静默

## 四讲详述

1. **第一讲写洞问题**：3+1 例子走 RMW 六步，crash 落中间即写洞；
   后台整桶以窗口期空间换数学无中间态。
2. **第二讲生命期复用**：整体锁定，位图锚活块，读到折叠，引用
   归零删除。
3. **第三讲修复降级**：单坏即修，并发无害化，缺口疏散，意图锁
   防删。
4. **第四讲读重建**：直读优先，锁内靠锁 IO 后靠钉，先验后算，
   预期静默。

## 违反后果

- 忘写洞：前台编码必遇 RMW 与中间态，无解。
- 忘整体：部分操作是 bug 温床。
- 忘阈值：容忍计数留给监控，不留给修复。
- 忘静默：预期刷屏耗尽预算，真错被淹没。

## 复用指南

- 复习先背四句话，再展开详述，最后对照源码。
- 教别人从 3+1 例子开始，不从定义开始。
