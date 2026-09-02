# Bug分析：调研任务拆出开发子任务的scenario_type断层

## 背景

提交 `bcb5ff17` 将 `T0501/T0502/T0503(research)` 与 `T0505-0512(development)` 混入一commit，`T0503` research 全栈报告 `composed_of 6叶` 未细化即跳至 `T0506-0511` 6 `development` 叶实现，缺 `research` 叶本体细化层，违 `ontology-governs-ontology: ontology_governs_creation` 与 `hybrid Topdown→Bottomup` 双向。

## 复现步骤

- 查 `T0503` `research` `composed_of 6叶` 未生 `research` 叶任务即生 `T0506-0511` `development`
- `git log --oneline bcb5ff17` 单commit含14任务 `research+development` 混排
- `grep scenario_type pdca/tasks/0903-zfs-*/task.json` 显示 `T0506-0511` 为 `development`

## 根因假设

`to-tickets#3.5` 默认 `tree_split` 未区分 `research`/`development` 双层，`task_identity` 继承 `scenario_type` 时父 `T0503 research` 被 `T0505 development` 截断，未按 `research叶→本体→develop叶` 双层建任务。

## 修复方案

- 已补 `T0513-T0518` 6 `research` 叶于 `T0503` 下（`parent T0503`），`scenario_type research`，各产 `zfs-*` 本体细化
- 现 `T0506-0511` 保留为 `development` 实现叶，`T0503→6 research叶→6 develop叶→system` 双层叶→根闭环
- 提交拆分：`research` 与 `development` 分 `commit`，`Flow Issue` 记 `scenario_type断层`

## 验收标准

- [ ] AC-1 根因已定位且 `Flow Issue` 已登记
- [ ] AC-2 6 `research` 叶已创建 `parent T0503` `scenario_type research` 且 `validate` 通过
- [ ] AC-3 双层叶→根可 `compute-frontier valid:true` 且 `GATE OK`
