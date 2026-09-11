# 不再区分论证 ontology:process/flow-do治理结论（T2148）

父任务 T2147 首票：先出治理结论，再做代码落地。

## 论证要点

- 现行 `flow-do` 路径A内 development/bugfix 的差异点：Seam 类型（行为 Seam vs 回归 Seam）、复现前置、门禁分支（`flow_audit.py` 对 bugfix 特殊处理）。
- 合并的可行性：六值键是路由与门禁分支键，多处脚本依赖；合并需同步改门禁、校验器与测试。
- 结论形态二选一：可行的 Improvement Candidate（含改动清单与验证计划），或保留区分的理由结论。

## 验收标准

- [ ] AC-1: research-report 通过门禁（mermaid≥3/Source≥3/http Source≥1/URLs≥2）
- [ ] AC-2: 结论明确二选一（Improvement Candidate 或保留理由），已归档

## 关联本体节点

```
ontology:process/flow-do
ontology:concept/pdca-scenario-boundary-rule
ontology:concept/pdca-task
```

## 拆分映射

- 可行性论证 -> ontology:process/flow-do
- 结论归档 -> ontology:concept/pdca-task
