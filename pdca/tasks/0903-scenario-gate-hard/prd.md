# 硬门禁：research→development scenario_type双层闸防断层

## 背景

T0520双轴审查定位 `T0503 research` 未生 `research` 叶即跳 `T0506-0511 development`，`to-tickets#3.5` 与 `task_identity` 未分 `research叶产本体→develop叶用本体` 双层闸，单commit混14任务。

## 目标

- `to-tickets` 与 `task_identity` 增双层闸：`research` 父仅生 `research` 叶，`development` 父仅生 `development` 叶，跨层需显式 `ontology:` 回链批注
- `ci-ontology-gate` + `doctor` 增 `SCENARIO_MISMATCH` 硬拦，`GATE OK` 外

## 范围

- 输入：`scripts/to-tickets.md` `task_identity.py` `ontology_gate.py` `pdca_core.py`
- 输出：3脚本+1 check脚本 `check-scenario-mismatch.py` 接入 `ci-gate`，全绿
- 不做：不改已 `archive` 14任务

## 功能需求

1. `task_identity` 创子时校验：父 `research` 生 `research` 叶（`research→本体`），父 `development` 生 `development` 叶（`本体→实现`），跨层 `development` 生 `research` 需 `ontology:` 批注否则 `SCENARIO_MISMATCH`
2. `to-tickets` 文档增双层说明
3. `check-scenario-mismatch.py` 扫描 `pdca/tasks/*/task.json` 父子 `scenario_type` 混层无批注即 `1`，接入 `ci-ontology-gate`

## 非功能需求

- `islands:0`，`GATE OK`

## 验收标准

- [ ] AC-1 双层闸已落：`research` 父生 `development` 叶无批注被硬拦 `SCENARIO_MISMATCH`
- [ ] AC-2 check脚本已产：`check-scenario-mismatch.py` 可 `python3 scripts/check-scenario-mismatch.py` 0/1
- [ ] AC-3 ci接入：`ci-ontology-gate` 调 check 且 `GATE OK`
- [ ] AC-4 全绿 islands:0
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:principle/ontology-governs-ontology
ontology:domain/ontology-hybrid-methodology
```

## 拆分映射

- 双层闸 -> ontology:principle/ontology-governs-ontology
