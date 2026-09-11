# PDCA本体落地A场景（T2147）

## 背景

T2135 结构审查已归档确认，`ontology-validate` 通过，flow-*四节点引用存活达标。
流程本体语义无阻断问题，进入 A 场景（`flow-do` 路径A：代码变更）。
首批先出治理结论，再做代码落地与端到端演示。

## 方向

- 现行 `scenario_type` 六值键保持不变，本任务暂记 `development`；“A场景不再区分 bugfix/development”作为治理议题先论证，结论为 Improvement Candidate 或保留区分的理由，不在任务内直接改权威流程。
- 允许附带修本体：结构类错字可附带，语义改动另立项。

## 验收标准

- [ ] AC-1: 治理结论已归档（不再区分的可行性论证 + Improvement Candidate 或保留理由）
- [ ] AC-2: 门禁全绿（`ci-ontology-gate` + `ontology-validate` 通过，有测试证据登记）
- [ ] AC-3: 端到端演示（一条A路径任务走完 plan→archive 并归档）

## 关联本体节点

```
ontology:process/flow-do
ontology:process/flow-plan
ontology:concept/pdca-scenario-boundary-rule
ontology:concept/pdca-task
```

## 拆分映射

- 治理结论 -> research 子票（先行，归档后解锁代码票）
- 门禁修复+回归测试 -> development 子票
- 端到端演示归档 -> development 子票（依赖前两票）
