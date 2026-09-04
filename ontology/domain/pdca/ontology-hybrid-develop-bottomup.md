---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-develop-bottomup
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-hybrid-develop-bottomup/1.0.0
summary: 混合方法论Develop Bottomup：叶→根实现（WBS bottom-up Work Package + NeOn 9场景 + ready-set）
relations:
  specializes:
    - ontology:domain/ai-efficiency
  relates_to:
    - ontology:concept/pdca-task
    - ontology:domain/ai-efficiency-ticket-dag-ready-set
attributes:
  - name: leaf_to_root_dependencies
    desc: 叶 dependencies:[]，根 dependencies:[leaf-slugs]，batches [[叶],[根]]
    constraint: 叶并行根串行，`tree_split` 候选含 `slug_base/ontology_node_type/dependencies` 且 `compute-frontier` `valid:true`
    testable_signal: "运行 python3 scripts/ontology_tree_split.py --ontology-dir ontology --prd <demo-prd> 产 candidates 含 leaf-slugs 且 python3 scripts/compute-frontier.py < dag.json 返回 valid:true"
  - name: work_package_assignable
    desc: 叶任务可分配至1人且可独立验证
    constraint: 1 leaf = 1 testable_signal → 1 scaffold → 1 pytest，且 `disposition` 含 `ontology:`
    testable_signal: "运行 python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-hybrid-develop-bottomup --out /tmp/demo.py 可产且 pytest --collect-only 可命中，且经 validate 通过"
  - name: inheritance_alignment
    desc: 本体边界对齐与继承
    constraint: task_identity自动继承ontology_fragment/node_type，叶任务沿本体边界对齐
    testable_signal: "检查 pdca/tasks/0902-*/task.json 中 leaf 任务 meta.ontology_fragment == 父 fragment 且经 validate 通过"
  - name: evidence_convergence
    desc: 收敛与证据回链
    constraint: 每叶 `meta.convergence → AC → evidence` 由 `validate-convergence valid:true` 校验
    testable_signal: "运行 python3 scripts/validate-convergence.py --task-dir pdca/tasks/<leaf> 返回 valid:true"
---

# Develop Bottomup — 叶→根实现

> 来源 WBS `bottom-up` Work Package + NeOn Scenario + `ready-set` + `task_identity` 继承

- **动作**：叶任务先实现（`task_identity` 自动继承 `fragment/node_type` 沿本体边界对齐），经 `dependencies` 聚合至根；`tree_split` 叶→根生 `candidates`（`slug_base/ontology_node_type/dependencies`），`compute-frontier` 算 `ready-set` 叶并行根串行。
- **Work Package**：叶为可分配单元，1人1验，1 leaf = 1 `testable_signal` → 1 `scaffold` → 1 `pytest --collect-only` 命中，且 `meta.disposition` 含 `ontology:` 硬拦 `archive`。
- **继承与对接**：`to-tickets#3.5` 默认启用 `tree_split`，`ontology-ready` 硬拦缺 `fragment`，`clash-check` 阻断重名，`flow-do→check` 需 `validate-convergence valid:true`。
- **反模式**：叶 `dependencies` 含传递依赖（应仅直接前置）；根未等叶 `ready-set` 完成即宣称完成。
