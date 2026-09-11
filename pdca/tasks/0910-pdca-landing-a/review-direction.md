# 方向规则满足性审查（B根→叶 / A叶→根）

## 文字层 ✅
- 设计核心 ontology:concept/pdca 1.0.3：B 根→叶、A 叶→根、方向总述原话。
- 执行层 ontology:process/flow-do 1.0.2：路径A/B 方向句与 hybrid 引用。

## B 根→叶机制 ✅（硬闭环）
- to-tickets 默认关系树拆分；ARCHIVE_ONTOLOGY_ISLANDS（islands>0 阻断 archive）；
  research 本体沉淀决策。当前 islands: 0，全绿。

## A 叶→根机制 ✅（基本满足）
- to-tickets 叶→根拆分 + ready-set/compute-frontier 独立验证；
  T2147 实测 batches [[T2148],[T2149],[T2150]]，T2148 归档后 ready-set=[T2149]。

## 缺口（1，非阻断）
- transition-phase 不校验 dependencies 前置状态，顺序执行靠调度纪律。
  建议：T2149 可选加固，或接受为纪律。现实风险无（T2148 已归档）。
