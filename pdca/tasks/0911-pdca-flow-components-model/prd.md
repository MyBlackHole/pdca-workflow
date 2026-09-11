# 建模 PDCA 流程构件关系

## 目标

补齐 `pdca-flow-model` 对任务、阶段、转换、门禁、验收标准、证据和判定的组成与追溯关系。

## 验收标准

- [ ] AC-1（回链父 AC-1）: 所有必需流程构件均由 `composed_of` 显式引用且引用可解析。
- [ ] AC-2（回链父 AC-2）: 合法转换仅为 plan→do→check→act→archive，图无环。
- [ ] AC-3（回链父 AC-5）: 每阶段入口、动作、产物和退出门禁可追溯。

## 关联本体节点

`ontology:process/pdca-flow-model`

## 拆分映射

- 流程构件关系 -> ontology:concept/pdca-task
