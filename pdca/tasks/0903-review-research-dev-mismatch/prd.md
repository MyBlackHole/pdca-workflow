# 审查调研任务拆出开发子任务的scenario_type断层根因

## 背景

`T0503-0903-research-zfs-implementation` `research` 全栈调研 `composed_of 6叶` 未生 `research` 叶任务即由 `T0505-0903-zfs-system-dev` `development` 生 `T0506-0511` 6 `development` 叶，`bcb5ff17` 单commit混 `research+development` 14任务，违 `ontology-governs-ontology: ontology_governs_creation`（调研必须基于 `research-topdown` 方法论产本体）与 `hybrid Topdown→Bottomup` 双层。

## 目标

- 双轴审查：Standards（`ontology-creation-gate` 6规则、WBS 100%、叶三准绳）与 Spec（PRD `拆分映射` 与 `tree_split` 是否叶→根）
- 定位根因至 `to-tickets#3.5` 未分 `research/dev` 双层与 `task_identity` 继承截断

## 范围

- 输入：`T0503/T0505/T0506-0511/T0513-0518` 14任务 `task.json`、`bcb5ff17` diff、`ontology-governs-ontology`、`hybrid-methodology`
- 输出：`records/T0520/report.md` 双轴报告 + `Flow Issue` 登记 + 修复验证
- 不做：不改 `archive` 不可变 `task.json`

## 功能需求

1. Standards轴：校验 `research` 未生 `research` 叶即跳 `development` 是否违 `AC-1 type受控` 与 `WBS 100%`（缺 `research` 叶层）
2. Spec轴：校验 `T0503 PRD##拆分映射` 与 `tree_split` 6叶候选是否被 `T0505 development` 冒用
3. 根因：追至 `to-tickets` 与 `task_identity` 未做 `research→本体→development` 双层闸

## 非功能需求

- 报告 `Standards/Spec` 双栏 <400字/轴，`grep scenario_type` 可复现

## 验收标准

- [ ] AC-1 双轴报告已产：Standards与Spec各 <400字且引 `file:line`
- [ ] AC-2 根因已定位：`to-tickets`/`task_identity` 双层缺失
- [ ] AC-3 Flow Issue已登记且 `validate` 通过
- [ ] AC-4 全绿 `islands:0` `GATE OK`
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:principle/ontology-governs-ontology
ontology:domain/ontology-hybrid-methodology
ontology:concept/ontology-creation-gate
```

## 拆分映射

- 双轴审查 -> ontology:principle/ontology-governs-ontology
