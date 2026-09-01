---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-develop-bottomup
type: domain
layer: Knowledge
status: active
summary: 混合方法论Develop Bottomup：叶→根实现（WBS bottom-up Work Package + NeOn 9场景 + ready-set）
relations:
  specializes:
    - ontology:domain/ai-efficiency
  relates_to:
    - ontology:concept/pdca-task
    - ontology:domain/ai-efficiency-ticket-dag-ready-set
attributes:
  - name: leaf_to_root_dependencies
    desc: 叶 dependencies:[]，根 dependencies:[leaf-slugs]
    constraint: 叶并行根串行，batches [[叶],[根]]
    testable_signal: "运行 python3 scripts/ontology_tree_split.py --ontology-dir ontology --prd <demo-prd> 产 candidates 含 leaf-slugs 且 compute-frontier 可算 ready-set"
  - name: work_package_assignable
    desc: 叶任务可分配至1人且可独立验证
    constraint: 1 leaf = 1 testable_signal → 1 scaffold → 1 pytest
    testable_signal: "运行 python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-hybrid-develop-bottomup --out /tmp/demo.py 可产且 pytest --collect-only 可命中"
---

# Develop Bottomup — 叶→根实现

> 来源 WBS `bottom-up` Work Package + NeOn Scenario + `ready-set`

- **动作**：叶任务先实现（`task_identity` 自动继承 `fragment/node_type`），经 `dependencies` 聚合至根；`tree_split` 叶→根生 `candidates`，`compute-frontier` 算 `ready-set` 叶并行
- **Work Package**：叶为可分配单元，1人1验，`testable_signal` 三模式各至少1 `scaffold`
