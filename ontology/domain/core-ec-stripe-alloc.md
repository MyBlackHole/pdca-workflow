---
schema: pdca.asset/v1
id: ontology:domain/core-ec-stripe-alloc
type: domain
layer: Knowledge
status: active
summary: 条带分配质心算法与离群重分配
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-ec-stripe-geometry
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 条带块分配位置优化、离群纠偏场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文质心与重分配函数在仓库中存在"
- name: constraints
  desc: 分配优化前提
  constraint: 见正文
  testable_signal: "通读正文三节，确认质心均值、逐块重算、减半才换三条在引用代码中有对应实现"
---

# 条带分配质心算法

沉淀自 T0543。对照 bcachefs `fs/data/ec/create.c`
（`stripe_blocks_centroid`、`__new_stripe_alloc_buckets`、
`stripe_reallocate_outliers`）。

## 背景

同条块分散在各盘各处，读时寻道爆炸。分配时让块向已得块的质心
靠拢，读放并行、寻道收敛。

## 核心概念

1. **质心均值**：已得块在各盘偏移分数均值，无效盘跳过，为空
   返零（`stripe_blocks_centroid:1042`）。
2. **逐块重算**：parity 先、数据后，每分配一块重算质心，后续块
   向新兴区域靠；同域硬排除；已占清位（`__new_stripe_alloc_
   buckets`）。
3. **离群重分配**：全部分配后，距质心超两倍中位差且超一桶才
   重试；新距不足旧半保留原块；失败不转整体失败
   （`stripe_reallocate_outliers:1189`）。

## 违反后果

- 无质心：块随机散，读寻道爆炸。
- 强制纠偏：重试失败转整体失败，分配成功率塌。

## 复用指南

- 位置亲和用质心迭代，best-effort 纠偏永不恶化。
- 优化失败不是失败，保留原值继续。
