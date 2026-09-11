---
schema: pdca.asset/v2
id: ontology:domain/core-journal-three-conflicts
type: domain
layer: Knowledge
status: active
summary: journal三矛盾场景化讲解：保序/空间/回收
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:domain/core-journal-space-topk-ram
  - ontology:domain/core-journal-watermark-thread
  - ontology:domain/core-journal-study-guide
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: journal 三矛盾教学、场景化理解场景
  constraint: 见正文
  testable_signal: 抽查正文三个场景的代码依据存在
  evidence_level: unclassified
- name: constraints
  desc: 讲解适用前提
  constraint: 见正文
  testable_signal: 通读正文三矛盾节，确认每矛盾含场景冲突解法三段且有代码依据
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

# journal 三矛盾场景化讲解

沉淀自教学（T0540），来源为 SIX 锁教学后 journal 第一讲用户确认内容。
对照 bcachefs `fs/journal/seq_blacklist.c`、`reclaim.c`。
本节点只讲场景化教学，不讲机制细节（机制见关联节点）。

## 背景

三矛盾不讲场景只讲机制，初学者记不住。本节点每矛盾配一个具体
crash/运行场景，先感受冲突，再给解法。

## 矛盾一：保序

1. **场景**：改键分两步落盘，先数据页后日志条。crash 落在两步
   之间，数据新日志旧。
2. **冲突**：重放旧日志覆盖新数据即乱序 corrupt。
3. **解法**：落盘数据记序号，启动问新于日志否，新的丢弃且序号
   永不复用并持久化。以日志为准，数据只许比日志旧
   （`seq_blacklist.c`）。

## 矛盾二：空间

1. **场景**：64 盘阵列，慢盘日志不动，快盘狂写。算剩余空间时
   平均掩盖短板，最小被坏盘拖死。
2. **冲突**：单数字无意义，异步流水线中游标才有意义。
3. **解法**：三视角游标加 Top-K 短板，取能用到的最差，不取全局
   最小不取平均（`reclaim.c:__journal_space_available`）。

## 矛盾三：回收

1. **场景**：脏节点 pin 住日志，回收要推进须刷脏，刷脏要写新
   日志需空间，空间要回收推进。
2. **冲突**：超前回收即死锁。
3. **解法**：遇未重放直接停，不等不抢不超时重试
   （`reclaim.c:778`）。

## 一句话串联

保序以日志为准、空间以能用最差为准、回收以不死锁为准。

## 核心概念

三矛盾对应三套机制，不混用：

1. **保序机制**：序号黑名单加永不复用加持久化
2. **空间机制**：三视角游标加 Top-K 短板加非对称钳制
3. **回收机制**：引用钉住加超前即停加节拍线程

详见关联的机制节点，本节点只保留场景化入口。

## 复用指南

- 讲 journal 先讲三场景，再给机制，最后背一句话。
- 每个解法追问一句：不这样会死在哪？
