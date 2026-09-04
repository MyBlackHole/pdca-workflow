---
schema: pdca.asset/v1
id: ontology:entity/ontology-deep-integration-tree
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-deep-integration-tree/1.0.0
summary: 树形执行与依赖推导（composed_of 树补齐，叶→根 ready-set 调度与可视化）
relations:
  specializes:
    - ontology:concept/domain-entity
---

# 树形执行与依赖推导

叶子实体3：使 WBS 树可执行、可视。

- 补齐领域 `composed_of` 边（父聚合子，部分-整体真实语义），保证 `ontology_tree_split` 能叶→根生成 `dependencies`
- 运行期由 `scripts/compute-frontier.py` 计算 `ready-set/batches`，叶可并行，根等待 YAGNI
- 新增可视化：`scripts/ontology_graph.py --format dot` 导出 WBS 树，或在 PRD 附录渲染树图
