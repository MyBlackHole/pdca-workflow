# P1 加固：flow-do 三路径本体化与 journal 硬门禁

## 验收标准

- [ ] AC-1 `flow-do.md` 的 design/documentation/review 三路径非空（含 skill 触发与 testable_signal），`ontology-validate OK` `islands:0`
- [ ] AC-2 `pdca_core:act→archive` 对缺 `pdca/journal/YYYY-MM-DD.md` 含 `T{id}` 的任务拒 `JOURNAL_MISSING`，有则放行

## 关联本体节点

```
ontology:process/flow-do
ontology:process/flow-act
```
