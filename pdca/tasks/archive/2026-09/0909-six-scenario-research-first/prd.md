# 分析六场景是否严格先调研后操作

## 背景
用户要求按 PDCA research 路径，判定 development/bugfix/research/documentation/design/review 六场景是否使用严格先调研后操作。Grill 已对齐口径 A：Do 准入有合法 ontology_fragment 即算先调研，复用已有本体即可，不必每次新建 research 票。

## 验收标准

- [ ] AC-1: 六场景前置门禁已逐项核验，每场景给出门禁代码与本体节点
- [ ] AC-2: 每结论附可复核验证途径，可运行命令或 file:line 复核
- [ ] AC-3: research-report.md 已产出并登记为证据，满足图门禁

## 关联本体节点

```
ontology:concept/pdca-gate-do
ontology:concept/pdca-ontology-ready
ontology:concept/pdca-scenario-boundary-rule
ontology:domain/skill-research
ontology:process/flow-do
```

## 拆分映射

- 六场景Do准入门禁核验 -> ontology:concept/pdca-gate-do
- 本体片段合法性核验 -> ontology:concept/pdca-ontology-ready
- research与development边界裁决 -> ontology:concept/pdca-scenario-boundary-rule
- 报告多图与沉淀决策 -> ontology:domain/skill-research
