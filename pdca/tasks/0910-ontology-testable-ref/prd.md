# 引用型testable批量产出 ontology:concept/pdca

## 验收标准

- [ ] AC-1: 核心12节点（flow-*×4 + pdca/pdca-task/pdca-evidence/pdca-gate/pdca-transition/pdca-verdict/triage/pdca-phase）引用型testable已写入并可执行通过
- [ ] AC-2: research-report通过门禁
- [ ] AC-3: ontology-validate通过，收敛valid:true证据已登记

## 关联本体节点

```
ontology:concept/pdca
ontology:process/flow-plan
ontology:process/flow-do
ontology:process/flow-check
ontology:process/flow-act
```

## 拆分映射

- 引用统计与testable生成 -> ontology:concept/pdca
- 报告与验证 -> ontology:process/flow-do
