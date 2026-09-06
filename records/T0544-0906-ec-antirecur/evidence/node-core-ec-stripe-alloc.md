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

## 算法原理

1. **质心均值**：已得块在各盘偏移分数均值，无效盘跳过，为空
   返零（`stripe_blocks_centroid:1042`）。
2. **逐块重算**：parity 先、数据后，每分配一块重算质心，后续块
   向新兴区域靠；同域硬排除；已占清位（`__new_stripe_alloc_
   buckets`）。
3. **离群重分配**：全部分配后，距质心超两倍中位差且超一桶才
   重试；新距不足旧半保留原块；失败不转整体失败
   （`stripe_reallocate_outliers:1189`）。

## 解决了什么问题

- **读寻道收敛**：同条块物理位置聚拢，重建读可并行下发，寻道
  最短。无质心则块随机散，重建读跨盘跳跃。
- **分配成功率**：纠偏 best-effort，失败保留原块，优化不转失败。
  严苛纠偏会把"够用"变"失败"，成功率塌。
- **故障域隔离**：同域硬排除在分配时而非事后检查，不合格组合
  根本建不出来。

## 引入了什么问题

- **分配变慢**：逐块重算质心加离群重试，分配路径多 O(n²) 量级
  计算。后台任务可接受，前台热点路径不可用——故只用于 EC 建条。
- **质心漂移**：parity 先分配定下基调，后续数据块被迫跟随；若
  parity 落偏，全条跟着偏。缓解靠离群重分配，但只纠偏不重建。
- **阈值拍脑袋**：两倍中位差、一桶、减半，三阈值均为经验值，无
  理论最优。换盘型需重调。

## 实际问题与修复

1. **原始偏移质心拖死小盘**：1G 盘被拖到 26%，8G 盘仅 3%，小盘提前空间耗尽（`6cf75ca7c`）。修复：分数质心（偏移占盘比均值）。防复发：质心定义写进注释，不同尺寸盘可比是硬要求。
2. **准入门控与实际拒绝不一致**：门控查冗余加 1，实际拒绝要加 2 且查故障域，空转失败任务（`6a73af4a7`）。修复：门控建模实际双条件。防复发：门控与执行共用同一判定函数。
3. **同域块无法重建**：同故障域多块损坏超冗余即丢数据（`707b0dbd6`）。修复：同域硬排除加限宽。防复发：正确性约束用硬失败，不用偏好排序。
4. **数组越界警告噪音**：离群重分配越界访问被告警（`97129d6bc`）。修复：边界收紧。防复发：Warray-bounds 零容忍，警告即修。
