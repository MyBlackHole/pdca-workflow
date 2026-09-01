# PRD模板硬化与fragment默认：缺映射即阻断

## 背景
当前 `skill-to-tickets:3.5` 为告警回退，PRD可无 `## 拆分映射` 通关，`meta.ontology_fragment` 可空。

## 目标
新建development任务默认带 `fragment` 与 `## 拆分映射`，缺失即阻断而非告警。

## 功能需求
1. PRD模板预置 `## 拆分映射` 与 `## 关联本体节点`，`triage` 产出即含
2. `task_identity` 新建时默认 `ontology_anchor=ontology:concept/pdca-task`，无 `fragment` 时 `pdca-doctor` 报 `ONTOLOGY_FRAGMENT_MISSING`
3. 有 `fragment` 无映射时 `ontology_tree_split` 报错退出，不回退

## 验收标准
- [ ] AC-1 新建任务 PRD 必含 `## 拆分映射` 与 `## 关联本体节点`
- [ ] AC-2 有fragment无映射时 `ontology_tree_split` 报错退出，无fragment时跳过，`validate` 0 issues


## 关联本体节点
```
ontology:domain/skill-to-tickets
ontology:domain/skill-triage
ontology:concept/pdca-task
```

## 风险与对策
- 风险：research豁免被误拦。对策：`ontology_exempt=true`任务豁免
