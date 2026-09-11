# CI门禁悬空引用修复 ontology:concept/pdca-architecture（T2149）

父任务 T2147 第二票，前置 T2148 已归档。按 T2148 特化方案与目录清理推荐执行。

## 工作内容

- 修复 `scripts/ci-ontology-gate.py` 对缺失脚本 `check-scenario-mismatch.py` 的悬空引用
 （改为 `scenario-boundary-check.py` 或补齐缺失脚本，以最小改动为准）。
- 补建 `ontology/role/` 目录（`_meta.yaml` 声称有但缺失；`decision/` 已由 T2148 补建）。
- 回归测试覆盖上述两项，`ci-ontology-gate` 与 `ontology-validate` 全绿。

## 验收标准

- [ ] AC-1: 悬空引用已修复，`ci-ontology-gate` 相关项通过，有测试证据
- [ ] AC-2: `ontology/role/` 已补建且 `ontology-validate` 通过
- [ ] AC-3: 门禁全绿（`ci-ontology-gate` + `ontology-validate`），证据已登记

## 关联本体节点

```
ontology:concept/pdca-architecture
ontology:process/flow-do
ontology:decision/t2148-bugfix-specialization
```

## 拆分映射

- 门禁修复 -> ontology:concept/pdca-architecture
- role 补建 -> ontology:concept/pdca-task
