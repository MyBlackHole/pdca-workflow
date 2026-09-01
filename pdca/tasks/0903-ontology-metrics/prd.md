# 补全量化度量本体：本体健康×过程硬指标×效果 verdict

## 背景

混合方法论与治理原则已硬，但缺 `METHONTOLOGY evaluate` 与 `NeOn empirical` 的量化度量硬指标化，导致“本体提效”无法判定 `improved/neutral/regressed`，T0494严格0%亦无法量收敛。

## 目标

- 新增 `ontology/pattern/ontology-metrics.md` 4度量（本体健康/过程硬指标/追溯度/效果），各 `attributes.testable_signal` 可 `scaffold` 且 `ci-gate` 可输出 `metrics.json`
- 接入 `self-optimization-loop` 效果闭环

## 范围

- 输入：`self-optimization-loop` `ci-ontology-gate` `validate` `graph`
- 输出：1 pattern节点 + `ci-ontology-gate` metrics段 + 全绿
- 不做：不改业务实体

## 功能需求

1. metrics 4度量：health(validate0+islands0+scaffold100%)/hard(fragment100%+disposition100%)/provenance回链率/effectiveness verdict
2. gate：`ci-ontology-gate.py` 输出 `metrics.json` 且 `GATE OK + metrics` 硬拦
3. 可 `scaffold` + `grep` 量化复盘

## 非功能需求

- `islands:0`，`scaffold` 可产

## 验收标准

- [ ] AC-1 度量已沉淀：`ontology-metrics.md` 4度量且 `validate` 通过
- [ ] AC-2 health可测：`validate 0 + islands:0 + scaffold 100%` 可 `ci` 输出
- [ ] AC-3 hard可测：`fragment 100% + disposition 100%` 新任务可 `grep` 命中
- [ ] AC-4 gate度量：`ci-ontology-gate` 输出 `metrics.json` 且 `GATE OK`
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:pattern/ontology-metrics
ontology:concept/self-optimization-loop
ontology:concept/pdca-continuous-improvement
```

## 拆分映射

- 度量本体 -> ontology:pattern/ontology-metrics
