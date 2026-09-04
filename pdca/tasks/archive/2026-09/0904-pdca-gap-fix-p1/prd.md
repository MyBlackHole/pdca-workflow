# P0 加固：check_confirmation 与 to-tickets 硬门禁

## 验收标准

- [ ] AC-1 `pdca_core:gate_issues:check` 对自写 `check_confirmation`（无 `grilling captured:true`）拒 `CHECK_GRILLING_MISSING`，有 grilling 则放行
- [ ] AC-2 `pdca_core:gate_issues:plan` 对非 research 且 `children=[]` 的 plan 拒 `TICKETS_MISSING`，有 children 或 research 则放行
- [ ] AC-3 `gate_issues` 单元可检（类似 T2028 模拟的 thin/thick 双测）

## 关联本体节点

```
ontology:concept/pdca-task
ontology:process/flow-plan
```
