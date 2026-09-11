---
schema: pdca.asset/v2
id: ontology:domain/core-time-stats-cheap-instrumentation
type: domain
layer: Knowledge
status: active
summary: time_stats 懒升级埋点 + 双均值防漂移 + X 宏一源多用
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 全路径性能埋点、低开销分位数、卡因归因场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/util/time_stats.c 在仓库中存在且含 quantiles_update 定义
  evidence_level: unclassified
- name: constraints
  desc: 低开销埋点的前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认懒升级阈值、双均值权重、关开关零开销三条前提在引用代码中有对应实现
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

# time_stats 低开销埋点体系

沉淀自 T0490（纵深分析）。对照 bcachefs `fs/util/time_stats.c`、
`fs/util/time_stats.h`、`fs/bcachefs.h`、`fs/debug/trace.h`。

## 核心概念

1. **懒升级 percpu 缓冲**：初期自旋锁直写，样本超 1024 且中位
   延迟够小才 alloc_percpu 缓冲攒批 flush；头注"cheap enough
   to shotgun everywhere"，敢全路径埋点
   （`__bch2_time_stats_update`）。
2. **双均值防漂移**：每次同时更新全量均值与半衰期加权均值，
   文本并列"since mount / recent"，一眼区分一直慢 vs 刚变坏
   （`time_stats_update_one`）。
3. **常数内存近似分位数**：NR_QUANTILES 中序树存 m/step 自适应
   追踪，O(logN)，默认关闭按需开（`quantiles_update`）。
4. **X 宏一源多用**：`BCH_TIME_STATS` 一次定义 40+ 事件（含
   blocked 卡因语义），sysfs 属性/读写/文件表自动生成；加埋点
   只加一行（`bcachefs.h`、`sysfs.c`）。
5. **trace 零成本分级**：关开关时生成空 inline + enabled=false，
   调用点守卫，高频路径无负担（`trace.h`）。

## 复用指南

- 埋点开销必须分级：冷路径直写、热路径攒批、超热路径可关，
  且切换自动（阈值）而非手动。
- 统计必须同时回答"一直如何"与"最近如何"，单均值必被长尾
  或漂移误导。
- 事件定义与消费表必须同源生成，加事件只改一处。
