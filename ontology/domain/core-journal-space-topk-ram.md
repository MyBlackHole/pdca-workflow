---
schema: pdca.asset/v2
id: ontology:domain/core-journal-space-topk-ram
type: domain
layer: Knowledge
status: active
summary: journal三视角记账 + Top-K短板 + RAM钳制 + 快慢水位
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 日志空间多视角记账、异构设备短板仲裁、预留快慢路径场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/journal/reclaim.c 在仓库中存在且含 journal_dev_space_available 定义
  evidence_level: unclassified
- name: constraints
  desc: 记账仲裁前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认末桶保留、Top-K取值、非对称钳制三条前提在引用代码中有对应实现
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

# journal三视角记账 + Top-K 短板

沉淀自 T0492（内核第四轮）。对照 bcachefs
`fs/journal/reclaim.c`、`fs/journal/journal.h`、
`fs/journal/journal.c`。

## 核心概念

1. **三视角 + 末桶保留**：按 from 取 discard/dirty_ondisk/dirty
   三游标算可用桶；落盘游标追平时减一，写新 last_seq 能腾桶
   前不耗尽最后一桶（`bch2_journal_dev_buckets_available`）。
2. **Top-K 短板仲裁**：逐盘算可用，插入排序取前 K 大，最小者
   为结果；K 取在线数与元数据副本数较小值
   （`__journal_space_available`）。
3. **RAM/4 非对称钳制**：total 钳常量顶，clean 随脏增长收缩，
   驱动节流；仅钳 total 不钳 next_entry，防 last_seq 推进卡死。
4. **in_flight 未写扣减**：遍历在途条目扣减 sectors，不足借整
   桶对齐（`journal_dev_space_available`）。
5. **may_skip_flush 三条件**：落盘与内存差距小且落盘占优时可
   免 flush（`bch2_journal_space_available`）。
6. **res 快慢双层水位**：快路径无锁先判 offset 与 watermark；
   失败复判 + must_open 重试；满且低水位时就地直接回收
   （`journal_res_get_fast`、`__journal_res_get`）。

## 复用指南

- 多视角记账必须显式定义每视角游标，禁止单数字 Kennedy。
- 异构成员取短板时用 Top-K 而非最小值，K 由冗余度决定。
- 钳制必须是非对称的：保推进的值不钳，只钳总量。
